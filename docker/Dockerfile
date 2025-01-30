FROM alpine

RUN apk add --update --no-cache bash nano python3 poetry git \
    && rm /usr/lib/python*/EXTERNALLY-MANAGED \
    && git clone https://github.com/sergemart/Wyoming-SaluteSpeech-Gateway.git /theapp \
    && poetry config virtualenvs.create false \
    && poetry install --directory=/theapp -vv --no-interaction

COPY entrypoint.sh /

EXPOSE 9999/tcp

ENV NO_COLOR=1

ENTRYPOINT ["/entrypoint.sh"]
