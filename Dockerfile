# Container image that runs your code
FROM --platform=amd64 python:3.9-slim
# FROM tensorflow/tensorflow

#RUN apk update
#RUN apk add chromium chromium-chromedriver
RUN apt update
RUN apt install --yes chromium chromium-driver

RUN pip install --upgrade pip
RUN pip install virtualenv
RUN virtualenv venv
COPY requirements.docker.txt .
RUN . ./venv/bin/activate; pip install -r requirements.docker.txt
COPY bot.py .
COPY mlcaptcha.py .
COPY solver.keras .
COPY entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]