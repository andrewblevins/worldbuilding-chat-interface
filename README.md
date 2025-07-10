# 🌍 Worldbuilding Chat Interface

> **Simple chat interface for the Vibe Worldbuilding MCP** - explore tools, create worlds, build together.

A web-based chat interface that makes the powerful [Vibe Worldbuilding MCP](https://github.com/jasnonaz/vibe-worldbuilding-mcp) accessible to everyone. Create detailed fictional worlds through natural conversation, with automatic organization, AI-generated images, and navigable websites.

## 🚀 Features

- **💬 Natural Language Interface** - Just chat to build worlds
- **🛠️ Tool Discovery** - All MCP tools available through conversation
- **📁 Real-time File Explorer** - See your world structure update live
- **🎨 AI-Generated Images** - Visual representations of your world elements
- **🌐 Instant Websites** - Generate navigable sites from your content
- **👥 Collaborative Building** - Work together on worlds in real-time

## 🎯 MVP Design

Simple chat interface that shows available tools and lets you interact with them naturally:

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

## 🛠️ Tech Stack

- **Frontend**: React 18 + TypeScript + Tailwind CSS + Vite
- **Backend**: FastAPI + Socket.io + Direct MCP integration
- **Deployment**: Vercel (frontend) + Railway (backend)
- **Real-time**: WebSocket updates for live collaboration

## 📁 Project Structure

```
worldbuilding-chat-interface/
├── frontend/          # React chat interface
├── backend/           # FastAPI server with MCP integration
├── worlds/            # Generated world storage
├── docs/              # Documentation
├── scripts/           # Development scripts
└── .github/           # CI/CD workflows
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- [Vibe Worldbuilding MCP](https://github.com/jasnonaz/vibe-worldbuilding-mcp)

### One-Command Setup & Start

```bash
# From the parent directory containing both repos
./start-chat.sh
```

That's it! The script will:
- ✅ Install all dependencies (first run only)
- ✅ Create Python virtual environment
- ✅ Set up environment files
- ✅ Start both frontend and backend servers
- ✅ Show you the URLs to access everything

### Manual Setup (Alternative)

```bash
# Clone the repository
git clone https://github.com/yourusername/worldbuilding-chat-interface.git
cd worldbuilding-chat-interface

# Install dependencies
npm install                    # Root workspace
cd frontend && npm install     # Frontend
cd ../backend && pip install -r requirements.txt  # Backend

# Start development servers
npm run dev                    # Starts both frontend and backend
```

### Environment Variables

```bash
# Backend (.env)
FAL_KEY=your_fal_api_key_here
FRONTEND_URL=http://localhost:3000

# Frontend (.env)
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## 📝 Usage Examples

### Creating a New World
```
You: "Create a fantasy world about floating islands"
Bot: "I'll create a floating islands world for you!"
     [Calls instantiate_world with parsed parameters]
Bot: "✅ World created! I've set up the foundation in floating-islands-world-20250101/
     Files created:
     - overview/world-overview.md
     - Basic folder structure ready
     
     What would you like to add next?"
```

### Adding World Elements
```
You: "Add some characters who live on the islands"
Bot: "I'll help you create character entries!"
     [Calls create_taxonomy_folders for characters, then create_world_entry]
Bot: "✅ Character taxonomy created! 
     ✅ Added 'Sky Dwellers' character entry
     
     Want to add more characters or explore other aspects of your world?"
```

## 🚧 Development Status

This is an MVP implementation focused on core functionality:

- [x] Project setup and planning
- [ ] Basic chat interface
- [ ] MCP tool integration
- [ ] Message parsing and tool dispatch
- [ ] Real-time file updates
- [ ] File explorer UI
- [ ] Tool suggestions
- [ ] Deployment and CI/CD

See [IMPLEMENTATION_PLAN.md](./docs/IMPLEMENTATION_PLAN.md) for detailed development roadmap.

## 🤝 Contributing

This project is in early development. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📖 Documentation

- [📋 Implementation Plan](./docs/IMPLEMENTATION_PLAN.md) - Detailed development roadmap
- [🔧 API Documentation](./docs/API.md) - Backend API reference
- [🚀 Deployment Guide](./docs/DEPLOYMENT.md) - Production deployment
- [💻 Development Guide](./docs/DEVELOPMENT.md) - Local development setup

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Related Projects

- [Vibe Worldbuilding MCP](https://github.com/jasnonaz/vibe-worldbuilding-mcp) - The underlying MCP server
- [Model Context Protocol](https://github.com/modelcontextprotocol/typescript-sdk) - MCP specification and SDKs

---

**Made with ❤️ for worldbuilders everywhere** 