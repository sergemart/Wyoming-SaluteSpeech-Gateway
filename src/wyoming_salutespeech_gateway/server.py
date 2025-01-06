__package__ = 'wyoming_salutespeech_gateway'

import asyncio
from functools import partial
import math

from wyoming.info import AsrModel, AsrProgram, TtsProgram, TtsVoice, Attribution, Info
from wyoming.server import AsyncServer

from . import app
from .event_handler import GatewayEventHandler


# endregion
# region =============================================== Interface

def get_wyoming_info() -> Info:
    """ Get Wyoming protocol implementation metadata """

    return Info(
        asr=[
            AsrProgram(
                name="Wyoming-SaluteSpeech Gateway",
                description="A gateway between a Wyoming protocol client and SberDevices SaluteSpeech STT/TTS cloud service.",
                attribution=Attribution(
                    name="Sergei Martynov",
                    url="https://github.com/sergemart/wyoming-salutespeech-gateway/",
                ),
                version="0.2",
                installed=True,
                models=[
                    AsrModel(
                        name="SaluteSpeech",
                        description="SaluteSpeech STT/TTS model",
                        attribution=Attribution(
                            name="SberDevices",
                            url="https://developers.sber.ru/docs/ru/salutespeech/overview",
                        ),
                        version="latest",
                        installed=True,
                        languages=["ru-RU", "kz-KZ"],
                    )
                ],
            )
        ],
        tts=[
            TtsProgram(
                name="Wyoming-SaluteSpeech Gateway",
                description="A gateway between a Wyoming protocol client and SberDevices SaluteSpeech STT/TTS cloud service.",
                attribution=Attribution(
                    name="Sergei Martynov",
                    url="https://github.com/sergemart/wyoming-salutespeech-gateway/",
                ),
                installed=True,
                version="0.2",
                voices=[
                    TtsVoice(
                        name="Nec_24000",
                        description="Наталья",
                        attribution=Attribution(
                            name="SberDevices",
                            url="https://developers.sber.ru/docs/ru/salutespeech/overview",
                        ),
                        installed=True,
                        version="latest",
                        languages=["ru-RU"],
                    ),
                    TtsVoice(
                        name="Bys_24000",
                        description="Борис",
                        attribution=Attribution(
                            name="SberDevices",
                            url="https://developers.sber.ru/docs/ru/salutespeech/overview",
                        ),
                        installed=True,
                        version="latest",
                        languages=["ru-RU"],
                    ),
                    TtsVoice(
                        name="May_24000",
                        description="Марфа",
                        attribution=Attribution(
                            name="SberDevices",
                            url="https://developers.sber.ru/docs/ru/salutespeech/overview",
                        ),
                        installed=True,
                        version="latest",
                        languages=["ru-RU"],
                    ),
                    TtsVoice(
                        name="Ost_24000",
                        description="Александра",
                        attribution=Attribution(
                            name="SberDevices",
                            url="https://developers.sber.ru/docs/ru/salutespeech/overview",
                        ),
                        installed=True,
                        version="latest",
                        languages=["ru-RU"],
                    ),
                    TtsVoice(
                        name="Pon_24000",
                        description="Сергей",
                        attribution=Attribution(
                            name="SberDevices",
                            url="https://developers.sber.ru/docs/ru/salutespeech/overview",
                        ),
                        installed=True,
                        version="latest",
                        languages=["ru-RU"],
                    ),
                    TtsVoice(
                        name="Kin_24000",
                        description="Kira",
                        attribution=Attribution(
                            name="SberDevices",
                            url="https://developers.sber.ru/docs/ru/salutespeech/overview",
                        ),
                        installed=True,
                        version="latest",
                        languages=["en-US"],
                    ),
                ],
            )
        ],
    )


def split_audio_into_chunks(audio: bytes):
    """ A generator function to split an audio stream into chunks """

    bytes_per_chunk = app.cli_args.chunk_size * 2   # 2 byte (16 bit) sample width * 1 channel = 2 bytes per sample
    chunks_number = int( math.ceil(len(audio) / bytes_per_chunk) )
    for i in range(chunks_number):
        offset = i * bytes_per_chunk
        yield audio[offset: offset + bytes_per_chunk]


async def run():
    """ Start the Wyoming server """

    wyoming_server = AsyncServer.from_uri(app.cli_args.listen_uri)
    app.LOGGER.info("Wyoming server is instantiated.")
    await wyoming_server.run(
        partial(
            GatewayEventHandler
        )
    )


# endregion