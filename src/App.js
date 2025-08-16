import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Header from './components/Header';
import MessageList from './components/MessageList';
import MessageInput from './components/MessageInput';
import ApiKeyModal from './components/ApiKeyModal';

const PROVIDER_MODELS = {
  openai: [
    { id: 'gpt-4', name: 'GPT-4' },
    { id: 'gpt-4-turbo', name: 'GPT-4 Turbo' },
    { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' }
  ],
  anthropic: [
    { id: 'claude-3-5-sonnet-20241022', name: 'Claude 3.5 Sonnet' },
    { id: 'claude-3-opus-20240229', name: 'Claude 3 Opus' },
    { id: 'claude-3-haiku-20240307', name: 'Claude 3 Haiku' }
  ],
  gemini: [
    { id: 'gemini-pro', name: 'Gemini Pro' },
    { id: 'gemini-pro-vision', name: 'Gemini Pro Vision' }
  ],
  mistral: [
    { id: 'mistral-large-latest', name: 'Mistral Large' },
    { id: 'mistral-medium-latest', name: 'Mistral Medium' },
    { id: 'mistral-small-latest', name: 'Mistral Small' }
  ]
};

function App() {
  const [messages, setMessages] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('openai');
  const [selectedModel, setSelectedModel] = useState('gpt-4');
  const [isLoading, setIsLoading] = useState(false);
  const [showApiModal, setShowApiModal] = useState(false);
  const [apiKeys, setApiKeys] = useState({});

  useEffect(() => {
    // Load saved messages
    const saved = localStorage.getItem('chat-messages');
    if (saved) {
      setMessages(JSON.parse(saved));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('chat-messages', JSON.stringify(messages));
  }, [messages]);

  const sendMessage = async (content) => {
    const userMessage = { role: 'user', content };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setIsLoading(true);

    try {
      const response = await axios.post('/api/chat', {
        provider: selectedProvider,
        model: selectedModel,
        messages: updatedMessages
      });

      const assistantMessage = { role: 'assistant', content: response.data.response };
      setMessages([...updatedMessages, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: error.response?.data?.error || 'An error occurred',
        isError: true
      };
      setMessages([...updatedMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const saveApiKeys = async (keys) => {
    try {
      await axios.post('/api/keys', keys);
      setApiKeys(keys);
      setShowApiModal(false);
    } catch (error) {
      console.error('Error saving API keys:', error);
    }
  };

  const clearChat = () => {
    setMessages([]);
    localStorage.removeItem('chat-messages');
  };

  return (
    <div className="app">
      <Header
        providers={Object.keys(PROVIDER_MODELS)}
        models={PROVIDER_MODELS[selectedProvider]}
        selectedProvider={selectedProvider}
        selectedModel={selectedModel}
        onProviderChange={setSelectedProvider}
        onModelChange={setSelectedModel}
        onApiKeysClick={() => setShowApiModal(true)}
        onClearChat={clearChat}
      />
      
      <main className="main-content">
        <MessageList messages={messages} isLoading={isLoading} />
        <MessageInput onSendMessage={sendMessage} isLoading={isLoading} />
      </main>

      {showApiModal && (
        <ApiKeyModal
          onSave={saveApiKeys}
          onClose={() => setShowApiModal(false)}
        />
      )}
    </div>
  );
}

export default App;