FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
COPY app/data_integration/requirements.txt .
RUN pip install -r requirements.txt
COPY app/data_integration /app
EXPOSE 5050
CMD ["python", "main.py"]
