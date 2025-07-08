import type { SendMessageRequest, SendMessageResponse } from '../types/chat';
import type { ToolsResponse } from '../types/tools';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface StreamChunk {
  type: 'thinking' | 'content' | 'tools' | 'error' | 'end';
  content?: string;
  is_final?: boolean;
  tool_calls?: any[];
  files_created?: string[];
  content_blocks?: any[];
  error?: string;
}

class ApiService {
  async sendMessage(request: SendMessageRequest): Promise<SendMessageResponse> {
    const response = await fetch(`${API_BASE_URL}/chat/send`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async *sendMessageStream(request: SendMessageRequest): AsyncGenerator<StreamChunk, void, unknown> {
    const response = await fetch(`${API_BASE_URL}/chat/send`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ...request, stream: true }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    if (!response.body) {
      throw new Error('No response body');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              yield data as StreamChunk;
            } catch (e) {
              console.warn('Failed to parse SSE data:', line);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  async getTools(): Promise<ToolsResponse> {
    const response = await fetch(`${API_BASE_URL}/tools/list`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getHealth(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/../health`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}

export const apiService = new ApiService(); 