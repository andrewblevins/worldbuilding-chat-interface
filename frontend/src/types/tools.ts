export interface WorldTool {
  name: string;
  description: string;
  category: 'world' | 'taxonomy' | 'entry' | 'image' | 'site';
  parameters?: Record<string, any>;
}

export interface ToolsResponse {
  tools: {
    world: string[];
    taxonomy: string[];
    entry: string[];
    image: string[];
    site: string[];
  };
}

export interface ToolSuggestion {
  text: string;
  example: string;
  tool: string;
} 