FROM python:3.6
WORKDIR /app
RUN pip install pika
COPY consumer.py /app/
CMD ["python", "consumer.py"]
