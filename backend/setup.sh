#!/bin/bash

echo "🚀 Setting up SBC Document Processor..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

echo "✅ Python and Node.js are installed"

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r ../requirements.txt

echo "✅ Backend setup complete"

# Frontend setup
echo "📦 Setting up frontend..."
cd ../frontend

# Install Node.js dependencies
npm install

echo "✅ Frontend setup complete"

# Create .env files if they don't exist
cd ../backend
if [ ! -f .env ]; then
    echo "📝 Creating backend .env file..."
    cp ../env.example .env
    echo "⚠️  Please update backend/.env with your actual configuration"
fi

cd ../frontend
if [ ! -f .env ]; then
    echo "📝 Creating frontend .env file..."
    cp ../env.example .env
    echo "⚠️  Please update frontend/.env with your actual configuration"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update backend/.env with your database and AWS credentials"
echo "2. Update frontend/.env with your API URL"
echo "3. Start the backend: cd backend && source venv/bin/activate && python app.py"
echo "4. Start the frontend: cd frontend && npm start"
echo ""
echo "For detailed instructions, see README.md"
