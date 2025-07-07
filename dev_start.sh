#!/bin/bash
# Development startup script for Worldbuilding Chat Interface

set -e

echo "🚀 Starting Worldbuilding Chat Interface in development mode..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to cleanup background processes
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    jobs -p | xargs -r kill
    exit 0
}

# Trap cleanup on script exit
trap cleanup EXIT INT TERM

# Start backend
echo -e "${GREEN}Starting backend server...${NC}"
cd backend
source venv/bin/activate 2>/dev/null || {
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
}

python run_dev.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend
echo -e "${GREEN}Starting frontend server...${NC}"
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 2

echo -e "${GREEN}✅ Both servers started successfully!${NC}"
echo -e "${GREEN}📱 Frontend:${NC} http://localhost:5173"
echo -e "${GREEN}🔧 Backend:${NC} http://localhost:8000"
echo -e "${GREEN}📚 API Docs:${NC} http://localhost:8000/docs"
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"

# Wait for background processes
wait 