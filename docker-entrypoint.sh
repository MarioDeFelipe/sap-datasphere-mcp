#!/bin/sh
# Authenticate the SAP Datasphere CLI with client_credentials (headless)
# so tools that shell out to `datasphere objects ...` work in the container.
# Falls through to the command regardless — Python server still serves
# tools that do not depend on the CLI.
set -e

if [ -n "$DATASPHERE_CLIENT_ID" ] \
   && [ -n "$DATASPHERE_CLIENT_SECRET" ] \
   && [ -n "$DATASPHERE_BASE_URL" ] \
   && [ -n "$DATASPHERE_TOKEN_URL" ]; then
  echo "[entrypoint] Authenticating datasphere CLI (client_credentials)..."
  if datasphere login \
       -d client_credentials \
       -F \
       -H "$DATASPHERE_BASE_URL" \
       -T "$DATASPHERE_TOKEN_URL" \
       -c "$DATASPHERE_CLIENT_ID" \
       -C "$DATASPHERE_CLIENT_SECRET"; then
    echo "[entrypoint] datasphere CLI login OK."
  else
    echo "[entrypoint] WARNING: datasphere CLI login failed — CLI-dependent tools will error at runtime."
  fi
else
  echo "[entrypoint] DATASPHERE_* env vars not all set — skipping CLI login. CLI-dependent tools will be unavailable."
fi

exec "$@"
