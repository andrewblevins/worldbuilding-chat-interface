# 🧪 Testing Guide: Worldbuilding Chat Interface

## Quick Start Testing

### 1. **Setup & Installation**

```bash
# Navigate to project
cd world-building-chat-interface

# Install backend dependencies
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install frontend dependencies  
cd ../frontend
npm install

# Install vibe-worldbuilding MCP (optional for full functionality)
cd ..
git clone https://github.com/jasnonaz/vibe-worldbuilding-mcp.git
cd vibe-worldbuilding-mcp
pip install -e .
```

### 2. **Start Services (Auto-Reload)**

**🚀 Option 1: One-Command Startup (Recommended)**
```bash
cd world-building-chat-interface
./dev_start.sh
```
This starts both servers with auto-reload enabled. Press `Ctrl+C` to stop both.

**🔧 Option 2: Manual Startup**

**Terminal 1 - Backend (Auto-Reload):**
```bash
cd backend
source venv/bin/activate
python run_dev.py
```

**Terminal 2 - Frontend (Auto-Reload):**
```bash
cd frontend  
npm run dev
```

### 3. **Access the Application**

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. **Auto-Reload Features**

✅ **Frontend**: Changes to React components, CSS, TypeScript files automatically refresh
✅ **Backend**: Changes to Python files automatically restart the server
✅ **Hot Module Replacement**: No page refresh needed for most React changes
✅ **File Watching**: Real-time updates when world files are created/modified

---

## 🎯 Core Feature Testing

### **Chat Interface Testing**

1. **Basic Chat**
   - Type any message → Should get helpful response
   - Try: "Hello" → Should see tool suggestions

2. **Tool Detection**
   - "Create a fantasy world about floating islands"
   - "Add a character entry for a wizard named Gandor"
   - "Generate an image for my castle"
   - "List the files in my world"

3. **Expected Responses**
   - Tool calls should appear in chat
   - Files created should be listed
   - Tool status (pending/completed/error) should show

### **World Creation Testing**

1. **Instantiate World**
   ```
   Create a sci-fi world about space pirates
   ```
   - Should create world directory structure
   - Files should appear in file explorer
   - Success message with file list

2. **Add Entries**
   ```
   Create a character entry for Captain Zara
   ```
   - Should create entry file
   - File explorer should update
   - Entry should be detailed

3. **Generate Images**
   ```
   Generate an image for Captain Zara
   ```
   - Should create image file (if FAL API configured)
   - Image should appear in files

### **File Explorer Testing**

1. **Real-time Updates**
   - Create world → Files should appear immediately
   - Add entries → File tree should expand
   - File count and sizes should update

2. **Navigation**
   - Click folders to expand/collapse
   - See file types with icons
   - Display file sizes

### **WebSocket Testing**

1. **Connection**
   - Open browser dev tools → Network → WS
   - Should see WebSocket connection to `ws://localhost:8000/ws`

2. **Real-time Updates**
   - Create world in chat → File explorer updates
   - Tool execution → Live status updates

---

## 🔧 API Testing

### **Health Endpoints**

```bash
# Backend health
curl http://localhost:8000/health

# MCP tools health  
curl http://localhost:8000/api/v1/tools/health

# Available tools
curl http://localhost:8000/api/v1/tools/list
```

### **Chat API**

```bash
# Send message
curl -X POST http://localhost:8000/api/v1/chat/send \
  -H "Content-Type: application/json" \
  -d '{"content": "Create a fantasy world about dragons", "role": "user"}'
```

### **Tool Execution**

```bash
# Execute tool directly
curl -X POST http://localhost:8000/api/v1/tools/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "instantiate_world", "parameters": {"concept": "Space pirates"}}'
```

---

## 🎮 Demo Scenarios

### **Scenario 1: Complete Worldbuilding Flow**

1. **Create World**
   ```
   Create a fantasy world about floating islands connected by magical bridges
   ```

2. **Add Characters**
   ```
   Create a character entry for Aira, a sky navigator who guides ships between islands
   ```

3. **Add Locations**
   ```
   Create a location entry for Nimbus Port, the main trading hub
   ```

4. **Generate Visuals**
   ```
   Generate an image for Nimbus Port
   ```

5. **Build Website**
   ```
   Build a static site for my world
   ```

### **Scenario 2: Sci-Fi World**

1. **World Creation**
   ```
   Create a sci-fi world where music controls technology and sound is currency
   ```

2. **Technology Entry**
   ```
   Create an entry for Sonic Drives, the engines powered by harmonic frequencies
   ```

3. **Character Entry**
   ```
   Create a character entry for Echo, a sound engineer and black market musician
   ```

4. **Faction Entry**
   ```
   Create an entry for the Silent Collective, rebels who use noise to resist
   ```

---

## 🛠 Troubleshooting

### **Backend Issues**

**Error: "MCP tools not available"**
- Check if vibe-worldbuilding-mcp is installed
- Verify Python path includes the MCP directory
- Backend will work in demo mode without MCP

**Error: "Module not found"**
- Ensure virtual environment is activated
- Install missing dependencies: `pip install -r requirements.txt`

**Port already in use**
- Stop existing processes: `pkill -f uvicorn`
- Or use different port: `python run_dev.py --port 8001`

### **Frontend Issues**

**Error: "Could not read package.json"**
- Ensure you're in the frontend directory
- Run `npm install` first

**CORS errors**
- Check backend is running on port 8000
- Verify CORS settings in backend config

**WebSocket connection failed**
- Check backend WebSocket endpoint is available
- Verify no firewall blocking WebSocket connections

**Auto-reload not working**
- Clear Vite cache: `npm run clean`
- Restart both servers
- Check file permissions in project directory

### **MCP Integration Issues**

**Tools not executing**
- Check backend logs for MCP errors
- Verify vibe-worldbuilding-mcp installation
- Test tool execution via API directly

**No files created**
- Check write permissions in worlds directory
- Verify tool parameters are correct
- Look for error messages in tool responses

---

## 📊 Expected Behavior

### **Successful World Creation**

- ✅ World directory created in `worlds/`
- ✅ Overview file generated
- ✅ Taxonomy folders structure
- ✅ Files appear in explorer
- ✅ WebSocket updates triggered

### **Successful Tool Execution**

- ✅ Tool status shows "completed"
- ✅ Result text describes what was created
- ✅ Files created list shows new files
- ✅ File explorer updates in real-time

### **Error Handling**

- ✅ Tool errors show in chat
- ✅ Invalid requests get helpful responses
- ✅ Network errors handled gracefully
- ✅ Backend stays responsive during errors

---

## 🚀 Performance Testing

### **Load Testing**

```bash
# Multiple simultaneous requests
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/v1/chat/send \
    -H "Content-Type: application/json" \
    -d '{"content": "Create world '$i'", "role": "user"}' &
done
```

### **WebSocket Testing**

- Open multiple browser tabs
- Create worlds in one tab
- Verify updates appear in all tabs
- Check for memory leaks over time

---

## 📝 Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend loads and displays chat interface
- [ ] WebSocket connection established
- [ ] Basic chat responses work
- [ ] Tool detection and execution works
- [ ] World creation generates files
- [ ] File explorer shows real-time updates
- [ ] Error handling works gracefully
- [ ] API endpoints respond correctly
- [ ] Performance is acceptable
- [ ] Auto-reload works for both servers

**Ready to build worlds! 🌍✨** 