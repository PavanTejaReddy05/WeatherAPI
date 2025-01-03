FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt


EXPOSE 8000

CMD [ "uvicorn", "Task2:app", "--host", "0.0.0.0", "--port", "8000"]