FROM python:3.10.8-alpine3.16
ENV TZ "Europe/Moscow"
RUN mkdir /home/app
WORKDIR home/app
RUN apk add --update -U build-base libffi-dev openssl-dev  \
    zlib-dev ca-certificates tzdata wget vim curl
RUN python -m pip install --upgrade pip
ADD requirements.txt .
RUN pip install -U -r requirements.txt
ADD . .
CMD ["uvicorn", "main:app", "--port", "5000"]