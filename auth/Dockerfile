FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 5000

ENV NAME AuthenticationMicroservice

CMD ["python", "app.py"]
