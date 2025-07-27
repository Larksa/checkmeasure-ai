#!/bin/bash

echo "🚀 Starting CheckMeasureAI Development Servers"
echo "=============================================="

# Function to kill background processes on script exit
cleanup() {
    echo ""
    echo "🛑 Stopping development servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Set up cleanup on script termination
trap cleanup SIGINT SIGTERM EXIT

# Start backend
echo ""
echo "🐍 Starting Backend (Port 8000)..."
cd backend
python3 main.py &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend started successfully"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend
echo ""
echo "⚛️  Starting Frontend (Port 3000)..."
cd ../frontend
npm start &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "🌐 Application URLs:"
echo "- Frontend: http://localhost:3000"
echo "- Backend:  http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Tips:"
echo "- Press Ctrl+C to stop both servers"
echo "- Backend logs will appear below"
echo "- Frontend will open in your browser automatically"
echo ""
echo "📝 Development servers running..."
echo "=================================="

# Wait for processes to finish
wait $BACKEND_PID $FRONTEND_PID