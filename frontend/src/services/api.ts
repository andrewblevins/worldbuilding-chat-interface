import type { SendMessageRequest, SendMessageResponse } from '../types/chat';
import type { ToolsResponse } from '../types/tools';

const API_BASE_URL = 'http://localhost:8000/api/v1';

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