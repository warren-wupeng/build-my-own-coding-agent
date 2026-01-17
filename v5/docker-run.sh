#!/bin/bash
# Docker run script for my-coding-agent-v5
# Provides a safe isolated environment for running the agent

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="my-coding-agent-v5"
CONTAINER_NAME="my-coding-agent-v5-run"
OUTPUT_DIR="./output"
WORKSPACE_DIR="$(pwd)"

# Create output directory if it doesn't exist
mkdir -p "${OUTPUT_DIR}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if OPENROUTER_API_KEY is set
if [ -z "${OPENROUTER_API_KEY}" ]; then
    echo -e "${YELLOW}Warning: OPENROUTER_API_KEY is not set.${NC}"
    echo "Set it with: export OPENROUTER_API_KEY='your-key-here'"
    echo ""
fi

# Build image if it doesn't exist
if ! docker image inspect "${IMAGE_NAME}:latest" > /dev/null 2>&1; then
    echo -e "${GREEN}Building Docker image...${NC}"
    docker build -t "${IMAGE_NAME}:latest" .
fi

# Run container
echo -e "${GREEN}Starting agent in isolated container...${NC}"
echo -e "${YELLOW}Note: Agent can only modify files in ${OUTPUT_DIR}${NC}"
echo ""

# Run with interactive mode if arguments provided, otherwise show help
# Security: workspace is read-only, .venv uses tmpfs, only /output is writable
if [ $# -eq 0 ]; then
    docker run --rm -it \
        --name "${CONTAINER_NAME}" \
        --user agent \
        --read-only \
        --tmpfs /tmp:nosuid,size=2g \
        --tmpfs /agent-workspace:nosuid,size=1g \
        --mount type=bind,source="${OUTPUT_DIR}",target=/output,consistency=cached \
        --mount type=bind,source="${WORKSPACE_DIR}",target=/workspace,readonly \
        --mount type=bind,source="${WORKSPACE_DIR}/cache/repos",target=/cache/repos,readonly \
        -e OPENROUTER_API_KEY="${OPENROUTER_API_KEY}" \
        -e PYTHONUNBUFFERED=1 \
        -e UV_PROJECT_ENVIRONMENT=/opt/venv \
        -e XDG_CACHE_HOME=/tmp/.cache \
        -e XDG_DATA_HOME=/tmp/.local/share \
        -e XDG_CONFIG_HOME=/tmp/.config \
        -e AGENT_WORKSPACE=/agent-workspace \
        --memory="8g" \
        --cpus="4" \
        "${IMAGE_NAME}:latest" \
        bash -c "cd /workspace && python agent.py --help"
else
    docker run --rm -it \
        --name "${CONTAINER_NAME}" \
        --user agent \
        --read-only \
        --tmpfs /tmp:nosuid,size=2g \
        --tmpfs /agent-workspace:nosuid,size=1g \
        --mount type=bind,source="${OUTPUT_DIR}",target=/output,consistency=cached \
        --mount type=bind,source="${WORKSPACE_DIR}",target=/workspace,readonly \
        --mount type=bind,source="${WORKSPACE_DIR}/cache/repos",target=/cache/repos,readonly \
        -e OPENROUTER_API_KEY="${OPENROUTER_API_KEY}" \
        -e PYTHONUNBUFFERED=1 \
        -e UV_PROJECT_ENVIRONMENT=/opt/venv \
        -e XDG_CACHE_HOME=/tmp/.cache \
        -e XDG_DATA_HOME=/tmp/.local/share \
        -e XDG_CONFIG_HOME=/tmp/.config \
        -e AGENT_WORKSPACE=/agent-workspace \
        --memory="8g" \
        --cpus="4" \
        "${IMAGE_NAME}:latest" \
        bash -c "cd /workspace && python agent.py \"$@\""
fi
