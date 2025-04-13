# Unified PraisonAI Dockerfile with build arguments
FROM python:3.11-slim

# Build arguments
ARG PRAISONAI_EXTRAS="ui,chat,crewai"
ARG DEFAULT_CMD="ui"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    praisonaiagents>=0.0.4 \
    praisonai_tools \
    "praisonai[${PRAISONAI_EXTRAS}]" \
    "embedchain[github,youtube]"

# Copy application code
COPY . .

# Default command
CMD ["praisonai", "${DEFAULT_CMD}"]