FROM python:slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . .

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["uvicorn", "--app-dir", ".", "--host", "0.0.0.0", "--port", "8192", "routers.main:router"]