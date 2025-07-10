import { useState, useCallback } from 'react';
import type { Message, ChatState } from '../types/chat';
import { apiService } from '../services/api';

const INITIAL_STATE: ChatState = {
  messages: [
    {
      id: 'welcome',
      content: `# 🌍 Welcome to the Worldbuilding Toolkit!

You have these tools available:

## **WORLD TOOLS:**
• **instantiate_world** - Create a new world project
• **list_world_files** - See what's in your world

## **TAXONOMY TOOLS:**
• **generate_taxonomy_guidelines** - Get custom guidelines for a taxonomy type
• **create_taxonomy_folders** - Create organized categories for your world

## **ENTRY TOOLS:**
• **create_world_entry** - Add detailed entries to your world
• **identify_stub_candidates** - Find entities that need their own entries
• **create_stub_entries** - Automatically create placeholder entries

## **IMAGE TOOLS:**
• **generate_image_from_markdown_file** - Create visuals for your content

## **SITE TOOLS:**
• **build_static_site** - Generate a navigable website from your world

---

💡 **Try saying things like:**
- "Create a fantasy world about floating islands"
- "Use instantiate_world to start a sci-fi project"
- "Generate an image for my character entry"

What would you like to build?`,
      role: 'assistant',
      timestamp: Date.now(),
    },
  ],
  isLoading: false,
  error: null,
};

export const useChat = () => {
  const [state, setState] = useState<ChatState>(INITIAL_STATE);

  const sendMessage = useCallback(async (content: string, useStreaming: boolean = true) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      role: 'user',
      timestamp: Date.now(),
    };

    // Add user message and get updated conversation history
    let conversationHistory: any[] = [];
    
    setState(prev => {
      const newMessages = [...prev.messages, userMessage];
      
      // Convert messages to conversation history format (exclude welcome message and current user message)
      conversationHistory = newMessages
        .filter(msg => msg.id !== 'welcome') // Exclude welcome message
        .filter(msg => !msg.isStreaming) // Exclude messages that are still streaming
        .slice(0, -1) // Exclude the current user message (will be sent separately)
        .map(msg => ({
          role: msg.role,
          // Use content_blocks if available (for assistant messages with thinking),
          // otherwise use simple content string (for user messages)
          content: msg.content_blocks || (typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content))
        }))
        .filter(msg => {
          // Only include messages with non-empty content
          const content = msg.content;
          if (typeof content === 'string') {
            return content.trim().length > 0;
          }
          if (Array.isArray(content)) {
            return content.length > 0 && content.some(block => 
              block.text && block.text.trim().length > 0
            );
          }
          return false;
        });

      return {
        ...prev,
        messages: newMessages,
        isLoading: true,
        error: null,
      };
    });

    try {

      if (useStreaming) {
        // Handle streaming response
        const assistantMessageId = (Date.now() + 1).toString();
        let streamedContent = '';
        let thinkingContent = '';
        let toolCalls: any[] = [];
        let filesCreated: string[] = [];
        let contentBlocks: any[] = [];

        // Add initial empty assistant message
        setState(prev => ({
          ...prev,
          messages: [...prev.messages, {
            id: assistantMessageId,
            content: '',
            thinking: '',
            role: 'assistant',
            timestamp: Date.now(),
            isStreaming: true,
            isThinking: false,
          }],
        }));

        // Process stream
        for await (const chunk of apiService.sendMessageStream({ 
          content, 
          conversation_history: conversationHistory 
        })) {
          if (chunk.type === 'thinking') {
            thinkingContent += chunk.content + ' ';
            
            // Update the thinking message
            setState(prev => ({
              ...prev,
              messages: prev.messages.map(msg =>
                msg.id === assistantMessageId
                  ? { ...msg, thinking: thinkingContent.trim(), isThinking: true }
                  : msg
              ),
            }));
          } else if (chunk.type === 'content') {
            streamedContent += chunk.content + ' ';
            
            // Switch from thinking to content and update the streaming message
            setState(prev => ({
              ...prev,
              messages: prev.messages.map(msg =>
                msg.id === assistantMessageId
                  ? { ...msg, content: streamedContent.trim(), isThinking: false }
                  : msg
              ),
            }));
          } else if (chunk.type === 'tools') {
            toolCalls = chunk.tool_calls || [];
            filesCreated = chunk.files_created || [];
            contentBlocks = chunk.content_blocks || [];
          } else if (chunk.type === 'error') {
            throw new Error(chunk.error);
          } else if (chunk.type === 'end') {
            // Finalize the message
            setState(prev => ({
              ...prev,
              messages: prev.messages.map(msg =>
                msg.id === assistantMessageId
                  ? { 
                      ...msg, 
                      isStreaming: false,
                      isThinking: false,
                      tool_calls: toolCalls,
                      files_created: filesCreated,
                      content_blocks: contentBlocks,
                    }
                  : msg
              ),
              isLoading: false,
            }));
            break;
          }
        }
      } else {
        // Handle regular response
        const response = await apiService.sendMessage({ 
          content, 
          conversation_history: conversationHistory 
        });
        
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: response.content,
          role: 'assistant',
          timestamp: Date.now(),
          tool_calls: response.tool_calls,
          files_created: response.files_created,
          content_blocks: response.content_blocks,
        };

        setState(prev => ({
          ...prev,
          messages: [...prev.messages, assistantMessage],
          isLoading: false,
        }));
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'An error occurred',
      }));
    }
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    sendMessage,
    clearError,
  };
}; 