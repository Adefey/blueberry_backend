FROM python:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["uvicorn", "--app-dir", ".", "--host", "0.0.0.0", "--port", "8192", "routers.main:router"]