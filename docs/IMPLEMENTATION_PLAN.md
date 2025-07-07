# 🚀 Worldbuilding Chat Interface - Implementation Plan

## **📋 Project Overview**

**Repo Name:** `worldbuilding-chat-interface`
**Description:** Simple chat interface for the Vibe Worldbuilding MCP - explore tools, create worlds, build together.

---

## **🛠 Tech Stack**

### **Frontend**
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Vite** for development/build
- **Socket.io Client** for real-time features

### **Backend**
- **FastAPI** (Python) - integrates naturally with existing MCP
- **Socket.io** for real-time chat
- **Uvicorn** ASGI server
- **Direct integration** with vibe-worldbuilding MCP

### **Infrastructure**
- **Frontend:** Vercel deployment
- **Backend:** Railway/Render deployment
- **Storage:** File-based (worlds stored as files)
- **Environment:** Docker for consistent deployment

---

## **📁 Project Structure**

```
worldbuilding-chat-interface/
├── frontend/                 # React chat interface
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   │   ├── ChatInterface.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── ChatInput.tsx
│   │   │   │   └── ToolsList.tsx
│   │   │   ├── WorldExplorer/
│   │   │   │   ├── FileTree.tsx
│   │   │   │   └── FileViewer.tsx
│   │   │   └── Layout/
│   │   │       ├── Header.tsx
│   │   │       └── Sidebar.tsx
│   │   ├── hooks/
│   │   │   ├── useChat.ts
│   │   │   ├── useWorldState.ts
│   │   │   └── useTools.ts
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── websocket.ts
│   │   ├── types/
│   │   │   ├── chat.ts
│   │   │   ├── tools.ts
│   │   │   └── world.ts
│   │   ├── utils/
│   │   │   ├── messageParser.ts
│   │   │   └── fileHelpers.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── index.html
├── backend/                  # FastAPI server
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── chat.py
│   │   │   │   ├── tools.py
│   │   │   │   ├── worlds.py
│   │   │   │   └── files.py
│   │   │   └── websocket.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── mcp_client.py    # Integration with vibe-worldbuilding
│   │   │   └── message_parser.py
│   │   ├── models/
│   │   │   ├── chat.py
│   │   │   ├── tools.py
│   │   │   └── world.py
│   │   ├── services/
│   │   │   ├── world_service.py
│   │   │   ├── tool_service.py
│   │   │   └── file_service.py
│   │   └── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── worlds/                   # Generated world storage
├── docs/
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── DEVELOPMENT.md
├── scripts/
│   ├── setup.sh
│   ├── dev.sh
│   └── deploy.sh
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── .gitignore
├── README.md
├── docker-compose.dev.yml
└── package.json              # Root workspace config
```

---

## **🔧 Implementation Plan**

### **Phase 1: Core Infrastructure (Week 1)**

#### **Day 1-2: Project Setup**
```bash
# 1. Create GitHub repo
gh repo create worldbuilding-chat-interface --public
cd worldbuilding-chat-interface

# 2. Initialize frontend
mkdir frontend && cd frontend
npm create vite@latest . -- --template react-ts
npm install tailwindcss @tailwindcss/typography socket.io-client
npm install @types/node

# 3. Initialize backend  
cd ../backend
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn python-socketio python-multipart
pip install -e ../vibe-worldbuilding-mcp  # Link to existing MCP
```

#### **Day 3-4: Basic Chat Interface**
```typescript
// frontend/src/components/Chat/ChatInterface.tsx
export const ChatInterface = () => {
  const { messages, sendMessage } = useChat();
  const { tools } = useTools();
  
  return (
    <div className="flex h-screen">
      <Sidebar tools={tools} />
      <main className="flex-1 flex flex-col">
        <MessageList messages={messages} />
        <ChatInput onSend={sendMessage} />
      </main>
    </div>
  );
};
```

#### **Day 5-7: Backend Integration**
```python
# backend/app/core/mcp_client.py
import asyncio
from vibe_worldbuilding.tools.world import handle_world_tool

class MCPClient:
    async def execute_tool(self, tool_name: str, params: dict):
        """Execute MCP tool and return formatted response"""
        if tool_name in WORLD_HANDLERS:
            return await handle_world_tool(tool_name, params)
        # ... handle other tool types
```

### **Phase 2: Tool Integration (Week 2)**

#### **Day 8-10: Message Parsing & Tool Dispatch**
```python
# backend/app/core/message_parser.py
class MessageParser:
    def parse_intent(self, message: str) -> ToolRequest:
        """Parse natural language into tool calls"""
        if "create world" in message.lower():
            return ToolRequest(
                tool="instantiate_world",
                params=self.extract_world_params(message)
            )
        # ... more parsing logic
```

#### **Day 11-12: Real-time File Updates**
```typescript
// frontend/src/hooks/useWorldState.ts
export const useWorldState = () => {
  const [worldFiles, setWorldFiles] = useState([]);
  
  useEffect(() => {
    socket.on('world_updated', (files) => {
      setWorldFiles(files);
    });
  }, []);
};
```

#### **Day 13-14: Tool Responses & UI**
```typescript
// frontend/src/components/Chat/MessageList.tsx
const ToolResponse = ({ response }) => (
  <div className="bg-green-50 p-4 rounded">
    <h4>✅ {response.tool} completed</h4>
    <p>{response.summary}</p>
    {response.files_created && (
      <FilesList files={response.files_created} />
    )}
  </div>
);
```

### **Phase 3: User Experience (Week 3)**

#### **Day 15-17: File Explorer**
```typescript
// frontend/src/components/WorldExplorer/FileTree.tsx
export const FileTree = ({ files }) => {
  return (
    <div className="file-tree">
      {files.map(file => (
        <FileNode 
          key={file.path} 
          file={file} 
          onSelect={handleFileSelect}
        />
      ))}
    </div>
  );
};
```

#### **Day 18-19: Tool Suggestions**
```python
# backend/app/services/suggestion_service.py
class SuggestionService:
    def suggest_next_actions(self, world_state: WorldState) -> List[Suggestion]:
        """Suggest logical next steps based on current world state"""
        suggestions = []
        
        if not world_state.has_taxonomies:
            suggestions.append(Suggestion(
                text="Create some taxonomies to organize your world",
                example="generate_taxonomy_guidelines for 'characters'"
            ))
        # ... more suggestion logic
```

#### **Day 20-21: Polish & Documentation**
- Add tool descriptions and examples
- Implement error handling
- Write user documentation
- Add keyboard shortcuts

### **Phase 4: Deployment & Testing (Week 4)**

#### **Day 22-24: Docker & Deployment**
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### **Day 25-26: CI/CD Pipeline**
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: cd frontend && npm ci && npm run build
      - uses: vercel/action@v1
```

#### **Day 27-28: Testing & Launch**
- End-to-end testing
- Performance optimization
- Demo content creation
- Public launch

---

## **🚀 Deployment Strategy**

### **Development**
```bash
# Local development
docker-compose -f docker-compose.dev.yml up
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### **Production**
- **Frontend:** Vercel (automatic deploys from main branch)
- **Backend:** Railway (Python app with MCP integration)
- **Worlds Storage:** Persistent volume or S3-compatible storage

### **Environment Variables**
```bash
# Backend
FAL_KEY=your_fal_api_key
FRONTEND_URL=https://worldbuilding-chat.vercel.app
ALLOWED_ORIGINS=["https://worldbuilding-chat.vercel.app"]

# Frontend  
VITE_API_URL=https://worldbuilding-api.railway.app
VITE_WS_URL=wss://worldbuilding-api.railway.app
```

---

## **📈 Success Metrics**

**MVP Goals:**
- [ ] Chat interface connects to all MCP tools
- [ ] Natural language → tool execution works
- [ ] File explorer shows real-time world updates
- [ ] Can create complete world from "create a fantasy world about X"
- [ ] Deployed and accessible via URL
- [ ] Tool discovery works for new users

**Next Steps:**
- Multi-user collaboration
- World templates/examples
- Export/sharing features
- Advanced file editing
- Community gallery

---

## **🎯 MVP Chat Interface Design**

### **Initial Welcome Message**
```
🌍 Welcome to the Worldbuilding Toolkit!

You have these tools available:

WORLD TOOLS:
• instantiate_world - Create a new world project
• list_world_files - See what's in your world

TAXONOMY TOOLS:  
• generate_taxonomy_guidelines - Get custom guidelines for a taxonomy type
• create_taxonomy_folders - Create organized categories for your world

ENTRY TOOLS:
• create_world_entry - Add detailed entries to your world
• identify_stub_candidates - Find entities that need their own entries
• create_stub_entries - Automatically create placeholder entries

IMAGE TOOLS:
• generate_image_from_markdown_file - Create visuals for your content

SITE TOOLS:
• build_static_site - Generate a navigable website from your world

---

Try saying things like:
"Create a fantasy world about floating islands"
"Use instantiate_world to start a sci-fi project"
"Generate an image for my character entry"

What would you like to build?
```

### **User Experience Flow**
```
User: "Create a world where music controls physics"
Bot: "I'll create a music-based physics world for you!"
     [Calls instantiate_world with parsed parameters]
Bot: "✅ World created! I've set up the foundation in music-physics-world-20250101/
     Files created:
     - overview/world-overview.md
     - Basic folder structure ready
     
     What would you like to add next? You could:
     - Create taxonomies for characters, locations, or magic systems
     - Add detailed entries for specific elements
     - Generate images for your world"

User: "Add some characters"
Bot: "I'll help you create character entries!"
     [Calls create_taxonomy_folders for characters, then create_world_entry]
```

Ready to build! 🚀 