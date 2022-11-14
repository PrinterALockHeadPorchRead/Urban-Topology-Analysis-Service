FROM python:3.9.6-slim

COPY /requirements.txt /requirements.txt

RUN pip install --upgrade pip && pip install -r /requirements.txt

#ADD ./fastapi_service /app/fastapi_service

WORKDIR /app/fastapi_service/

ENTRYPOINT [ "python", "main.py" ]