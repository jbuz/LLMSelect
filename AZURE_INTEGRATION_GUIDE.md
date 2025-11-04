# Azure AI Foundry Integration Guide

This guide walks through enabling Azure AI Foundry integration in LLMSelect to route all provider APIs (OpenAI, Anthropic, Gemini, Mistral) through Azure for centralized billing and governance.

## 🎯 Overview

**What this integration does:**
- Routes all LLM API calls through Azure AI Foundry
- Provides centralized billing under your Azure tenant
- Enables Azure monitoring, logging, and compliance features
- Maintains backward compatibility with direct provider APIs
- Uses OpenAI-compatible API format for all providers

**Architecture:**
```
User Request → LLMSelect → Azure AI Foundry → Provider APIs
                    ↓
              Single Azure Bill
```

## 📋 Prerequisites

Before enabling Azure integration, you need:

1. **Azure Subscription** with appropriate permissions
2. **Azure AI Foundry resource** (AI Services multi-service account)
3. **Model deployments** for each model you want to use
4. **Azure API key** and endpoint URL

See [`AZURE_FOUNDRY_SETUP.md`](./AZURE_FOUNDRY_SETUP.md) for detailed Azure setup instructions.

## 🚀 Quick Start

### Step 1: Configure Environment Variables

Copy the Azure configuration section from `.env.example` to your `.env` file:

```bash
# Enable Azure routing
USE_AZURE_FOUNDRY=true

# Azure endpoint and credentials
AZURE_AI_FOUNDRY_ENDPOINT=https://your-resource.openai.azure.com
AZURE_AI_FOUNDRY_KEY=your-azure-api-key-here
AZURE_AI_FOUNDRY_API_VERSION=2024-02-15-preview

# Deployment name mappings (customize based on your Azure deployments)
AZURE_DEPLOYMENT_GPT4O=gpt-4o-deployment
AZURE_DEPLOYMENT_GPT4O_MINI=gpt-4o-mini-deployment
AZURE_DEPLOYMENT_CLAUDE_35_SONNET=claude-35-sonnet-deployment
# ... add other models as needed
```

### Step 2: Get Your Azure Values

**Find your Azure AI Foundry endpoint:**
```bash
az cognitiveservices account show \
  --name your-resource-name \
  --resource-group your-rg \
  --query "properties.endpoint" -o tsv
```

**Get your Azure API key:**
```bash
az cognitiveservices account keys list \
  --name your-resource-name \
  --resource-group your-rg \
  --query "key1" -o tsv
```

**List your model deployments:**
```bash
az cognitiveservices account deployment list \
  --name your-resource-name \
  --resource-group your-rg \
  --query "[].name" -o table
```

### Step 3: Map Deployment Names

For each model you want to use, create an environment variable mapping:

**Format:**
```
AZURE_DEPLOYMENT_<MODEL_KEY>=your-azure-deployment-name
```

**Example mappings:**

| Model | Environment Variable | Example Value |
|-------|---------------------|---------------|
| `gpt-4o` | `AZURE_DEPLOYMENT_GPT4O` | `gpt-4o-deployment` |
| `gpt-4o-mini` | `AZURE_DEPLOYMENT_GPT4O_MINI` | `gpt-4o-mini-deployment` |
| `claude-3-5-sonnet-20241022` | `AZURE_DEPLOYMENT_CLAUDE_35_SONNET` | `claude-35-sonnet-deployment` |
| `gemini-1.5-pro` | `AZURE_DEPLOYMENT_GEMINI_15_PRO` | `gemini-15-pro-deployment` |
| `mistral-large-latest` | `AZURE_DEPLOYMENT_MISTRAL_LARGE` | `mistral-large-deployment` |

**Model Key Conversion Rules:**
1. Take the model name (e.g., `gpt-4o`)
2. Convert to uppercase: `GPT-4O`
3. Replace dots and dashes with underscores: `GPT_4O`
4. Add prefix: `AZURE_DEPLOYMENT_GPT_4O`

**Note:** The actual model names in LLMSelect are defined in `llmselect/config.py` under `AZURE_DEPLOYMENT_MAPPINGS`. Check this file for the exact keys.

### Step 4: Restart the Application

```bash
# If using Docker
docker-compose restart

# If using Flask directly
# Stop the app (Ctrl+C) and restart
python3 app.py
```

### Step 5: Verify Azure Integration

**Check logs on startup:**
```bash
docker-compose logs -f app
```

You should see Azure configuration loaded (if enabled).

**Test with a simple chat:**
1. Open the app in your browser
2. Select any model (e.g., GPT-4)
3. Send a test message: "Hello, are you responding through Azure?"
4. Check the response comes through successfully

**Verify routing through Azure Monitor:**
```bash
# Check recent API calls in Azure
az monitor activity-log list \
  --resource-group your-rg \
  --resource-type "Microsoft.CognitiveServices/accounts" \
  --max-events 10 \
  --query "[].{Time:eventTimestamp, Operation:operationName.value}" -o table
```

## 🔧 Configuration Details

### Deployment Name Mapping

The deployment name mapping in `llmselect/config.py` looks like this:

```python
AZURE_DEPLOYMENT_MAPPINGS = {
    "gpt-4o": os.getenv("AZURE_DEPLOYMENT_GPT4O", "gpt-4o-deployment"),
    "gpt-4o-mini": os.getenv("AZURE_DEPLOYMENT_GPT4O_MINI", "gpt-4o-mini-deployment"),
    # ... more mappings
}
```

**How it works:**
1. User selects a model in the UI (e.g., "GPT-4")
2. LLMSelect looks up the model name in `AZURE_DEPLOYMENT_MAPPINGS`
3. Gets the Azure deployment name from environment variable
4. Makes API call to Azure with deployment name

**Adding new models:**
1. Deploy the model in Azure AI Foundry portal
2. Add environment variable: `AZURE_DEPLOYMENT_<KEY>=deployment-name`
3. Add mapping to `config.py` (requires code change)
4. Restart app

### API Format

Azure AI Foundry uses OpenAI-compatible format for all providers:

**Endpoint:**
```
POST {endpoint}/openai/deployments/{deployment-name}/chat/completions?api-version={version}
```

**Headers:**
```http
api-key: {azure-api-key}
Content-Type: application/json
```

**Body:**
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello"}
  ],
  "max_tokens": 1000,
  "stream": false
}
```

**Streaming:**
Set `"stream": true` in the body to get SSE streaming responses.

## 🔄 Dual-Mode Support

The integration maintains backward compatibility with direct provider APIs.

**Mode Selection:**
- **Azure Mode:** Set `USE_AZURE_FOUNDRY=true` (routes through Azure)
- **Direct Mode:** Set `USE_AZURE_FOUNDRY=false` or omit (uses direct APIs)

**When to use each mode:**

| Mode | Use When | Benefits |
|------|----------|----------|
| **Azure** | Production, enterprise, demos | Centralized billing, compliance, monitoring |
| **Direct** | Development, testing, personal use | Simpler setup, direct provider access |

**Switching modes:**
1. Change `USE_AZURE_FOUNDRY` in `.env`
2. Restart application
3. No code changes needed

## 🧪 Testing

### Test Checklist

- [ ] Environment variables configured correctly
- [ ] Azure endpoint accessible from app server
- [ ] API key has correct permissions
- [ ] All model deployments exist in Azure
- [ ] Deployment names match environment variables
- [ ] App restarts successfully with Azure enabled
- [ ] Single-model chat works (non-streaming)
- [ ] Single-model chat works (streaming)
- [ ] Comparison mode works with multiple models
- [ ] Error messages are clear when deployment missing
- [ ] Azure Monitor shows API calls
- [ ] Billing appears in Azure Cost Management

### Manual Testing

**Test 1: Single Model Chat (Non-Streaming)**
1. Open app → Select "Single Model Chat"
2. Choose any model (e.g., GPT-4)
3. Enter message: "Tell me a short joke"
4. Wait for complete response
5. ✅ Response should appear normally

**Test 2: Single Model Chat (Streaming)**
1. Same as above, but message should stream token-by-token
2. ✅ Response should appear gradually

**Test 3: Comparison Mode**
1. Select "Comparison Mode"
2. Choose 2-3 models from different providers
3. Enter message: "Explain quantum computing in one sentence"
4. ✅ All models should respond simultaneously
5. ✅ Responses should be side-by-side

**Test 4: Error Handling**
1. Set invalid deployment name: `AZURE_DEPLOYMENT_GPT4O=nonexistent-deployment`
2. Restart app
3. Try to use GPT-4
4. ✅ Should show clear error: "No Azure deployment mapping found for model 'gpt-4o'"

**Test 5: Azure to Direct Mode Switch**
1. Start with Azure enabled and working
2. Change `USE_AZURE_FOUNDRY=false`
3. Restart app
4. ✅ App should work with direct provider APIs
5. ✅ User API keys should still be required

### Automated Testing

Run the test suite to ensure no regressions:

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test
python3 -m pytest tests/test_llm_service.py -v

# Run with coverage
python3 -m pytest tests/ --cov=llmselect --cov-report=html
```

## 📊 Monitoring & Debugging

### Check if Azure Mode is Active

**Method 1: Check environment**
```bash
cat .env | grep USE_AZURE_FOUNDRY
```

**Method 2: Check app logs**
```bash
docker-compose logs app | grep -i azure
```

**Method 3: Check config at runtime**
In Python shell:
```python
from llmselect import create_app
app = create_app()
print(f"Azure enabled: {app.config['USE_AZURE_FOUNDRY']}")
print(f"Azure endpoint: {app.config['AZURE_AI_FOUNDRY_ENDPOINT']}")
```

### Azure Monitor Queries

**View recent API calls:**
```bash
az monitor metrics list \
  --resource /subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{name} \
  --metric "ProcessedPromptTokens" \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-12-31T23:59:59Z \
  --interval PT1H \
  --output table
```

**Check errors:**
```bash
az monitor activity-log list \
  --resource-group your-rg \
  --status Failed \
  --max-events 20 \
  --output table
```

### Common Issues

**Issue: "No Azure deployment mapping found for model"**
- **Cause:** Missing environment variable for model
- **Fix:** Add `AZURE_DEPLOYMENT_<MODEL_KEY>=deployment-name` to `.env`
- **Verify:** Check `llmselect/config.py` for exact key name

**Issue: 401 Unauthorized from Azure**
- **Cause:** Invalid API key or wrong endpoint
- **Fix:** Verify key and endpoint with Azure CLI
- **Test:**
  ```bash
  curl -X POST "{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2024-02-15-preview" \
    -H "api-key: {key}" \
    -H "Content-Type: application/json" \
    -d '{"messages":[{"role":"user","content":"test"}],"max_tokens":10}'
  ```

**Issue: 404 Not Found - Deployment doesn't exist**
- **Cause:** Model not deployed in Azure or wrong deployment name
- **Fix:** Deploy model in Azure AI Foundry portal
- **Verify:**
  ```bash
  az cognitiveservices account deployment list \
    --name your-resource \
    --resource-group your-rg
  ```

**Issue: App still using direct APIs despite USE_AZURE_FOUNDRY=true**
- **Cause:** App not restarted after config change
- **Fix:** Restart the application
- **Verify:** Check logs for Azure configuration on startup

**Issue: Streaming not working through Azure**
- **Cause:** Network/proxy blocking SSE
- **Fix:** Check network configuration, try non-streaming first
- **Verify:** Test with `curl` and `stream=true`

## 💰 Cost Tracking

### Azure Cost Management

**View costs by resource:**
```bash
az consumption usage list \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --output table
```

**Set budget alerts:**
```bash
az consumption budget create \
  --budget-name llmselect-monthly \
  --amount 1000 \
  --time-grain Monthly \
  --category Cost \
  --notifications enabled=true,threshold=80
```

### Cost Comparison

| Billing Method | Pros | Cons |
|----------------|------|------|
| **Azure Unified** | Single invoice, centralized monitoring, enterprise discounts | Requires Azure subscription |
| **Direct Providers** | Simple setup, no Azure needed | Multiple invoices, harder to track |

**Note:** Azure AI Foundry currently has **0% markup** on provider pricing, so costs are the same as direct APIs.

## 🔐 Security Best Practices

1. **Store Azure key securely:**
   - Use Azure Key Vault in production
   - Never commit `.env` file to git
   - Rotate keys regularly

2. **Use Managed Identity:**
   - In Azure environments (App Service, Container Apps)
   - Eliminates need for API keys
   - Better security and key management

3. **Restrict network access:**
   - Use Private Endpoints for Azure resources
   - Restrict firewall to your app's IP
   - Enable Azure WAF for protection

4. **Monitor for anomalies:**
   - Set up Azure Monitor alerts
   - Track usage patterns
   - Alert on unusual activity

## 📚 Additional Resources

- **Detailed Setup:** [`AZURE_FOUNDRY_SETUP.md`](./AZURE_FOUNDRY_SETUP.md)
- **Azure AI Foundry Docs:** https://learn.microsoft.com/azure/ai-services/
- **OpenAI on Azure:** https://learn.microsoft.com/azure/ai-services/openai/
- **Azure Monitor:** https://learn.microsoft.com/azure/azure-monitor/

## 🤝 Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review [`AZURE_FOUNDRY_SETUP.md`](./AZURE_FOUNDRY_SETUP.md)
3. Check application logs: `docker-compose logs app`
4. Verify Azure resources: `az cognitiveservices account show ...`
5. Test Azure endpoint directly with `curl`

## 📝 Summary

**What you've done:**
✅ Added Azure AI Foundry configuration to LLMSelect  
✅ Configured environment variables for Azure routing  
✅ Mapped model names to Azure deployment names  
✅ Tested routing through Azure  
✅ Verified centralized billing in Azure  

**What's next:**
- Consider enabling Managed Identity for production
- Set up Azure Monitor dashboards
- Configure cost alerts and budgets
- Document your deployment names for team
