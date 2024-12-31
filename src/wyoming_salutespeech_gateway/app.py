import argparse
import asyncio
import logging
import tempfile
import time
import wave

from . import server

# region =============================================== The app context

cli_args: argparse.Namespace

token: str = ""
token_expiration_time: int = 0
token_expiration_time_delta: int = 30   # A protection interval before the expiration time, in seconds

_LOGGER: logging.Logger


# endregion
# region =============================================== Entrypoint

def start() -> None:
    """ Start the app """

    _LOGGER.info('Wyoming-Salutespeech Gateway is starting')
    asyncio.run( server.run() )


# endregion
# region =============================================== Utilities

def parse_arguments() -> None:
    """ Parse CLI arguments """

    global cli_args

    parser = argparse.ArgumentParser()
    parser.add_argument("--auth-key", default="", help="SberDevices authorization key for the SaluteSpeech service")
    parser.add_argument("--listen-uri", default="tcp://0.0.0.0:9999", help="Wyoming server URI to listen to, like 'tcp://0.0.0.0:9999'")
    parser.add_argument("--sber-auth-url", default="https://ngw.devices.sberbank.ru:9443/api/v2/oauth", help="SberDevices authorization URL")
    parser.add_argument("--salutespeech-url", default="https://smartspeech.sber.ru/rest/v1/speech:recognize", help="SaluteSpeech service URL")
    parser.add_argument("--salutespeech-model", default="general", help="SaluteSpeech AI model flavor, like 'general', 'ivr' etc.")
    parser.add_argument("--download-dir", default=tempfile.TemporaryDirectory(), help="A directory to temporarily store intermediate audio files")
    parser.add_argument("--language", default="ru-RU", help="Transcription language, like 'ru-RU'")
    parser.add_argument("--log-level", default="WARNING", help="Log level, like 'ERROR', 'INFO', 'DEBUG' etc.")

    cli_args = parser.parse_args()
    return


def setup_custom_logger(name) -> None:
    """ Set up the app logger"""

    global _LOGGER
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    _LOGGER = logging.getLogger(name)
    _LOGGER.setLevel( logging.getLevelNamesMapping()[cli_args.log_level] )
    _LOGGER.addHandler(handler)


def check_if_token_expired() -> bool:
    """Check if the authentication token expired. Returns True if the token is expired"""

    global token_expiration_time
    global token_expiration_time_delta
    current_time: int = int( time.time() )
    result: bool = current_time > token_expiration_time - token_expiration_time_delta
    return result


def write_wav_file(filename: str, data: bytes) -> None:
    """ Write data to a wav file """

    wav_file: wave.Wave_write = wave.open(filename, "wb")
    with wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(data)
    _LOGGER.debug(f"Audio written to file {filename}")


# endregion