FROM python:3.6
WORKDIR /app
COPY test.py /app/
CMD ["python", "test.py"]
