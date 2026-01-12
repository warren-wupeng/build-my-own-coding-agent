#!/bin/bash
# V1 - Practical Enhancement Version (100+ lines of code)
# Add conversation loops, safety checks, error handling

SYSTEM_PROMPT='You are a helpful assistant that can execute bash commands.

When a user gives you a task, reply with this JSON format:
{"action": "bash", "command": "your command"}

When the task is complete, reply:
{"action": "done", "message": "description of what was completed"}

Only reply with JSON, no other text.'

# Build message array (using jq for proper escaping)
MESSAGES="[]"

execute_with_permission() {
    local COMMAND="$1"

    # Check if command is dangerous
    if echo "$COMMAND" | grep -qE 'rm |sudo |chmod |curl.*\|.*sh'; then
        # Use >&2 to output to stderr, ensuring prompts display immediately
        echo "⚠️  Detected potentially dangerous command: $COMMAND" >&2
        echo "Allow execution? (y/n)" >&2
        read CONFIRM
        if [ "$CONFIRM" != "y" ]; then
            echo "User denied execution"
            return 1
        fi
    fi

    # Execute command and capture output and errors
    eval "$COMMAND" 2>&1
}

run_agent() {
    local USER_MSG="$1"

    # Check API key
    if [ -z "$OPENROUTER_API_KEY" ]; then
        echo "❌ Error: OPENROUTER_API_KEY environment variable not set"
        echo "Please run: export OPENROUTER_API_KEY=\"your-key-here\""
        exit 1
    fi

    # Use jq to add initial user message
    MESSAGES=$(echo "$MESSAGES" | jq --arg msg "$USER_MSG" '. + [{"role": "user", "content": $msg}]')

    echo "🚀 Starting AI assistant, beginning task processing..."
    echo "📝 Task: $USER_MSG"
    echo ""

    local STEP_COUNT=1

    while true; do
        echo "🔄 Step $STEP_COUNT..."

        # Use jq to build request body
        REQUEST_BODY=$(jq -n \
            --arg model "deepseek/deepseek-v3.2" \
            --arg system "$SYSTEM_PROMPT" \
            --argjson messages "$MESSAGES" \
            '{"model": $model, "max_tokens": 1024, "messages": ([{"role": "system", "content": $system}] + $messages)}')

        # Call OpenRouter API with timeout and error handling
        RESPONSE=$(curl -s --connect-timeout 10 --max-time 30 \
          https://openrouter.ai/api/v1/chat/completions \
          -H "Authorization: Bearer $OPENROUTER_API_KEY" \
          -H "Content-Type: application/json" \
          -d "$REQUEST_BODY")

        # Check if curl succeeded
        if [ $? -ne 0 ]; then
            echo "❌ Network request failed, please check network connection"
            break
        fi

        # Extract AI reply
        AI_TEXT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content // empty')

        # Check API response
        if [ -z "$AI_TEXT" ]; then
            echo "❌ API response error: $RESPONSE"
            break
        fi

        # Fix format issues in AI reply
        AI_TEXT=$(echo "$AI_TEXT" | sed 's/"(action)"/"action"/g')

        # Add assistant message to history
        MESSAGES=$(echo "$MESSAGES" | jq --arg msg "$AI_TEXT" '. + [{"role": "assistant", "content": $msg}]')

        # Parse action from JSON response
        ACTION=$(echo "$AI_TEXT" | jq -r '.action // empty' 2>/dev/null)

        if [ -z "$ACTION" ]; then
            echo "❌ Cannot parse AI response: $AI_TEXT"
            break
        elif [ "$ACTION" = "done" ]; then
            MESSAGE=$(echo "$AI_TEXT" | jq -r '.message // "Task completed"')
            echo "✅ $MESSAGE"
            echo ""
            echo "🎉 Task successfully completed! Total steps executed: $STEP_COUNT."
            break
        elif [ "$ACTION" = "bash" ]; then
            COMMAND=$(echo "$AI_TEXT" | jq -r '.command // empty')

            if [ -z "$COMMAND" ]; then
                echo "❌ Command is empty"
                break
            fi

            echo "🔧 Preparing to execute: $COMMAND"

            # Use safe execution function
            OUTPUT=$(execute_with_permission "$COMMAND")
            EXEC_RESULT=$?

            if [ $EXEC_RESULT -eq 0 ]; then
                echo "📤 Output:"
                echo "$OUTPUT"
            else
                echo "❌ Command execution failed (exit code: $EXEC_RESULT)"
                echo "$OUTPUT"
            fi

            echo ""

            # Provide feedback to AI
            FEEDBACK="Command '$COMMAND' execution result:\nExit code: $EXEC_RESULT\nOutput: $OUTPUT"
            MESSAGES=$(echo "$MESSAGES" | jq --arg msg "$FEEDBACK" '. + [{"role": "user", "content": $msg}]')

            # Prevent infinite loops
            STEP_COUNT=$((STEP_COUNT + 1))
            if [ $STEP_COUNT -gt 20 ]; then
                echo "⚠️  Executed 20 steps, stopping to prevent infinite loops"
                break
            fi
        else
            echo "❌ Unknown action: $ACTION"
            break
        fi
    done
}

# Main function
main() {
    if [ -z "$1" ]; then
        echo "Usage: $0 \"your task description\""
        echo "Example: $0 \"create a Python project structure\""
        exit 1
    fi

    run_agent "$1"
}

main "$@"