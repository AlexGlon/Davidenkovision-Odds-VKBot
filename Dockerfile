FROM python:3.10.6-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk add --update
RUN apk upgrade

ADD . /opt/dv-vkbot

COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --system --deploy

ENTRYPOINT ["python3", "./opt/dv-vkbot/main.py"]
