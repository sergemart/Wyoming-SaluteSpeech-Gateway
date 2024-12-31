__package__ = 'wyoming_salutespeech_gateway'

import argparse
import asyncio
import logging
import os
import tempfile
import time
from pathlib import Path

from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioChunkConverter, AudioStop
from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler

from . import app, model_stub


_LOGGER = logging.getLogger("root")


class GatewayEventHandler(AsyncEventHandler):
    """Server's incoming request handler"""

    def __init__(
        self,
        wyoming_info: Info,
        cli_args: argparse.Namespace,
        model: model_stub.SaluteSpeechModel,
        model_lock: asyncio.Lock,
        *args,
        **kwargs,
    ) -> None:
        """ Constructor """

        super().__init__(*args, **kwargs)

        self._cli_args = cli_args
        self._wyoming_info_event = wyoming_info.event()
        self._model = model
        self._model_lock = model_lock
        self._language = self._cli_args.language
        self._temp_dir = tempfile.TemporaryDirectory()
        self._audio = b""
        self._audio_converter = AudioChunkConverter(rate=16000, width=2, channels=1)


    async def handle_event(self, event: Event) -> bool:
        """Handle the event"""

        if Describe.is_type(event.type):
            await self.write_event(self._wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True

        if Transcribe.is_type(event.type):
            transcribe = Transcribe.from_event(event)
            if transcribe.language:
                self._language = transcribe.language
                _LOGGER.debug("Language set to %s", transcribe.language)
            return True

        if AudioChunk.is_type(event.type):
            if not self._audio:
                _LOGGER.debug("Receiving audio")
            chunk = AudioChunk.from_event(event)
            chunk = self._audio_converter.convert(chunk)
            self._audio += chunk.audio
            return True

        if AudioStop.is_type(event.type):
            _LOGGER.debug("Audio stopped")
            filename = os.path.join(self._temp_dir.name, f"{time.monotonic_ns()}.wav")
            app.write_wav_file(str(filename), self._audio)

            async with self._model_lock:
                start_time = time.time()
                _LOGGER.debug("Starting transcription")
                text = self._model.transcribe( str(filename), language=self._language )
                _LOGGER.info(f"Transcription completed in {time.time() - start_time:.2f} seconds")

            await self.write_event(Transcript(text=text).event())
            _LOGGER.debug("Completed request")

            # Reset
            self._audio = b""
            self._language = self._cli_args.language

            # Clean up temporary file
            Path(filename).unlink()
            _LOGGER.debug(f"Deleted temporary audio file {filename}")

        return True
