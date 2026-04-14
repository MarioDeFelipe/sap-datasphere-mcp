"""
Decode OAuth JWT token to inspect claims and scopes
"""

import asyncio
import os
import base64
import json
from dotenv import load_dotenv
from auth.oauth_handler import OAuthHandler

def decode_jwt_payload(token):
    """Decode JWT payload without verification"""
    try:
        # JWT format: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            return None

        # Decode payload (second part)
        payload = parts[1]
        # Add padding if needed
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding

        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        return {"error": str(e)}

async def main():
    load_dotenv()

    print("=" * 80)
    print("OAuth JWT Token Inspector")
    print("=" * 80)
    print()

    # Get OAuth token
    client_id = os.getenv('DATASPHERE_CLIENT_ID')
    client_secret = os.getenv('DATASPHERE_CLIENT_SECRET')
    token_url = os.getenv('DATASPHERE_TOKEN_URL')

    print("[*] Acquiring OAuth token...")
    oauth_handler = OAuthHandler(
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url
    )

    token = await oauth_handler.get_token()
    print(f"   [OK] Token acquired")
    print()

    # Decode JWT
    print("[JWT Token Analysis]")
    payload = decode_jwt_payload(token.access_token)

    if payload:
        print(json.dumps(payload, indent=2))
        print()

        # Highlight important fields
        print("[Key Claims]")
        print(f"   Issuer (iss): {payload.get('iss', 'N/A')}")
        print(f"   Subject (sub): {payload.get('sub', 'N/A')}")
        print(f"   Client ID (cid/client_id): {payload.get('cid') or payload.get('client_id', 'N/A')}")
        print(f"   Scopes: {payload.get('scope', 'N/A')}")
        print(f"   Audience (aud): {payload.get('aud', 'N/A')}")
        print(f"   Grant Type: {payload.get('grant_type', 'N/A')}")
        print(f"   User ID: {payload.get('user_id') or payload.get('user_name', 'N/A')}")
        print(f"   Zone ID: {payload.get('zid', 'N/A')}")
        print()

if __name__ == "__main__":
    asyncio.run(main())
