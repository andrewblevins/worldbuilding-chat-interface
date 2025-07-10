#!/bin/bash
# Simplified startup script for Worldbuilding Chat Interface
# This script handles all setup and startup in one command

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌍 Worldbuilding Chat Interface Launcher${NC}"
echo -e "${BLUE}======================================${NC}\n"

# Function to cleanup background processes
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    jobs -p | xargs -r kill 2>/dev/null || true
    exit 0
}

# Trap cleanup on script exit
trap cleanup EXIT INT TERM

# Change to chat interface directory
cd "$(dirname "$0")/world-building-chat-interface"

# Check if initial setup is needed
if [ ! -d "node_modules" ] || [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}First-time setup detected. Running installation...${NC}"
    
    # Install root dependencies
    echo -e "${GREEN}📦 Installing dependencies...${NC}"
    npm install
    
    # Setup frontend
    if [ ! -d "frontend/node_modules" ]; then
        cd frontend
        npm install
        cd ..
    fi
    
    # Setup backend
    if [ ! -d "backend/venv" ]; then
        cd backend
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        cd ..
    fi
    
    # Create .env files if they don't exist
    if [ ! -f "backend/.env" ]; then
        cat > backend/.env << EOF
# Backend Environment Variables
FAL_KEY=your_fal_api_key_here
FRONTEND_URL=http://localhost:5173
ALLOWED_ORIGINS=["http://localhost:5173"]
EOF
        echo -e "${YELLOW}📝 Created backend/.env (please update with your FAL API key if you have one)${NC}"
    fi
    
    if [ ! -f "frontend/.env" ]; then
        cat > frontend/.env << EOF
# Frontend Environment Variables
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
EOF
        echo -e "${GREEN}📝 Created frontend/.env${NC}"
    fi
fi

# Start backend
echo -e "${GREEN}🔧 Starting backend server...${NC}"
cd backend
source venv/bin/activate
python run_dev.py &
BACKEND_PID=$!

# Give backend time to start
sleep 3

# Start frontend
echo -e "${GREEN}🎨 Starting frontend server...${NC}"
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Give frontend time to start
sleep 3

echo -e "\n${GREEN}✅ Worldbuilding Chat Interface is ready!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}📱 Frontend:${NC} http://localhost:5173"
echo -e "${GREEN}🔧 Backend:${NC} http://localhost:8000"
echo -e "${GREEN}📚 API Docs:${NC} http://localhost:8000/docs"
echo -e "${YELLOW}\nPress Ctrl+C to stop all servers${NC}\n"

# Wait for background processes
wait