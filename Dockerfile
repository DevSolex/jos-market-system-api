FROM python:3.11-slim

WORKDIR /app

COPY requierment.txt .

RUN pip install -r requierment.txt

COPY . .

EXPOSE 8000

CMD [ "uvicorn", "main:app", "--port", "8000", "--host", "0.0.0.0" ]