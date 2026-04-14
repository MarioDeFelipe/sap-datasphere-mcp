# SAP Datasphere MCP Server

MCP server exposing SAP Datasphere **task-monitoring** tools over Streamable HTTP. Built for remote deployment behind a TLS-terminating proxy so MCP clients (e.g., SAP Studio) can call it over the network.

Fork of [MarioDeFelipe/sap-datasphere-mcp](https://github.com/MarioDeFelipe/sap-datasphere-mcp), trimmed to the task-monitoring surface. Other tools remain in the codebase but are disabled — see `_TASK_MONITORING_TOOLS` in `sap_datasphere_mcp_server.py`.

## Exposed Tools

| Tool | Purpose |
|------|---------|
| `list_task_chains` | List task chains in a space |
| `get_task_status` | Latest status of a specific task chain |
| `get_task_history` | Historical runs of a task chain |
| `get_task_log` | Log output of a specific run |
| `run_task_chain` | Trigger execution of a task chain |

## Cloud Deployment (Streamable HTTP)

```bash
git clone https://github.com/sokolat/sap-datasphere-mcp
cd sap-datasphere-mcp
cp .env.example .env   # fill in values
docker build -t sap-datasphere-mcp .
docker run -d -p 8080:8080 --env-file .env sap-datasphere-mcp
```

### Required env vars

See `.env.example` for the full list.

| Variable | Purpose |
|----------|---------|
| `DATASPHERE_BASE_URL` | Datasphere tenant URL |
| `DATASPHERE_CLIENT_ID` | OAuth client ID (technical user) |
| `DATASPHERE_CLIENT_SECRET` | OAuth client secret |
| `DATASPHERE_TOKEN_URL` | OAuth token endpoint |
| `MCP_API_KEY` | Bearer token required on `/mcp`. Generate: `python -c "import secrets;print(secrets.token_urlsafe(32))"` |
| `SERVER_PORT` | HTTP port (default `8080`) |

### Endpoints

- `GET /health` — healthcheck, no auth, returns `{"status":"ok"}`
- `POST /mcp` — MCP Streamable HTTP, requires header `Authorization: Bearer <MCP_API_KEY>`

### TLS

Server speaks plain HTTP. Terminate TLS at a proxy or load balancer (nginx, Cloudflare, Cloud Run, ECS Fargate, Fly.io).

### Client configuration

```
URL:    https://<your-public-host>/mcp
Header: Authorization: Bearer <MCP_API_KEY>
```

### Validate

```bash
curl https://<host>/health
# {"status":"ok"}

curl -i -X POST https://<host>/mcp
# 401 Unauthorized  (expected without token)

curl -X POST https://<host>/mcp \
  -H "Authorization: Bearer $MCP_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
# Lists the 5 task-monitoring tools
```

## Local Development (stdio)

```bash
pip install -r requirements.txt
cp .env.example .env
python sap_datasphere_mcp_server.py        # stdio mode (for Claude Desktop)
python sap_datasphere_mcp_server.py http   # HTTP mode on 0.0.0.0:8080
```

## License

Apache 2.0. See `LICENSE` and `NOTICE`. Full historical README preserved at `docs/archive/README_full.md`.
