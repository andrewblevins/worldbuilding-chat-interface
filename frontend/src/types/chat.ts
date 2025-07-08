export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: number;
  tool_calls?: ToolCall[];
  files_created?: string[];
  thinking?: string;
  isStreaming?: boolean;
  isThinking?: boolean;
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
}

export interface SendMessageResponse {
  content: string;
  role: string;
  tool_calls?: ToolCall[];
  files_created?: string[];
} 