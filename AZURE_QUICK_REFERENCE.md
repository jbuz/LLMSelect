# Azure AI Foundry Quick Reference

## 🚀 Quick Setup (3 Steps)

### 1️⃣ Create Azure Resource
```bash
# Login to Azure
az login

# Create resource
az cognitiveservices account create \
  --name llmselect-ai-foundry \
  --kind AIServices \
  --sku S0 \
  --location eastus \
  --resource-group your-rg \
  --yes
```

### 2️⃣ Configure Environment
```bash
# Get endpoint
az cognitiveservices account show \
  --name llmselect-ai-foundry \
  --resource-group your-rg \
  --query "properties.endpoint" -o tsv

# Get API key
az cognitiveservices account keys list \
  --name llmselect-ai-foundry \
  --resource-group your-rg \
  --query "key1" -o tsv

# Add to .env file
USE_AZURE_FOUNDRY=true
AZURE_AI_FOUNDRY_ENDPOINT=<endpoint from above>
AZURE_AI_FOUNDRY_KEY=<key from above>
```

### 3️⃣ Deploy Models & Map Names
```bash
# Deploy models in Azure AI Foundry Portal
# https://ai.azure.com → Your Resource → Deployments → Deploy Model

# Map deployment names in .env
AZURE_DEPLOYMENT_GPT4O=gpt-4o-deployment
AZURE_DEPLOYMENT_CLAUDE_35_SONNET=claude-35-sonnet-deployment
# ... add more as needed

# Restart app
docker-compose restart
```

## 📋 Environment Variables Cheat Sheet

### Required (when USE_AZURE_FOUNDRY=true)
```bash
USE_AZURE_FOUNDRY=true
AZURE_AI_FOUNDRY_ENDPOINT=https://your-resource.openai.azure.com
AZURE_AI_FOUNDRY_KEY=your-azure-api-key-here
```

### Optional
```bash
AZURE_AI_FOUNDRY_API_VERSION=2024-02-15-preview  # Default shown
```

### Deployment Mappings
```bash
# OpenAI Models
AZURE_DEPLOYMENT_GPT4O=gpt-4o-deployment
AZURE_DEPLOYMENT_GPT4O_MINI=gpt-4o-mini-deployment
AZURE_DEPLOYMENT_GPT4_TURBO=gpt-4-turbo-deployment
AZURE_DEPLOYMENT_GPT4=gpt-4-deployment
AZURE_DEPLOYMENT_GPT35_TURBO=gpt-35-turbo-deployment

# Anthropic Models
AZURE_DEPLOYMENT_CLAUDE_35_SONNET=claude-35-sonnet-deployment
AZURE_DEPLOYMENT_CLAUDE_35_HAIKU=claude-35-haiku-deployment
AZURE_DEPLOYMENT_CLAUDE_3_OPUS=claude-3-opus-deployment

# Gemini Models
AZURE_DEPLOYMENT_GEMINI_15_PRO=gemini-15-pro-deployment
AZURE_DEPLOYMENT_GEMINI_15_FLASH=gemini-15-flash-deployment
AZURE_DEPLOYMENT_GEMINI_15_FLASH_8B=gemini-15-flash-8b-deployment

# Mistral Models
AZURE_DEPLOYMENT_MISTRAL_LARGE=mistral-large-deployment
AZURE_DEPLOYMENT_MISTRAL_MEDIUM=mistral-medium-deployment
AZURE_DEPLOYMENT_MISTRAL_SMALL=mistral-small-deployment
```

## 🔍 Testing Commands

### Verify Azure Endpoint
```bash
curl -X POST "${AZURE_AI_FOUNDRY_ENDPOINT}/openai/deployments/gpt-4o-deployment/chat/completions?api-version=2024-02-15-preview" \
  -H "api-key: ${AZURE_AI_FOUNDRY_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 50
  }'
```

### List Deployments
```bash
az cognitiveservices account deployment list \
  --name llmselect-ai-foundry \
  --resource-group your-rg \
  --query "[].{Name:name, Model:properties.model.name}" \
  --output table
```

### Check App Configuration
```bash
# Check if Azure is enabled
cat .env | grep USE_AZURE_FOUNDRY

# View all Azure config
cat .env | grep AZURE_
```

## 🐛 Troubleshooting Quick Fixes

### Error: "No Azure deployment mapping found"
```bash
# Add missing deployment mapping to .env
AZURE_DEPLOYMENT_<MODEL_KEY>=your-deployment-name

# Restart app
docker-compose restart
```

### Error: 401 Unauthorized
```bash
# Verify endpoint and key
echo $AZURE_AI_FOUNDRY_ENDPOINT
echo $AZURE_AI_FOUNDRY_KEY

# Test with curl (see above)
```

### Error: 404 Deployment not found
```bash
# List your deployments
az cognitiveservices account deployment list \
  --name llmselect-ai-foundry \
  --resource-group your-rg

# Fix deployment name in .env or deploy model in portal
```

### App still using direct APIs
```bash
# Verify Azure is enabled
cat .env | grep "USE_AZURE_FOUNDRY=true"

# Restart app
docker-compose restart

# Check logs
docker-compose logs app | grep -i azure
```

## 📊 Monitoring Commands

### View API Usage
```bash
az monitor metrics list \
  --resource /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{name} \
  --metric ProcessedPromptTokens \
  --start-time $(date -u -d '1 hour ago' '+%Y-%m-%dT%H:%M:%SZ') \
  --interval PT5M
```

### View Costs
```bash
az consumption usage list \
  --start-date $(date -u -d '7 days ago' '+%Y-%m-%d') \
  --end-date $(date -u '+%Y-%m-%d') \
  --query "[?contains(instanceName, 'llmselect')].{Date:usageStart, Cost:pretaxCost}" \
  --output table
```

### Check Recent Errors
```bash
az monitor activity-log list \
  --resource-group your-rg \
  --status Failed \
  --max-events 10 \
  --output table
```

## 🔄 Mode Switching

### Enable Azure Mode
```bash
# Edit .env
USE_AZURE_FOUNDRY=true

# Restart
docker-compose restart
```

### Disable Azure Mode (Use Direct APIs)
```bash
# Edit .env
USE_AZURE_FOUNDRY=false

# Restart
docker-compose restart
```

## 📚 Documentation Links

- **Full Setup Guide:** `AZURE_FOUNDRY_SETUP.md`
- **Integration Guide:** `AZURE_INTEGRATION_GUIDE.md`
- **Implementation Details:** `AZURE_IMPLEMENTATION_SUMMARY.md`
- **Azure AI Foundry Docs:** https://learn.microsoft.com/azure/ai-services/

## 🆘 Get Help

### Common Issues
1. **Missing deployment mapping** → Add to `.env` and restart
2. **Invalid API key** → Get new key with `az cognitiveservices account keys list`
3. **Deployment not found** → Deploy model in Azure AI Foundry portal
4. **Still using direct APIs** → Verify `USE_AZURE_FOUNDRY=true` and restart

### Validation Checklist
- [ ] `USE_AZURE_FOUNDRY=true` in `.env`
- [ ] Endpoint URL is correct
- [ ] API key is valid (test with curl)
- [ ] Models are deployed in Azure portal
- [ ] Deployment names match environment variables
- [ ] App restarted after config changes
- [ ] Logs show no Azure-related errors

### Test Sequence
```bash
# 1. Verify config
cat .env | grep AZURE_

# 2. Test Azure endpoint
curl -X POST "${AZURE_AI_FOUNDRY_ENDPOINT}/openai/deployments/<deployment>/chat/completions?api-version=2024-02-15-preview" \
  -H "api-key: ${AZURE_AI_FOUNDRY_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}]}'

# 3. Restart app
docker-compose restart

# 4. Check logs
docker-compose logs -f app

# 5. Test in browser
# Navigate to http://localhost:3044 and send a message
```

---

**Need More Help?** Check the comprehensive guides:
- Setup: `AZURE_FOUNDRY_SETUP.md`
- Integration: `AZURE_INTEGRATION_GUIDE.md`
- Implementation: `AZURE_IMPLEMENTATION_SUMMARY.md`
