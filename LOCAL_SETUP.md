# Local Development Setup Guide

## ✅ Step 1: Environment Variables (COMPLETE)

Your `.env` file has been created with:
- ✅ Secure random SECRET_KEY
- ✅ Secure random JWT_SECRET_KEY  
- ✅ Fernet ENCRYPTION_KEY for API key encryption
- ✅ Development configuration
- ✅ Open registration enabled for easy testing

**Note:** The `.env` file is already in `.gitignore` so your keys are safe!

---

## 🚀 Step 2: Start the Application

### Backend (Flask):

```bash
cd /home/jamesbuzzard/Git/LLMSelect

# Install Python dependencies (if not already done)
pip install -r requirements.txt

# Initialize the database
flask db upgrade  # or: python -m flask db upgrade

# Start the Flask server
python app.py
```

The backend will run on **http://localhost:3044**

### Frontend (React):

Open a new terminal:

```bash
cd /home/jamesbuzzard/Git/LLMSelect

# Install Node dependencies (if not already done)
npm install

# Build the frontend
npm run build

# Or for development with hot reload:
npm run dev
```

---

## 🔑 Step 3: Add Your API Keys

Once the app is running:

1. **Open your browser:** http://localhost:3044

2. **Register/Login:**
   - Click "Register" (since `ALLOW_OPEN_REGISTRATION=true`)
   - Create a username and password
   - Login with your credentials

3. **Add API Keys:**
   - Click the "🔑 API Keys" button in the header
   - Enter your API keys:
     - **OpenAI:** Your OpenAI API key (starts with `sk-...`)
     - **Anthropic:** Your Anthropic API key (starts with `sk-ant-...`)
     - **Google Gemini:** Your Google AI Studio API key
     - **Mistral:** Your Mistral API key
   - Click "Save Keys"

**Security:** Your API keys are encrypted using the `ENCRYPTION_KEY` in your `.env` file before being stored in the database. They are never stored in plain text!

---

## 🎮 Step 4: Demo the Features

### Phase 4 Features (Chat Streaming):

1. **Single Model Chat:**
   - Select a provider (OpenAI, Anthropic, Gemini, or Mistral)
   - Select a model (e.g., GPT-4o, Claude 3.5 Sonnet)
   - Type a message
   - Watch it stream in real-time! ✨
   - Click "Cancel" to stop mid-stream

2. **Comparison Mode:**
   - Switch to "Comparison" mode
   - Select 2-4 models from different providers
   - Ask the same question to all
   - See responses side-by-side with streaming

### Phase 5 Features (Conversation Management) - PR #7 In Progress:

Once PR #7 is merged, you'll also have:

1. **Conversation Sidebar:**
   - View all your past conversations
   - Search conversations
   - Click to load any past conversation

2. **Conversation Management:**
   - Double-click title to rename
   - Context menu (⋮) for actions:
     - Rename conversation
     - Export as markdown
     - Delete conversation
   - New conversation button

3. **Comparison History:**
   - View saved comparisons
   - Load past comparisons
   - Vote on which model was better

---

## 🧪 Testing with All 4 Providers

### Recommended Test Prompts:

**1. Simple Test (verify all work):**
```
Hello! Can you tell me a fun fact about Python programming?
```

**2. Code Generation:**
```
Write a Python function to calculate the Fibonacci sequence recursively.
```

**3. Creative Writing:**
```
Write a short haiku about artificial intelligence.
```

**4. Reasoning:**
```
If I have 5 apples and give away 2, then buy 3 more, how many do I have?
```

**5. Long-form (test streaming):**
```
Explain quantum computing in simple terms, suitable for a beginner.
```

---

## 📊 Testing Conversation Management (After PR #7)

1. **Create multiple conversations:**
   - Chat with OpenAI GPT-4o about Python
   - Chat with Claude about JavaScript  
   - Chat with Gemini about AI
   - Chat with Mistral about web development

2. **Test the sidebar:**
   - See all 4 conversations listed
   - Click each to switch between them
   - Notice they load instantly!

3. **Test search:**
   - Search for "Python" - should find first conversation
   - Search for "web" - should find Mistral conversation

4. **Test rename:**
   - Double-click a conversation title
   - Rename it to "My Python Session"
   - See the change persist

5. **Test export:**
   - Click ⋮ on a conversation
   - Click "Export"
   - Check downloads folder for `.md` file

6. **Test delete:**
   - Click ⋮ on a test conversation
   - Click "Delete"
   - Confirm deletion
   - Verify it's removed from sidebar

---

## 🐛 Troubleshooting

### Database Issues:

```bash
# Reset the database (WARNING: deletes all data)
rm llmselect.db
flask db upgrade
```

### Port Already in Use:

```bash
# Change PORT in .env file
PORT=3045  # or any available port
```

### API Key Errors:

- Make sure your API keys are valid and have credits
- Check the browser console for detailed error messages
- Verify keys are saved (🔑 API Keys modal should show "✓" for each)

### Build Errors:

```bash
# Clean and rebuild
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## 📝 Available Models (37 total)

### OpenAI (12 models):
- GPT-4o, GPT-4o-mini, GPT-4 Turbo
- O1-preview, O1-mini
- GPT-3.5 Turbo

### Anthropic (6 models):
- Claude 3.5 Sonnet/Haiku
- Claude 3 Opus/Sonnet/Haiku

### Google Gemini (10 models):
- Gemini 2.0 Flash (latest!)
- Gemini 1.5 Pro/Flash
- Gemini 1.0 Pro

### Mistral (9 models):
- Mistral Large
- Mistral Medium/Small
- Codestral

---

## 🎉 What to Expect

### Performance:
- **First token:** < 1 second (streaming starts immediately)
- **Full response:** 5-30 seconds depending on length and provider
- **Sidebar load:** < 500ms

### Features Working:
- ✅ Real-time streaming for all 4 providers
- ✅ Cancel mid-stream
- ✅ Message persistence
- ✅ Side-by-side comparison
- ✅ Markdown rendering with syntax highlighting
- ✅ Copy code blocks
- ✅ Conversation history (after PR #7 merges)

---

## 🚀 Next Steps After Testing

1. **Provide Feedback:** Any bugs? Features you want?
2. **Monitor PR #7:** Conversation management UI
3. **Plan Phase 6:** What's next? (Performance optimization? Advanced features?)

---

**Happy testing! 🎮✨**

If you run into any issues, check the Flask console and browser console for error messages.
