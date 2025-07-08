export interface ContentBlock {
  type: 'text' | 'thinking' | 'tool_use' | 'tool_result';
  text?: string;
  thinking?: string;
  id?: string;
  name?: string;
  input?: any;
  tool_use_id?: string;
  content?: string;
  is_error?: boolean;
}

export interface Message {
  id: string;
  content: string | ContentBlock[];
  role: 'user' | 'assistant';
  timestamp: number;
  tool_calls?: ToolCall[];
  files_created?: string[];
  thinking?: string;
  isStreaming?: boolean;
  isThinking?: boolean;
  // Store original content blocks for API
  content_blocks?: ContentBlock[];
}

export interface ToolCall {
  tool: string;
  input: Record<string, any>;
  result?: string;
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

export interface SendMessageRequest {
  content: string;
  stream?: boolean;
  conversation_history?: Array<{
    role: string; 
    content: string | ContentBlock[];
  }>;
}

export interface SendMessageResponse {
  content: string;
  role: string;
  tool_calls?: ToolCall[];
  files_created?: string[];
  content_blocks?: ContentBlock[];
} 