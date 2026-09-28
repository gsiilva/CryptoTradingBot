FROM python:3.12-slim

WORKDIR /app

ENV TZ=America/Sao_Paulo

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]