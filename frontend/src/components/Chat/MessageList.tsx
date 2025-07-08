import React, { useEffect, useRef } from 'react';
import type { Message } from '../../types/chat';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

const MessageBubble: React.FC<{ message: Message }> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-3xl ${isUser ? 'ml-12' : 'mr-12'}`}>
        <div
          className={`p-3 rounded-lg ${
            isUser
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-900'
          }`}
        >
          <div className="whitespace-pre-wrap">{message.content}</div>
          
          {/* Show tool calls if any */}
          {message.tool_calls && message.tool_calls.length > 0 && (
            <div className="mt-2 pt-2 border-t border-gray-200">
              <div className="text-sm opacity-75">
                🛠️ Tool calls: {message.tool_calls.map(tc => tc.tool).join(', ')}
              </div>
            </div>
          )}
          
          {/* Show files created if any */}
          {message.files_created && message.files_created.length > 0 && (
            <div className="mt-2 pt-2 border-t border-gray-200">
              <div className="text-sm opacity-75">
                📄 Files created: {message.files_created.length}
              </div>
              <div className="text-xs mt-1 opacity-60">
                {message.files_created.slice(0, 3).map(file => (
                  <div key={file}>• {file}</div>
                ))}
                {message.files_created.length > 3 && (
                  <div>... and {message.files_created.length - 3} more</div>
                )}
              </div>
            </div>
          )}
        </div>
        
        <div className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};

const LoadingMessage: React.FC = () => (
  <div className="flex justify-start mb-4">
    <div className="max-w-3xl mr-12">
      <div className="p-3 rounded-lg bg-gray-100">
        <div className="flex items-center gap-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
          <span className="text-gray-600">Thinking...</span>
        </div>
      </div>
    </div>
  </div>
);

export const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      
      {isLoading && <LoadingMessage />}
      
      <div ref={messagesEndRef} />
    </div>
  );
}; 