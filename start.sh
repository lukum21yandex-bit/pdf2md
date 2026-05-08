#!/bin/bash
# Start LlamaCloud PDF Parser server

# Set API key from file
export LLAMA_CLOUD_API_KEY=$(cat ~/.openclaw/llama-cloud-api-key.txt 2>/dev/null | grep -v "^#" | grep -v "^LLAMA_CLOUD" | head -1)

# Check if API key exists
if [ -z "$LLAMA_CLOUD_API_KEY" ]; then
    echo "❌ LLAMA_CLOUD_API_KEY not found!"
    echo "Please set your API key in ~/.openclaw/llama-cloud-api-key.txt"
    echo "Get your key from: https://cloud.llamaindex.ai/api-key"
    exit 1
fi

# Navigate to project directory
cd "$(dirname "$0")"

# Start the server
echo "🚀 Starting LlamaCloud PDF Parser..."
echo "📊 Open: http://localhost:8080"
echo "📄 Project directory: $(pwd)"
uvicorn backend:app --host 0.0.0.0 --port 8080 --reload
