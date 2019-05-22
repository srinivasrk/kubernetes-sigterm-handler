FROM python:3.6
WORKDIR /app
COPY consumer.py /app/
RUN pip install pika
CMD ["python", "consumer.py"]
