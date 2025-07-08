import React, { useState, useRef, useEffect } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  placeholder?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({ 
  onSend, 
  isLoading, 
  placeholder = "Type your message..." 
}) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white">
      <div className="max-w-4xl mx-auto px-4 py-4">
        <form onSubmit={handleSubmit} className="relative">
          <div className="flex items-end gap-3">
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={placeholder}
                disabled={isLoading}
                rows={1}
                className="w-full px-4 py-3 pr-12 border border-gray-200 rounded-2xl 
                         resize-none outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                         disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed
                         text-[15px] leading-relaxed placeholder-gray-400
                         max-h-[200px] overflow-y-auto"
                style={{ minHeight: '48px' }}
              />
              
              {/* Send button */}
              <button
                type="submit"
                disabled={!message.trim() || isLoading}
                className="absolute right-2 bottom-2 w-8 h-8 flex items-center justify-center
                         rounded-full bg-blue-500 text-white hover:bg-blue-600 
                         disabled:bg-gray-300 disabled:cursor-not-allowed
                         transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <svg 
                    className="w-4 h-4" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path 
                      strokeLinecap="round" 
                      strokeLinejoin="round" 
                      strokeWidth={2} 
                      d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" 
                    />
                  </svg>
                )}
              </button>
            </div>
          </div>
          
          {/* Help text */}
          <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
            <div className="flex items-center gap-4">
              <span>Press Enter to send, Shift+Enter for new line</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1">
                <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                Streaming enabled
              </span>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}; 