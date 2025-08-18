# README.md content
# MultiChat - Multi-LLM Chat Interface

A beautiful, modern chat interface that supports multiple AI providers including OpenAI, Anthropic, Google Gemini, and Mistral AI.

## Features

- 🎨 **Modern Dark Theme** - Stylish UI with gradient accents and smooth animations
- 🤖 **Multiple AI Providers** - Support for OpenAI, Anthropic, Gemini, and Mistral
- 🔐 **Secure API Key Management** - Store and manage your API keys securely
- 💬 **Real-time Chat** - Responsive chat interface with typing indicators
- 📱 **Mobile Responsive** - Works perfectly on desktop and mobile devices
- 🐳 **Docker Ready** - Easy deployment with Docker and docker-compose
- ⚡ **Fast & Lightweight** - Built with React and Flask for optimal performance

## Quick Start with Docker

1. Clone the repository:
```bash
git clone <your-repo-url>
cd multichat
```

2. Build and run with Docker Compose:
```bash
docker-compose up --build
```

3. Open your browser to `http://localhost:3044`

4. Configure your API keys and start chatting!

## Manual Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Build the React frontend:
```bash
npm run build
```

4. Run the Flask application:
```bash
python app.py
```

## API Keys Setup

1. Click the "API Keys" button in the header
2. Enter your API keys for the providers you want to use:
   - **OpenAI**: Get from https://platform.openai.com/api-keys
   - **Anthropic**: Get from https://console.anthropic.com/
   - **Google Gemini**: Get from https://makersuite.google.com/app/apikey
   - **Mistral AI**: Get from https://console.mistral.ai/

## Supported Models

### OpenAI
- GPT-4
- GPT-4 Turbo
- GPT-3.5 Turbo

### Anthropic
- Claude 3.5 Sonnet
- Claude 3 Opus
- Claude 3 Haiku

### Google Gemini
- Gemini Pro
- Gemini Pro Vision

### Mistral AI
- Mistral Large
- Mistral Medium
- Mistral Small

## Development

### Frontend Development
```bash
npm run dev  # Watch for changes and rebuild
```

### Backend Development
```bash
export FLASK_ENV=development
python app.py
```

## Production Deployment

### Using Docker Compose (Recommended)
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Production Setup
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:3044 app:app
```

## Environment Variables

- `FLASK_ENV`: Set to `production` for production deployment
- `API_KEYS`: JSON string of API keys (optional, can use UI instead)

## Security Notes

- API keys are stored in browser localStorage by default
- For production, consider implementing server-side key storage
- The application includes CORS headers for API access
- All API communications use HTTPS when deployed properly

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please create an issue on GitHub.

---

Built with ❤️ using React, Flask, and Docker