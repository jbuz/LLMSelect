# Flask Backend (app.py)
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv, find_dotenv, set_key

load_dotenv()

app = Flask(__name__)
CORS(app)

# Function to get API keys from environment variables
def get_api_keys_from_env():
    return {
        "openai": os.environ.get("OPENAI_API_KEY"),
        "anthropic": os.environ.get("ANTHROPIC_API_KEY"),
        "gemini": os.environ.get("GEMINI_API_KEY"),
        "mistral": os.environ.get("MISTRAL_API_KEY"),
    }

@app.route('/')
def index():
    return render_template('multi-llm-chat.html')

@app.route('/api/keys', methods=['POST'])
def save_api_keys():
    keys = request.json
    dotenv_path = find_dotenv()
    if not dotenv_path:
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        open(dotenv_path, 'a').close()

    for key, value in keys.items():
        set_key(dotenv_path, f"{key.upper()}_API_KEY", value)
    
    return jsonify({"status": "success"})

@app.route('/api/keys', methods=['GET'])
def get_api_keys():
    api_keys = get_api_keys_from_env()
    return jsonify({key: "***" if value else "" for key, value in api_keys.items()})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    provider = data.get('provider')
    model = data.get('model')
    messages = data.get('messages', [])
    api_keys = get_api_keys_from_env()
    
    if provider not in api_keys or not api_keys[provider]:
        return jsonify({"error": f"API key for {provider} not configured"}), 400
    
    try:
        response = call_llm_api(provider, model, messages, api_keys[provider])
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def compare():
    data = request.json
    providers = data.get('providers', [])
    prompt = data.get('prompt')
    messages = [{'role': 'user', 'content': prompt}]
    api_keys = get_api_keys_from_env()

    responses = {}
    
    def get_response(provider, model):
        try:
            api_key = api_keys.get(provider)
            if not api_key:
                return f"API key for {provider} not configured"
            return call_llm_api(provider, model, messages, api_key)
        except Exception as e:
            return str(e)

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(get_response, p['provider'], p['model']): p['provider'] for p in providers}
        for future in futures:
            provider = futures[future]
            try:
                responses[provider] = future.result()
            except Exception as e:
                responses[provider] = str(e)

    return jsonify(responses)

def call_llm_api(provider, model, messages, api_key):
    if provider == 'openai':
        return call_openai(model, messages, api_key)
    elif provider == 'anthropic':
        return call_anthropic(model, messages, api_key)
    elif provider == 'gemini':
        return call_gemini(model, messages, api_key)
    elif provider == 'mistral':
        return call_mistral(model, messages, api_key)
    else:
        raise Exception(f"Unsupported provider: {provider}")

def call_openai(model, messages, api_key):
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        },
        json={
            'model': model,
            'messages': messages,
            'max_tokens': 1000
        }
    )
    
    if not response.ok:
        raise Exception(f"OpenAI API error: {response.text}")
    
    return response.json()['choices'][0]['message']['content']

def call_anthropic(model, messages, api_key):
    # Filter out system messages for Anthropic format
    system_message = next((m for m in messages if m['role'] == 'system'), None)
    filtered_messages = [m for m in messages if m['role'] != 'system']
    
    payload = {
        'model': model,
        'max_tokens': 1000,
        'messages': filtered_messages
    }
    
    if system_message:
        payload['system'] = system_message['content']
    
    response = requests.post(
        'https://api.anthropic.com/v1/messages',
        headers={
            'x-api-key': api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        },
        json=payload
    )
    
    if not response.ok:
        raise Exception(f"Anthropic API error: {response.text}")
    
    return response.json()['content'][0]['text']

def call_gemini(model, messages, api_key):
    contents = []
    for message in messages:
        if message['role'] != 'system':  # Gemini doesn't use system messages the same way
            contents.append({
                'role': 'model' if message['role'] == 'assistant' else 'user',
                'parts': [{'text': message['content']}]
            })
    
    response = requests.post(
        f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
        headers={'Content-Type': 'application/json'},
        params={'key': api_key},
        json={'contents': contents}
    )
    
    if not response.ok:
        raise Exception(f"Gemini API error: {response.text}")
    
    return response.json()['candidates'][0]['content']['parts'][0]['text']

def call_mistral(model, messages, api_key):
    response = requests.post(
        'https://api.mistral.ai/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        },
        json={
            'model': model,
            'messages': messages,
            'max_tokens': 1000
        }
    )
    
    if not response.ok:
        raise Exception(f"Mistral API error: {response.text}")
    
    return response.json()['choices'][0]['message']['content']

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3044, debug=False)