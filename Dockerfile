FROM python:3.11-slim

WORKDIR /app

# Copy application files
COPY . /app

# Expose server port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Start TruthGuard Server
CMD ["python", "server.py"]
