import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message } from '../../types/chat';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

const MessageBubble: React.FC<{ message: Message }> = ({ message }) => {
  const isUser = message.role === 'user';
  const isStreaming = message.isStreaming;
  const isThinking = message.isThinking;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      <div className={`max-w-4xl ${isUser ? 'ml-16' : 'mr-16'}`}>
        {/* Avatar */}
        <div className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
            isUser 
              ? 'bg-blue-500 text-white' 
              : 'bg-gray-200 text-gray-700'
          }`}>
            {isUser ? '👤' : '🤖'}
          </div>
          
          <div className="flex-1 min-w-0 space-y-2">
            {/* Thinking content */}
            {!isUser && (message.thinking || isThinking) && (
              <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-amber-600">🧠</span>
                  <span className="text-sm font-medium text-amber-800">Thinking...</span>
                </div>
                {message.thinking && (
                  <div className="text-sm text-amber-700 leading-relaxed whitespace-pre-wrap">
                    {message.thinking}
                    {isThinking && (
                      <span className="inline-block w-2 h-4 bg-amber-500 animate-pulse ml-1" />
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Main message content */}
            {(message.content || !isThinking) && (
              <div
                className={`rounded-2xl px-4 py-3 ${
                  isUser
                    ? 'bg-blue-500 text-white'
                    : 'bg-white border border-gray-200 text-gray-900 shadow-sm'
                }`}
              >
              {isUser ? (
                <div className="text-[15px] leading-relaxed whitespace-pre-wrap">
                  {message.content}
                </div>
              ) : (
                <div className={`prose prose-sm max-w-none ${
                  isUser ? 'prose-invert' : 'prose-gray'
                }`}>
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      // Custom styling for markdown elements
                      h1: ({children}) => <h1 className="text-xl font-semibold mb-3 text-gray-900">{children}</h1>,
                      h2: ({children}) => <h2 className="text-lg font-semibold mb-2 text-gray-800">{children}</h2>,
                      h3: ({children}) => <h3 className="text-base font-semibold mb-2 text-gray-800">{children}</h3>,
                      p: ({children}) => <p className="mb-2 last:mb-0 text-[15px] leading-relaxed text-gray-700">{children}</p>,
                      ul: ({children}) => <ul className="mb-2 space-y-1">{children}</ul>,
                      ol: ({children}) => <ol className="mb-2 space-y-1">{children}</ol>,
                      li: ({children}) => <li className="text-[15px] text-gray-700">{children}</li>,
                      code: ({children, ...props}) => {
                        const isInline = !props.className;
                        return isInline ? (
                          <code className="bg-gray-100 text-red-600 px-1 py-0.5 rounded text-sm font-mono">
                            {children}
                          </code>
                        ) : (
                          <code className="block bg-gray-50 p-3 rounded-lg text-sm font-mono overflow-x-auto">
                            {children}
                          </code>
                        );
                      },
                      pre: ({children}) => <div className="bg-gray-50 rounded-lg overflow-hidden mb-2">{children}</div>,
                      strong: ({children}) => <strong className="font-semibold text-gray-900">{children}</strong>,
                      em: ({children}) => <em className="italic text-gray-700">{children}</em>,
                      blockquote: ({children}) => (
                        <blockquote className="border-l-4 border-blue-200 pl-4 py-2 bg-blue-50 text-gray-700 rounded-r">
                          {children}
                        </blockquote>
                      ),
                      hr: () => <hr className="border-gray-200 my-4" />,
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                  
                  {/* Streaming cursor */}
                  {isStreaming && (
                    <span className="inline-block w-2 h-4 bg-blue-500 animate-pulse ml-1" />
                  )}
                </div>
              )}
              
              {/* Tool calls indicator */}
              {message.tool_calls && message.tool_calls.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <span className="text-blue-500">🔧</span>
                    <span className="font-medium">Tools used:</span>
                    <span className="text-blue-600">
                      {message.tool_calls.map(tc => tc.tool).join(', ')}
                    </span>
                  </div>
                </div>
              )}
              
              {/* Files created indicator */}
              {message.files_created && message.files_created.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-100">
                  <div className="flex items-start gap-2 text-sm text-gray-600">
                    <span className="text-green-500 mt-0.5">📁</span>
                    <div>
                      <div className="font-medium mb-1">
                        {message.files_created.length} file{message.files_created.length > 1 ? 's' : ''} created:
                      </div>
                      <div className="space-y-1">
                        {message.files_created.slice(0, 3).map((file, index) => (
                          <div key={index} className="text-xs text-gray-500 font-mono bg-gray-50 px-2 py-1 rounded">
                            {file}
                          </div>
                        ))}
                        {message.files_created.length > 3 && (
                          <div className="text-xs text-gray-400">
                            ... and {message.files_created.length - 3} more
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
              </div>
            )}
            
            {/* Timestamp */}
            <div className={`text-xs text-gray-400 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
              {new Date(message.timestamp).toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const LoadingMessage: React.FC = () => (
  <div className="flex justify-start mb-6">
    <div className="max-w-4xl mr-16">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 text-gray-700 flex items-center justify-center text-sm">
          🤖
        </div>
        <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
            <span className="text-sm text-gray-500">Thinking...</span>
          </div>
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
    <div className="flex-1 overflow-y-auto bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-6">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
        {isLoading && <LoadingMessage />}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}; 