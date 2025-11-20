#!/usr/bin/env python3
"""
Script to verify available models from each provider's API.
This queries the actual APIs to determine which models are currently available.
"""

import os
import sys
import json
from typing import List, Dict, Optional
import requests


def query_openai_models(api_key: Optional[str] = None) -> List[str]:
    """Query OpenAI API for available models."""
    if not api_key:
        api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        print("⚠️  No OpenAI API key provided, skipping OpenAI verification")
        return []
    
    try:
        response = requests.get(
            'https://api.openai.com/v1/models',
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        # Filter for chat models only
        models = [m['id'] for m in data.get('data', []) 
                 if 'gpt' in m['id'].lower() or m['id'].startswith('o')]
        
        print(f"✓ Found {len(models)} OpenAI models")
        return sorted(models)
    except Exception as e:
        print(f"✗ Error querying OpenAI: {e}")
        return []


def query_anthropic_models(api_key: Optional[str] = None) -> List[str]:
    """Query Anthropic API for available models."""
    if not api_key:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("⚠️  No Anthropic API key provided, skipping Anthropic verification")
        return []
    
    # Anthropic doesn't have a models endpoint, we'll verify by testing known models
    known_models = [
        'claude-sonnet-4-5-20250929',
        'claude-haiku-4-5-20251001',
        'claude-opus-4-1-20250805',
        'claude-3-5-sonnet-20241022',
        'claude-3-opus-20240229',
        'claude-3-haiku-20240307',
    ]
    
    available = []
    for model in known_models:
        try:
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01',
                    'content-type': 'application/json'
                },
                json={
                    'model': model,
                    'max_tokens': 1,
                    'messages': [{'role': 'user', 'content': 'test'}]
                },
                timeout=10
            )
            if response.status_code in [200, 429]:  # 429 means rate limited but model exists
                available.append(model)
        except:
            pass
    
    print(f"✓ Found {len(available)} Anthropic models")
    return available


def query_gemini_models(api_key: Optional[str] = None) -> List[str]:
    """Query Google Gemini API for available models."""
    if not api_key:
        api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    
    if not api_key:
        print("⚠️  No Gemini API key provided, skipping Gemini verification")
        return []
    
    try:
        response = requests.get(
            f'https://generativelanguage.googleapis.com/v1beta/models?key={api_key}',
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        # Filter for generateContent models
        models = [m['name'].replace('models/', '') for m in data.get('models', [])
                 if 'generateContent' in m.get('supportedGenerationMethods', [])]
        
        print(f"✓ Found {len(models)} Gemini models")
        return sorted(models)
    except Exception as e:
        print(f"✗ Error querying Gemini: {e}")
        return []


def query_mistral_models(api_key: Optional[str] = None) -> List[str]:
    """Query Mistral API for available models."""
    if not api_key:
        api_key = os.environ.get('MISTRAL_API_KEY')
    
    if not api_key:
        print("⚠️  No Mistral API key provided, skipping Mistral verification")
        return []
    
    try:
        response = requests.get(
            'https://api.mistral.ai/v1/models',
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        models = [m['id'] for m in data.get('data', [])]
        
        print(f"✓ Found {len(models)} Mistral models")
        return sorted(models)
    except Exception as e:
        print(f"✗ Error querying Mistral: {e}")
        return []


def compare_models(static_list: List[Dict], api_list: List[str], provider: str):
    """Compare static model list with API results."""
    static_ids = [m['id'] for m in static_list]
    
    print(f"\n📊 {provider.upper()} Model Comparison:")
    print(f"   Static list: {len(static_ids)} models")
    print(f"   API returned: {len(api_list)} models")
    
    # Models in static list but not in API (possibly deprecated)
    deprecated = [m for m in static_ids if m not in api_list and api_list]
    if deprecated:
        print(f"\n⚠️  Potentially deprecated {provider} models:")
        for model in deprecated:
            print(f"   - {model}")
    
    # Models in API but not in static list (new models)
    new_models = [m for m in api_list if m not in static_ids]
    if new_models:
        print(f"\n✨ New {provider} models available:")
        for model in new_models:
            print(f"   - {model}")
    
    if not deprecated and not new_models and api_list:
        print(f"   ✓ Static list is up to date")


def main():
    print("🔍 Verifying LLM Models Availability\n")
    print("=" * 60)
    
    # Read current static lists
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from llmselect.services.model_registry import (
        OPENAI_MODELS, ANTHROPIC_MODELS, GEMINI_MODELS, MISTRAL_MODELS
    )
    
    # Query APIs
    print("\n🌐 Querying Provider APIs...\n")
    
    openai_models = query_openai_models()
    anthropic_models = query_anthropic_models()
    gemini_models = query_gemini_models()
    mistral_models = query_mistral_models()
    
    # Compare results
    print("\n" + "=" * 60)
    
    if openai_models:
        compare_models(OPENAI_MODELS, openai_models, "OpenAI")
    
    if anthropic_models:
        compare_models(ANTHROPIC_MODELS, anthropic_models, "Anthropic")
    
    if gemini_models:
        compare_models(GEMINI_MODELS, gemini_models, "Gemini")
    
    if mistral_models:
        compare_models(MISTRAL_MODELS, mistral_models, "Mistral")
    
    print("\n" + "=" * 60)
    print("\n💡 To update models, edit: llmselect/services/model_registry.py")


if __name__ == '__main__':
    main()
