#!/bin/bash

echo "======================================"
echo "Group2Coin Setup and Launch Script"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}Error: Please run this script from the Group2Coin root directory${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Step 1: Setting up Backend...${NC}"

# Navigate to backend
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo -e "${GREEN}Backend setup complete!${NC}"

# Start backend in background
echo -e "\n${YELLOW}Starting Backend Server...${NC}"
python main.py &
BACKEND_PID=$!

echo -e "${GREEN}Backend server started (PID: $BACKEND_PID)${NC}"
echo "Backend running on http://localhost:5000"

# Wait for backend to start
sleep 3

# Navigate to frontend
cd ../frontend

echo -e "\n${YELLOW}Step 2: Setting up Frontend...${NC}"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

echo -e "${GREEN}Frontend setup complete!${NC}"

# Start frontend
echo -e "\n${YELLOW}Starting Frontend Server...${NC}"
echo -e "${GREEN}Frontend will open in your browser...${NC}"
npm start

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null
    echo -e "${GREEN}Servers stopped. Goodbye!${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT