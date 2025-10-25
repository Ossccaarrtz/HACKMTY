FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg ca-certificates curl && rm -rf /var/lib/apt/lists/*
COPY app/cfo_voice/requirements.txt .
RUN pip install -r requirements.txt
COPY app/cfo_voice /app
ENV AUDIO_DIR=/app/audio
RUN mkdir -p /app/audio
EXPOSE 8000
CMD ["python", "main.py"]
