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

    // Add user message
    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
      error: null,
    }));

    try {
      if (useStreaming) {
        // Handle streaming response
        const assistantMessageId = (Date.now() + 1).toString();
        let streamedContent = '';
        let toolCalls: any[] = [];
        let filesCreated: string[] = [];

        // Add initial empty assistant message
        setState(prev => ({
          ...prev,
          messages: [...prev.messages, {
            id: assistantMessageId,
            content: '',
            role: 'assistant',
            timestamp: Date.now(),
            isStreaming: true,
          }],
        }));

        // Process stream
        for await (const chunk of apiService.sendMessageStream({ content })) {
          if (chunk.type === 'content') {
            streamedContent += chunk.content + ' ';
            
            // Update the streaming message
            setState(prev => ({
              ...prev,
              messages: prev.messages.map(msg =>
                msg.id === assistantMessageId
                  ? { ...msg, content: streamedContent.trim() }
                  : msg
              ),
            }));
          } else if (chunk.type === 'tools') {
            toolCalls = chunk.tool_calls || [];
            filesCreated = chunk.files_created || [];
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
                      tool_calls: toolCalls,
                      files_created: filesCreated,
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
        const response = await apiService.sendMessage({ content });
        
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: response.content,
          role: 'assistant',
          timestamp: Date.now(),
          tool_calls: response.tool_calls,
          files_created: response.files_created,
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