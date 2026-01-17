# Dockerfile for my-coding-agent-v5
# Provides an isolated environment for running the agent safely

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/opt/venv/bin:/home/agent/.local/bin:$PATH"

# Install system dependencies
# Note: build-essential is large (~400MB), install in separate step to reduce memory pressure
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install build tools separately (if needed for Python packages with C extensions)
# Only install if actually needed - most packages don't require compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Create non-root user for security
RUN useradd -m -u 1000 agent && \
    mkdir -p /workspace /output /home/agent/.local /opt/venv && \
    chown -R agent:agent /workspace /output /home/agent /opt/venv

# Set working directory
WORKDIR /workspace

# Copy project files
COPY --chown=agent:agent pyproject.toml uv.lock ./
COPY --chown=agent:agent core/ ./core/
COPY --chown=agent:agent tools/ ./tools/
COPY --chown=agent:agent conversation/ ./conversation/
COPY --chown=agent:agent delegation/ ./delegation/
COPY --chown=agent:agent execution/ ./execution/
COPY --chown=agent:agent interface/ ./interface/
COPY --chown=agent:agent llm/ ./llm/
COPY --chown=agent:agent monitoring/ ./monitoring/
COPY --chown=agent:agent swebench/ ./swebench/
COPY --chown=agent:agent agent.py app.py main.py ./

# Install Python dependencies using uv
# Install to a persistent location in the image (/opt/venv)
# This will be copied to tmpfs at runtime for better performance
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
RUN uv sync --frozen

# Switch to non-root user
USER agent

# Verify installation
RUN python -c "import sys; print(f'Python {sys.version}')" && \
    uv --version

# Set default command
CMD ["python", "agent.py", "--help"]
