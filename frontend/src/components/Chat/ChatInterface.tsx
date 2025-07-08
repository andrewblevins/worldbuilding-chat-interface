import React from 'react';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { useChat } from '../../hooks/useChat';

export const ChatInterface: React.FC = () => {
  const { messages, isLoading, error, sendMessage, clearError } = useChat();

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <span className="text-2xl">🌍</span>
                Worldbuilding Assistant
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                Chat with Claude to create and manage your worlds using powerful tools
              </p>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <div className="flex items-center gap-1">
                <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                <span>Claude Sonnet 4</span>
              </div>
              <span className="text-gray-300">•</span>
              <div className="flex items-center gap-1">
                <span className="w-2 h-2 bg-blue-400 rounded-full"></span>
                <span>11 MCP Tools</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-b border-red-200">
          <div className="max-w-4xl mx-auto px-4 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span className="text-sm font-medium text-red-800">{error}</span>
              </div>
              <button
                onClick={clearError}
                className="text-red-400 hover:text-red-600 transition-colors"
                aria-label="Dismiss error"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-h-0">
        <MessageList messages={messages} isLoading={isLoading} />
        <ChatInput 
          onSend={sendMessage} 
          isLoading={isLoading}
          placeholder="Describe the world you want to create, or ask me to use any of the 11 worldbuilding tools..."
        />
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-3">
          <div className="flex items-center justify-center text-xs text-gray-500">
            <span className="flex items-center gap-1">
              💡 Try: "Create a sci-fi world" • "Generate an image for my character" • "Build a static site"
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}; 