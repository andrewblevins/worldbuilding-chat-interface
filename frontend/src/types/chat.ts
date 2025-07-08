export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: number;
  tool_calls?: ToolCall[];
  files_created?: string[];
}

export interface ToolCall {
  tool: string;
  params: Record<string, any>;
  result?: any;
  status: 'pending' | 'completed' | 'failed';
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

export interface SendMessageRequest {
  content: string;
}

export interface SendMessageResponse {
  content: string;
  role: 'assistant';
  tool_calls: ToolCall[];
  files_created: string[];
} 