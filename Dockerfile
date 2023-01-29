FROM python:3.7-alpine

EXPOSE 5000

WORKDIR /CloudExp

RUN apk update \
    && apk add --no-cache mariadb-dev linux-headers libffi-dev gcc musl-dev openssl-dev cargo \
    && apk add python3-dev

# Install project dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . .

ENV FLASK_APP=run.py

ENTRYPOINT ["gunicorn"]
CMD ["--workers=3", "app:run"]
