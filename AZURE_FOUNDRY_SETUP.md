# Azure AI Foundry Integration Guide

## Overview

This guide explains how to configure LLMSelect to use Azure AI Foundry APIs instead of direct provider APIs. This enables:
- Centralized billing through Azure
- Enterprise governance and compliance
- Unified rate limiting and quotas
- Azure monitoring and logging

## Architecture

```
User Request
    ↓
LLMSelect Backend
    ↓
┌─────────────────────┐
│ Routing Decision    │
├─────────────────────┤
│ Direct API  | Azure │
└─────────────────────┘
         ↓           ↓
    Provider    Azure AI Foundry
                     ↓
                 Providers
```

## Azure AI Foundry Setup

### 1. Create Azure AI Foundry Resource

```bash
# Login to Azure
az login

# Create resource group (if needed)
az group create --name rg-llmselect --location eastus

# Create Azure AI Foundry resource
az cognitiveservices account create \
  --name llmselect-ai-foundry \
  --resource-group rg-llmselect \
  --kind AIServices \
  --sku S0 \
  --location eastus
```

### 2. Deploy Models

In Azure AI Foundry Portal:
1. Go to https://ai.azure.com
2. Navigate to your project
3. Deploy models:
   - `gpt-4` (OpenAI)
   - `claude-3-5-sonnet` (Anthropic)
   - `gemini-1.5-pro` (Google)
   - `mistral-large` (Mistral)

Note your **deployment names** (they may differ from model names).

### 3. Get API Keys and Endpoints

```bash
# Get keys
az cognitiveservices account keys list \
  --name llmselect-ai-foundry \
  --resource-group rg-llmselect

# Get endpoint
az cognitiveservices account show \
  --name llmselect-ai-foundry \
  --resource-group rg-llmselect \
  --query properties.endpoint
```

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Azure AI Foundry Configuration
AZURE_AI_FOUNDRY_ENDPOINT=https://llmselect-ai-foundry.openai.azure.com/
AZURE_AI_FOUNDRY_KEY=your-azure-api-key
AZURE_AI_FOUNDRY_API_VERSION=2024-02-15-preview

# Enable Azure routing (optional, can be per-user)
USE_AZURE_FOUNDRY=true

# Deployment name mappings (Azure deployment name -> provider:model)
AZURE_DEPLOYMENT_GPT4=gpt-4-deployment
AZURE_DEPLOYMENT_CLAUDE=claude-35-sonnet-deployment
AZURE_DEPLOYMENT_GEMINI=gemini-15-pro-deployment
AZURE_DEPLOYMENT_MISTRAL=mistral-large-deployment
```

### Database Configuration

Users can choose their routing preference:
- Store Azure API key in `api_keys` table with provider `azure`
- Add `use_azure_routing` boolean to user preferences

## API Endpoints

### Azure AI Foundry Unified API

All providers use the OpenAI-compatible API format:

```
POST {endpoint}/openai/deployments/{deployment-name}/chat/completions?api-version={version}
```

**Headers:**
```
api-key: {your-azure-key}
Content-Type: application/json
```

**Body:**
```json
{
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "max_tokens": 1000,
  "stream": false
}
```

## Model Mapping

| Provider | Model | Azure Deployment Name |
|----------|-------|----------------------|
| OpenAI | gpt-4 | gpt-4-deployment |
| OpenAI | gpt-4-turbo | gpt-4-turbo-deployment |
| OpenAI | gpt-3.5-turbo | gpt-35-turbo-deployment |
| Anthropic | claude-3-5-sonnet-20241022 | claude-35-sonnet-deployment |
| Anthropic | claude-3-5-sonnet-20240620 | claude-35-sonnet-v1-deployment |
| Google | gemini-1.5-pro | gemini-15-pro-deployment |
| Google | gemini-1.5-flash | gemini-15-flash-deployment |
| Mistral | mistral-large-latest | mistral-large-deployment |

## Usage

### For Users

1. Navigate to Settings → API Keys
2. Toggle "Use Azure AI Foundry"
3. Enter your Azure API key
4. Models will now route through Azure

### For Developers

```python
# Direct API (current)
llm_service.invoke(
    provider="openai",
    model="gpt-4",
    messages=messages,
    api_key=user_api_key
)

# Azure AI Foundry (new)
llm_service.invoke(
    provider="openai",
    model="gpt-4",
    messages=messages,
    api_key=user_azure_key,
    use_azure=True  # Routes through Azure
)
```

## Benefits

### Cost Management
- Single Azure invoice for all LLM usage
- Azure Cost Management and budgets
- Granular cost allocation by tags

### Security
- Private endpoints (no public internet)
- Azure AD authentication
- Managed identities for services
- VNet integration

### Monitoring
- Application Insights integration
- Azure Monitor metrics
- Centralized logging
- Request tracing

### Compliance
- Azure compliance certifications
- Data residency control
- GDPR compliance
- Audit logs

## Troubleshooting

### Common Issues

**Issue:** "Deployment not found"
- **Fix:** Check deployment name in Azure Portal matches configuration

**Issue:** "Rate limit exceeded"
- **Fix:** Increase quota in Azure Portal or implement retry logic

**Issue:** "Authentication failed"
- **Fix:** Verify API key is correct and not expired

**Issue:** "Model not available in region"
- **Fix:** Deploy model to your Azure region or change region

## Migration Path

### Phase 1: Dual Mode (Recommended)
- Support both direct and Azure routing
- Users choose their preference
- Default to direct for backward compatibility

### Phase 2: Azure Default
- New users default to Azure
- Existing users can opt-in

### Phase 3: Azure Only
- Deprecate direct API support
- All traffic through Azure

## Cost Comparison

| Provider | Direct API | Azure AI Foundry |
|----------|-----------|------------------|
| OpenAI GPT-4 | $0.03/$0.06 per 1K | Same |
| Anthropic Claude | $0.015/$0.075 per 1K | Same + 0% markup |
| Google Gemini | $0.0015/$0.005 per 1K | Same + 0% markup |
| Mistral Large | €0.008/€0.024 per 1K | Same + 0% markup |

**Note:** Azure AI Foundry currently has **no markup** on provider pricing!

## Next Steps

1. ✅ Read this guide
2. ⬜ Set up Azure AI Foundry resource
3. ⬜ Deploy required models
4. ⬜ Configure environment variables
5. ⬜ Test with a single model
6. ⬜ Roll out to all models
7. ⬜ Update user documentation

## Resources

- [Azure AI Foundry Docs](https://learn.microsoft.com/en-us/azure/ai-studio/)
- [Model Deployments](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/deploy-models)
- [Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)
- [API Reference](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference)
