# Flask Backend (app.py)
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Store API keys in memory (in production, use a proper database)
api_keys = {}

@app.route('/')
def index():
    return render_template('multi-llm-chat.html')

@app.route('/api/keys', methods=['POST'])
def save_api_keys():
    global api_keys
    api_keys = request.json
    return jsonify({"status": "success"})

@app.route('/api/keys', methods=['GET'])
def get_api_keys():
    # Return keys without actual values for security
    return jsonify({key: "***" if value else "" for key, value in api_keys.items()})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    provider = data.get('provider')
    model = data.get('model')
    messages = data.get('messages', [])
    
    if provider not in api_keys or not api_keys[provider]:
        return jsonify({"error": f"API key for {provider} not configured"}), 400
    
    try:
        response = call_llm_api(provider, model, messages, api_keys[provider])
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    app.run(host='0.0.0.0', port=5000, debug=True)