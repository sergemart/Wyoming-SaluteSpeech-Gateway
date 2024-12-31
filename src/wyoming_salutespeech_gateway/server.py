__package__ = 'wyoming_salutespeech_gateway'

import asyncio
import logging
from functools import partial

from wyoming.info import AsrModel, AsrProgram, Attribution, Info
from wyoming.server import AsyncServer

from . import app, model_stub
from .event_handler import GatewayEventHandler


_LOGGER = logging.getLogger("root")


# endregion
# region =============================================== Interface

def get_wyoming_info() -> Info:
    """ Get a Wyoming protocol implementation metadata """
    return Info(
        asr=[
            AsrProgram(
                name="Wyoming-SaluteSpeech Gateway",
                description="A gateway between a Wyoming protocol client and SberDevices SaluteSpeech STT/TTS cloud service.",
                attribution=Attribution(
                    name="Sergei Martynov",
                    url="https://github.com/sergemart/wyoming-salutespeech-gateway/",
                ),
                version="1.0",
                installed=True,
                models=[
                    AsrModel(
                        name="SaluteSpeech",
                        description="SaluteSpeech STT/TTS model",
                        attribution=Attribution(
                            name="Sber Devices",
                            url="https://developers.sber.ru/docs/ru/salutespeech/overview",
                        ),
                        version="latest",
                        installed=True,
                        languages=["ru-RU", "kz-KZ"],
                    )
                ],
            )
        ],
    )


async def run():
    """ Start the Wyoming server """

    wyoming_server = AsyncServer.from_uri(app.cli_args.listen_uri)
    _LOGGER.info("Wyoming server is instantiated")
    model_lock = asyncio.Lock()
    await wyoming_server.run(
        partial(
            GatewayEventHandler,
            get_wyoming_info(),
            app.cli_args,
            model_stub.SaluteSpeechModel(),
            model_lock,
        )
    )


# endregion