FROM python:alpine

COPY main.py /app/

COPY requirements.txt /app/

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["python", "main.py"]