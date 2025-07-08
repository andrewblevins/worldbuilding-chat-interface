import React from 'react';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { useChat } from '../../hooks/useChat';

export const ChatInterface: React.FC = () => {
  const { messages, isLoading, error, sendMessage, clearError } = useChat();

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            🌍 Worldbuilding Chat Interface
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Chat with your worldbuilding tools to create amazing worlds
          </p>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <div className="flex items-center justify-between">
            <div className="flex">
              <div className="text-red-700">
                <p className="text-sm font-medium">Error: {error}</p>
              </div>
            </div>
            <button
              onClick={clearError}
              className="text-red-400 hover:text-red-600"
            >
              <span className="sr-only">Dismiss</span>
              <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-h-0">
        <MessageList messages={messages} isLoading={isLoading} />
        <ChatInput 
          onSend={sendMessage} 
          isLoading={isLoading}
          placeholder="Ask me to create a world, generate content, or help with worldbuilding..."
        />
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 px-4 py-2">
        <div className="text-center text-xs text-gray-500">
          💡 Try: "Create a fantasy world about floating islands" or "Generate an image for my character"
        </div>
      </footer>
    </div>
  );
}; 