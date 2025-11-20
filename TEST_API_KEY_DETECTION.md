# API Key Detection - Testing Guide

## Quick Test

To verify the API key detection is working:

### 1. Check Current Status

```bash
docker exec llmselect-llm-chat-1 python3 -c "
import os
print('Environment API Keys:')
print(f'  OPENAI_API_KEY: {\"✅ Set\" if os.getenv(\"OPENAI_API_KEY\") else \"❌ Not set\"}')
print(f'  ANTHROPIC_API_KEY: {\"✅ Set\" if os.getenv(\"ANTHROPIC_API_KEY\") else \"❌ Not set\"}')
print(f'  GEMINI_API_KEY: {\"✅ Set\" if os.getenv(\"GEMINI_API_KEY\") else \"❌ Not set\"}')
print(f'  MISTRAL_API_KEY: {\"✅ Set\" if os.getenv(\"MISTRAL_API_KEY\") else \"❌ Not set\"}')
"
```

### 2. Add a Test Key (Example)

Edit `.env` and add:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

### 3. Restart Container

```bash
docker compose restart
```

### 4. Verify Model Verification

```bash
docker compose exec llm-chat python scripts/verify_models.py
```

You should see:
- ✅ "Found X OpenAI models" (if OPENAI_API_KEY is set)
- ⚠️ "No X API key provided" (for providers without keys)

### 5. Test in the Application

1. Open http://localhost:3044
2. Login or register a user
3. Start a new chat
4. Select a model from a provider that has an environment key configured
5. Send a message

**Expected behavior:**
- If you configured an environment key → Chat should work immediately
- If no environment key and no user key → Error: "API key not configured"
- If user has their own key in database → Uses user's key (highest priority)

## API Key Priority Flow

```
User makes a chat request
    ↓
Check environment variables FIRST
    ↓
┌─────────────────────────────┐
│ Environment key exists?     │
│  YES → Use environment key  │ ← HIGHEST Priority (system-wide)
│  NO  → Continue to fallback │
└─────────────────────────────┘
    ↓
Check Azure AI Foundry config
    ↓
┌─────────────────────────────┐
│ Azure Foundry configured?   │
│  YES → Use Azure routing    │ ← Alternative routing
│  NO  → Continue             │
└─────────────────────────────┘
    ↓
Check user's database for API key
    ↓
┌─────────────────────────────┐
│ User has key in database?   │
│  YES → Use user's key       │ ← LOWEST Priority (fallback only)
│  NO  → Return error         │
└─────────────────────────────┘
```

## Expected Outputs

### Without Environment Keys
```
⚠️  No OpenAI API key provided, skipping OpenAI verification
⚠️  No Anthropic API key provided, skipping Anthropic verification
⚠️  No Gemini API key provided, skipping Gemini verification
⚠️  No Mistral API key provided, skipping Mistral verification
```

### With Environment Keys
```
✓ Found 42 OpenAI models
✓ Verified models cached for 1 hour
⚠️  No Anthropic API key provided, skipping Anthropic verification
...
```

## Troubleshooting

### Keys not being detected after adding to .env

**Solution:** Make sure to restart the container
```bash
docker compose restart
```

### "API key not configured" error in chat

**Possible causes:**
1. No environment key in `.env`
2. No user key configured in database
3. Wrong provider name

**Solution:**
- Add key to `.env` file, OR
- Have user configure their own key via the UI

### Model verification not working

**Check:**
1. Is the API key valid?
2. Does it have proper permissions?
3. Check Docker logs: `docker logs llmselect-llm-chat-1 --tail 50`

## Benefits of This System

✅ **Environment-first approach**
- System administrators control default keys
- All users automatically use system keys
- No per-user configuration needed for team deployments

✅ **Automatic model verification**
- Models are verified against live APIs when keys available
- Falls back to static lists without keys

✅ **Flexible deployment**
- Personal use: Set env keys, everyone uses them
- Team use: Set env keys as default
- Multi-tenant: Leave env keys empty, users provide their own

✅ **User fallback**
- Users can still provide keys if system keys not configured
- User keys only used when no system keys exist
- Prevents user keys from overriding system configuration
