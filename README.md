# LLMSelect

[![CI](https://github.com/jbuz/LLMSelect/actions/workflows/ci.yml/badge.svg)](https://github.com/jbuz/LLMSelect/actions/workflows/ci.yml)
[![Security Scan](https://github.com/jbuz/LLMSelect/actions/workflows/security-scan.yml/badge.svg)](https://github.com/jbuz/LLMSelect/actions/workflows/security-scan.yml)

Secure multi-provider LLM comparison tool built with Flask and React. LLMSelect enables teams to experiment with multiple language model providers in a single interface while keeping API credentials encrypted at rest, enforcing strong authentication, and providing observability for every interaction.

## Highlights
- **Side-by-side model comparison** for 2-4 LLM models simultaneously
- **Per-user encrypted API keys** stored in the database using Fernet encryption with a master key supplied via environment variables.
- **Session-based authentication** powered by JWT cookies with automatic CSRF protection and refresh token rotation.
- **Zero-trust defaults** including strict rate limiting, request sanitisation, structured error responses, and hardened HTTP security headers.
- **Comprehensive logging** with JSON-formatted request/response traces and retry logic for outbound LLM requests.
- **Comparison history persistence** with voting and preference tracking for analysis.
- **Conversation history persistence** stored per user/provider in the database for auditing and retrieval.
- **Versioned REST API** served under `/api/v1` for forward compatibility.
- **Health monitoring** via `/health` for uptime checks and container orchestration probes.

## Quick Start

### 1. Configure Environment
Copy `.env.example` to `.env` and set the required secrets. A Fernet encryption key can be generated with:

```bash
python - <<'PY'
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
PY
```

Update `.env` with the generated value for `ENCRYPTION_KEY` along with your `SECRET_KEY` and `JWT_SECRET_KEY`.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
npm install
```

### 3. Build Frontend Assets

```bash
npm run build
```

### 4. Run the Application

```bash
python app.py
```

The service will start on `http://localhost:3044` by default.

## Environment Variables

| Variable | Required | Description |
| --- | --- | --- |
| `SECRET_KEY` | ✅ | Flask secret key used for session signing and CSRF tokens. |
| `JWT_SECRET_KEY` | ✅ | Signing key for authentication cookies. Use a long, random value. |
| `ENCRYPTION_KEY` | ✅ | 32-byte Fernet key used to encrypt API credentials in the database. |
| `DATABASE_URL` | ❌ | SQLAlchemy database URL. Defaults to `sqlite:///llmselect.db`. |
| `PORT` | ❌ | HTTP port for the Flask server (default `3044`). |
| `CORS_ORIGINS` | ❌ | Comma-separated list of allowed origins for the SPA. |
| `JWT_COOKIE_SECURE` | ❌ | Set to `true` in production to force HTTPS-only cookies. |
| `ACCESS_TOKEN_EXPIRES_MINUTES` | ❌ | Access token lifetime (default `15`). |
| `REFRESH_TOKEN_EXPIRES_DAYS` | ❌ | Refresh token lifetime (default `7`). |
| `ALLOW_OPEN_REGISTRATION` | ❌ | When `true`, any user can self-register. Defaults to `false`. |
| `REGISTRATION_TOKEN` | ❌ | Optional shared secret required during registration when open registration is disabled. |

### Azure AI Foundry Integration (Optional)

LLMSelect can optionally route all provider APIs (OpenAI, Anthropic, Gemini, Mistral) through **Azure AI Foundry** for centralized billing and enterprise governance. See [`AZURE_QUICK_REFERENCE.md`](AZURE_QUICK_REFERENCE.md) for quick setup.

| Variable | Required | Description |
| --- | --- | --- |
| `USE_AZURE_FOUNDRY` | ❌ | Set to `true` to route all API calls through Azure AI Foundry. |
| `AZURE_AI_FOUNDRY_ENDPOINT` | ⚠️ | Your Azure AI Foundry endpoint URL (required if Azure enabled). |
| `AZURE_AI_FOUNDRY_KEY` | ⚠️ | Your Azure API key (required if Azure enabled). |
| `AZURE_AI_FOUNDRY_API_VERSION` | ❌ | Azure API version (default: `2024-02-15-preview`). |
| `AZURE_DEPLOYMENT_*` | ❌ | Model deployment name mappings (see `.env.example` for full list). |

**Benefits of Azure routing:**
- 💰 **Centralized Billing**: Single Azure invoice for all providers
- 🔐 **Enterprise Governance**: Azure Monitor, compliance, and security controls
- 🌐 **Unified API**: OpenAI-compatible interface for all providers
- 📊 **Better Monitoring**: Azure logging, metrics, and cost tracking

**Documentation:**
- 🚀 **Quick Start**: [`AZURE_QUICK_REFERENCE.md`](AZURE_QUICK_REFERENCE.md) - 3-step setup guide
- 📖 **Full Setup**: [`AZURE_FOUNDRY_SETUP.md`](AZURE_FOUNDRY_SETUP.md) - Azure resource creation with CLI
- 🔧 **Integration**: [`AZURE_INTEGRATION_GUIDE.md`](AZURE_INTEGRATION_GUIDE.md) - Configuration and testing
- 💻 **Implementation**: [`AZURE_IMPLEMENTATION_SUMMARY.md`](AZURE_IMPLEMENTATION_SUMMARY.md) - Technical details

**Note:** Azure integration is **completely optional**. LLMSelect works perfectly with direct provider APIs (default behavior).

> ⚠️ API keys for LLM providers are **no longer read from environment variables**. They are securely stored per user inside the database and encrypted with the master key.

## Authentication & API Key Flow
1. Users create an account (subject to the registration policy above) and sign in through the SPA. JWT cookies are issued with CSRF protection enabled.
2. Each user can upload provider credentials via the “API Keys” dialog. Keys are encrypted before touching the database and never returned to the frontend.
3. Chat requests require an authenticated session. Incoming payloads are validated and sanitised before invoking provider APIs.
4. Rate limiting ensures that chat and comparison endpoints cannot be abused (`60 per minute` by default).

## API Surface

| Method | Path | Description |
| --- | --- | --- |
| POST | /api/v1/auth/register | Create a new user (honours registration policy). |
| POST | /api/v1/auth/login | Authenticate a user and mint JWT cookies. |
| POST | /api/v1/auth/logout | Revoke the refresh/access cookies. |
| POST | /api/v1/auth/refresh | Rotate the access token using a refresh cookie. |
| GET | /api/v1/auth/me | Return the authenticated user's profile. |
| POST | /api/v1/keys | Persist provider API keys for the current user. |
| POST | /api/v1/chat | Submit a chat turn and receive a provider response plus `conversationId`. |
| POST | /api/v1/compare | Request side-by-side responses from multiple providers. Returns comparison ID. |
| POST | /api/v1/compare/stream | Stream comparison results in real-time via Server-Sent Events (SSE). |
| GET | /api/v1/comparisons | Retrieve user's comparison history with pagination. |
| POST | /api/v1/comparisons/:id/vote | Vote for preferred model response in a comparison. |
| GET | /health | Lightweight health check for infrastructure probes. |

## Features

### Chat Mode
- Single-model conversational interface
- Support for OpenAI, Anthropic, Google, and Mistral models
- Conversation history persistence
- Model and provider selection
- **Markdown Rendering**: Rich text formatting with syntax highlighting
- **Code Blocks**: Syntax highlighting for 277+ programming languages
- **Copy Buttons**: One-click copying of code blocks

### Comparison Mode
- **Real-Time Streaming**: See all models respond simultaneously with <1s time to first token
- **Multi-Model Selection**: Choose 2-4 models to compare simultaneously
- **Side-by-Side Display**: View responses in a responsive grid layout
- **Performance Metrics**: See response time and token counts for each model
- **Markdown Rendering**: Rich text formatting with GitHub Flavored Markdown support
- **Syntax Highlighting**: Beautiful code blocks with copy buttons
- **Streaming Indicators**: Visual feedback as models generate responses
- **Voting**: Mark your preferred response for future reference
- **History**: Access past comparisons with full results
- **Error Handling**: Graceful degradation when individual providers fail
- **Cancellation**: Stop streaming mid-response if needed

### Message Rendering
- **Markdown Support**: Tables, lists, blockquotes, links, and images
- **GitHub Flavored Markdown**: Task lists, strikethrough, and autolinks
- **Syntax Highlighting**: VS Code Dark Plus theme for code blocks
- **Copy Functionality**: Copy entire messages or individual code blocks
- **Responsive Design**: Mobile-friendly layouts

## Error Handling & Observability
- Requests and responses are logged in structured JSON, making it easy to ship logs to systems such as ELK, Datadog, or CloudWatch.
- All API responses follow a consistent error envelope with `error` and `message` fields and omit sensitive details.
- Automatic retries with exponential backoff protect against transient provider outages. Persistent failures return human-readable errors to the UI.
- React components include error boundaries and global notifications to surface network issues gracefully.

## Health & Maintenance
- Use `GET /health` for liveness checks; the payload includes the current environment and a UTC timestamp.
- Authentication cookies can be rotated without downtime by updating `JWT_SECRET_KEY` (invalidate old sessions) or `ENCRYPTION_KEY` (requires re-encrypting stored keys).
- Logs default to `INFO` level; override via the `LOG_LEVEL` environment variable.

## Development Notes
- The database schema is created automatically on startup. For production, run migrations or manage schema with your preferred tooling before deploying.
- Default rate limits can be tuned via the `API_RATE_LIMIT` environment variable (e.g., `30 per minute` or `100 per hour`).
- The frontend bundles are produced by Webpack and served from the `dist` directory referenced by Flask.

## Security & CI/CD

This project follows security-first development practices:

### Pre-commit Hooks (Required for Contributors)
Install pre-commit hooks to prevent committing secrets locally:
```bash
pip install pre-commit
pre-commit install
```

Hooks will automatically run on every commit to:
- Scan for secrets (Gitleaks, detect-secrets)
- Format code (Black for Python, Prettier for JS)
- Lint code (Flake8)
- Check for common issues

### CI/CD Pipeline
All code changes trigger automated checks:
- **Secret Scanning**: Gitleaks and TruffleHog scan for exposed credentials
- **Security Analysis**: CodeQL analyzes Python and JavaScript for vulnerabilities
- **Dependency Auditing**: Safety (Python) and npm audit check for vulnerable dependencies
- **Linting & Testing**: Code quality checks and test suites
- **Container Scanning**: Trivy scans Docker images for vulnerabilities
- **SBOM Generation**: Software Bill of Materials generated for supply chain security

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed security guidelines and [SECURITY.md](SECURITY.md) for vulnerability reporting.

### Supply Chain Security
- All GitHub Actions are pinned to commit SHAs (not tags)
- Dependencies are scanned for vulnerabilities on every PR
- SBOM published with releases for transparency

## Contributing
1. Fork and clone the repository.
2. Create a feature branch and ensure your changes include appropriate tests or manual verification notes.
3. Open a pull request describing the behaviour change, security considerations, and rollout plan.

## License

MIT License. See `LICENSE` for details.
