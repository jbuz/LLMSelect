import React from 'react';
import MessageList from '../components/MessageList';
import MessageInput from '../components/MessageInput';
import { useChat } from '../contexts/ChatContext';
import { useApp } from '../contexts/AppContext';
import { useAuth } from '../contexts/AuthContext';
import { useStreamingChat } from '../hooks/useStreamingChat';
import { useModels } from '../hooks/useModels';
import { useConversations } from '../hooks/useConversations';

const ChatMode = () => {
  const { messages, addMessage, conversationId, setConversationId, setActiveConversationId } = useChat();
  const { selectedProvider, selectedModel } = useApp();
  const { user } = useAuth();
  const { models, loading: modelsLoading } = useModels();
  const { fetchConversations } = useConversations();
  
  const {
    streamMessage,
    currentMessage,
    isStreaming,
    error: streamError,
    conversationId: streamConversationId,
    cancelStream
  } = useStreamingChat();

  // When streaming completes, add the message to the list and refresh conversations
  React.useEffect(() => {
    if (!isStreaming && currentMessage && streamConversationId) {
      addMessage({
        role: 'assistant',
        content: currentMessage
      });
      setConversationId(streamConversationId);
      setActiveConversationId(streamConversationId);
      // Refresh conversations list to show updated conversation
      fetchConversations();
    }
  }, [isStreaming, currentMessage, streamConversationId, addMessage, setConversationId, setActiveConversationId, fetchConversations]);

  const sendMessage = async (content) => {
    const userMessage = { role: 'user', content };
    addMessage(userMessage);

    await streamMessage({
      conversationId,
      message: content,
      provider: selectedProvider,
      model: selectedModel
    });
  };

  return (
    <>
      {streamError && <div className="global-error">{streamError}</div>}
      <MessageList 
        messages={messages} 
        isStreaming={isStreaming}
        currentMessage={currentMessage}
      />
      <MessageInput 
        onSendMessage={sendMessage} 
        isLoading={isStreaming || !user || modelsLoading}
        onCancel={cancelStream}
      />
    </>
  );
};

export default ChatMode;
