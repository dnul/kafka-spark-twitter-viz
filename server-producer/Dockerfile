FROM python:3.8-alpine
RUN apk add --no-cache --virtual .build-deps gcc musl-dev python3-dev 
COPY src/requirements.txt /
RUN  pip install -r /requirements.txt 
#&& apk del .build-deps

#RUN pip install -r /requirements.txt
COPY src/ /app  
WORKDIR /app
#use flask
CMD ["python","main.py"]
#CMD ["gunicorn","-k eventlet","-w 4","--threads","12","--bind","0.0.0.0:5000","--log-level", "DEBUG","main:app"]