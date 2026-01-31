#!/bin/bash
# Development mode: Run Flask backend and Astro dev server concurrently

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting development servers...${NC}\n"

# Get the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    kill $FLASK_PID $ASTRO_PID 2>/dev/null || true
    exit
}

trap cleanup SIGINT SIGTERM

# Start Flask backend server
echo -e "${GREEN}Starting Flask backend server on http://localhost:5000${NC}"
cd "$BACKEND_DIR"
uv run python run_server.py &
FLASK_PID=$!

# Wait a moment for Flask to start
sleep 2

# Start Astro dev server
echo -e "${GREEN}Starting Astro dev server on http://localhost:4321${NC}"
cd "$PROJECT_ROOT"
bun run dev &
ASTRO_PID=$!

echo -e "\n${BLUE}Both servers are running!${NC}"
echo -e "${GREEN}Flask API:${NC} http://localhost:5000"
echo -e "${GREEN}Astro Frontend:${NC} http://localhost:4321"
echo -e "\n${YELLOW}Press Ctrl+C to stop both servers${NC}\n"

# Wait for both processes
wait

