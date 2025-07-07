#!/bin/bash
# Setup script for Worldbuilding Chat Interface

set -e

echo "🚀 Setting up Worldbuilding Chat Interface..."

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

echo "✅ Prerequisites satisfied"

# Install root dependencies
echo "📦 Installing root dependencies..."
npm install

# Setup frontend
echo "🎨 Setting up frontend..."
if [ ! -d "frontend/node_modules" ]; then
    cd frontend
    npm install
    cd ..
fi

# Setup backend
echo "🔧 Setting up backend..."
if [ ! -d "backend/venv" ]; then
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# Create .env files if they don't exist
echo "⚙️  Creating environment files..."
if [ ! -f "backend/.env" ]; then
    cat > backend/.env << EOF
# Backend Environment Variables
FAL_KEY=your_fal_api_key_here
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=["http://localhost:3000"]
EOF
    echo "📝 Created backend/.env (please update with your FAL API key)"
fi

if [ ! -f "frontend/.env" ]; then
    cat > frontend/.env << EOF
# Frontend Environment Variables
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
EOF
    echo "📝 Created frontend/.env"
fi

echo "✅ Setup complete!"
echo ""
echo "🎉 Next steps:"
echo "1. Update backend/.env with your FAL API key (if you have one)"
echo "2. Run 'npm run dev' to start development servers"
echo "3. Visit http://localhost:3000 to see the interface"
echo ""
echo "📚 See README.md for more information" 