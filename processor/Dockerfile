FROM openjdk:8-slim
COPY --from=python:3.7-alpine / /

RUN apk add --no-cache --virtual .build-deps gcc musl-dev python3-dev 
COPY src/requirements.txt /
RUN  pip install -r /requirements.txt 
#&& apk del .build-deps

#RUN pip install -r /requirements.txt
COPY src/ /app  
WORKDIR /app
ENV FLASK_DEBUG=True
CMD ["python","spark-consumer-kafka.py"]
#CMD ["gunicorn", "-w 4", "main:app"]