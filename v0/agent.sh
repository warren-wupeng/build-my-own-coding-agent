#!/bin/bash
# V0 - Simplest AI Assistant (24 lines of code)
# Demonstrates the most basic AI assistant concept: Ask AI -> Get Suggestion -> Execute Command

PROMPT="$1"

# Check if API key is provided
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ Error: Please set OPENROUTER_API_KEY environment variable"
    echo "export OPENROUTER_API_KEY=\"your-key-here\""
    exit 1
fi

# Ask AI what command to run through OpenRouter
RESPONSE=$(curl -s https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek/deepseek-v3.2",
    "messages": [{"role": "user", "content": "'"$PROMPT"'\n\nOnly reply with bash commands, no markdown, no explanations, no code blocks."}],
    "max_tokens": 1024
  }')

# Extract command from response
COMMAND=$(echo "$RESPONSE" | jq -r '.choices[0].message.content')

echo "🤖 AI suggests executing: $COMMAND"
read -r -p "Confirm to run this command? (y/n) " CONFIRM

if [ "$CONFIRM" = "y" ]; then
    eval "$COMMAND"
else
    echo "Execution cancelled"
fi