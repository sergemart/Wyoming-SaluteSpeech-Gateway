# Wyoming-SaluteSpeech Gateway

Шлюз между облачным сервисом SaluteSpeech от Сбера и клиентом, использующим Wyoming protocol. На данный момент реализованы синхронные операции STT (ASR) и TTS.

A gateway between a Wyoming protocol client and SberDevices SaluteSpeech STT/TTS cloud service. This is not a Home Assistant integration but a stand-alone service, which can be used with any Wyoming client.

Это не интеграция Home Assistant, а отдельный сервис. Для клиента Wyoming (например, Home Assistant) он выглядит как сервер Wyoming. Чтобы использовать этот сервис в HA, нужно добавить интеграцию Wyoming Protocol и указать имя/адрес и порт сервиса (по умолчанию 9999).

##### Установка / Install:
```commandline
pip install poetry
git clone https://github.com/sergemart/Wyoming-SaluteSpeech-Gateway.git
cd Wyoming-SaluteSpeech-Gateway
poetry install
```
##### Запуск с настройками по умолчанию / Run with default options:
```commandline
poetry run python3 src/wyoming_salutespeech_gateway --auth-key your_authorization_key
```
##### Запуск с настройками для отладки / Run with debug options:
```commandline
poetry run python3 src/wyoming_salutespeech_gateway --log-level=DEBUG --keep-audio-files --download-dir=~/downloads/WAVs --auth-key=your_authorization_key
```
##### Возможные параметры запуска / Command line options:
```commandline
usage: __main__.py [-h] [--auth-key AUTH_KEY] [--listen-uri LISTEN_URI]
                   [--sber-auth-url SBER_AUTH_URL]
                   [--salutespeech-url SALUTESPEECH_URL]
                   [--salutespeech-model SALUTESPEECH_MODEL]
                   [--salutespeech-voice SALUTESPEECH_VOICE]
                   [--keep-audio-files] [--download-dir DOWNLOAD_DIR]
                   [--language LANGUAGE] [--chunk-size CHUNK_SIZE]
                   [--log-level LOG_LEVEL]

options:
  -h, --help            show this help message and exit
  --auth-key AUTH_KEY   SberDevices authorization key for the SaluteSpeech
                        service
  --listen-uri LISTEN_URI
                        Wyoming server URI to listen to, like
                        'tcp://0.0.0.0:9999'
  --sber-auth-url SBER_AUTH_URL
                        SberDevices authorization URL
  --salutespeech-url SALUTESPEECH_URL
                        SaluteSpeech service URL
  --salutespeech-model SALUTESPEECH_MODEL
                        SaluteSpeech AI model flavor: 'general', 'media',
                        'ivr', 'callcenter'
  --salutespeech-voice SALUTESPEECH_VOICE
                        SaluteSpeech synth voice: 'Ost_24000', 'May_24000'
                        etc.
  --keep-audio-files    Keep intermediate audio files, if set
  --download-dir DOWNLOAD_DIR
                        A directory to temporarily store intermediate audio
                        files
  --language LANGUAGE   Transcription language, like 'ru-RU'
  --chunk-size CHUNK_SIZE
                        Number of samples per Wyoming audio chunk
  --log-level LOG_LEVEL
                        Log level, like 'ERROR', 'INFO', 'DEBUG' etc.
```
##### Установка в контейнер:
```
cd docker
```
Здесь нужно отредактировать файл `entrypoint.sh` и записать в него свой ключ авторизации.
Создать образ:
```
docker build --tag wssg .
```
Создать и запустить контейнер:
```commandline
docker run -d --name wssg -p 9999:9999 wssg:latest
```
