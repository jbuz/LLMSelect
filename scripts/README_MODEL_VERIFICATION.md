# Model Verification Script

## Overview

The `verify_models.py` script queries each LLM provider's API to verify which models are actually available and compares them against our static model lists.

## Usage

### Basic Usage (No API Keys)

```bash
python scripts/verify_models.py
```

This will skip providers that don't have API keys set.

### With API Keys

Set environment variables for the providers you want to verify:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="..."
export MISTRAL_API_KEY="..."

python scripts/verify_models.py
```

### Docker Container Usage

To run verification from inside the Docker container:

```bash
docker compose exec llm-chat python scripts/verify_models.py
```

## What It Does

1. **Queries Provider APIs**: Fetches the current list of available models from each provider
2. **Compares with Static Lists**: Compares API results with our hardcoded model lists
3. **Identifies Issues**:
   - ⚠️ **Deprecated Models**: Models in our list but not available via API
   - ✨ **New Models**: Models available via API but not in our list

## Output Example

```
🔍 Verifying LLM Models Availability

============================================================

🌐 Querying Provider APIs...

✓ Found 42 OpenAI models
✓ Found 6 Anthropic models
✓ Found 8 Gemini models
✓ Found 3 Mistral models

============================================================

📊 OPENAI Model Comparison:
   Static list: 15 models
   API returned: 42 models

⚠️  Potentially deprecated OpenAI models:
   - gpt-5
   - gpt-5-mini

✨ New OpenAI models available:
   - gpt-4-turbo-2024-11-01
   - gpt-4o-2024-11-15
```

## Dynamic Model Verification (In Application)

The application now supports dynamic model verification. New methods have been added to `ModelRegistryService`:

### `get_models_with_verification(provider, api_key)`

This method queries the provider's API and filters the static model list to only include actually available models.

```python
from llmselect.services.model_registry import ModelRegistryService

registry = ModelRegistryService()

# Get verified OpenAI models
verified_models = registry.get_models_with_verification(
    provider="openai",
    api_key="sk-..."
)
```

### How It Works

1. Queries the provider's API for available models
2. Filters the static model list to only include verified models
3. Caches results for 1 hour
4. Falls back to full static list if API query fails

### Supported Providers

- **OpenAI**: Uses `/v1/models` endpoint
- **Gemini**: Uses Google's models API
- **Mistral**: Uses `/v1/models` endpoint
- **Anthropic**: No API endpoint available, uses static list

## Updating Model Lists

When the verification script shows deprecated or new models:

1. Edit `llmselect/services/model_registry.py`
2. Update the relevant model list (`OPENAI_MODELS`, `ANTHROPIC_MODELS`, etc.)
3. Remove deprecated models
4. Add new models with appropriate metadata (contextWindow, maxTokens)
5. Rebuild the Docker container: `docker compose down && docker compose build && docker compose up -d`

## Automation

Consider running this verification script:
- Weekly via cron job
- As part of CI/CD pipeline
- Before major deployments

## Notes

- **Rate Limits**: The script makes minimal API calls but be aware of rate limits
- **Anthropic**: Anthropic doesn't provide a models list API, so verification uses test requests
- **Costs**: Most model list queries are free, but Anthropic verification may incur minimal costs
- **Caching**: Dynamic verification results are cached for 1 hour to reduce API calls
