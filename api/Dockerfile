FROM python:3.9.6

COPY /requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

ADD ./fastapi_service /app/fastapi_service
WORKDIR /app/fastapi_service/

CMD [ "python", "main.py" ]