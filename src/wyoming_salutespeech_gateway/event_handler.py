__package__ = 'wyoming_salutespeech_gateway'

import asyncio
import os
import tempfile
import time
from pathlib import Path

from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioChunkConverter, AudioStop
from wyoming.event import Event
from wyoming.info import Describe
from wyoming.server import AsyncEventHandler
from wyoming.tts import Synthesize

from . import app, server, client, model_stub


class GatewayEventHandler(AsyncEventHandler):
    """Server's incoming request handler"""

    def __init__(
        self,
        model_lock: asyncio.Lock,
        *args,
        **kwargs,
    ) -> None:
        """ Constructor """

        super().__init__(*args, **kwargs)

        self._model = model_stub.SaluteSpeechModel()
        self._model_lock = model_lock
        self._language = app.cli_args.language
        self._voice = app.cli_args.salutespeech_voice
        self._temp_dir = tempfile.TemporaryDirectory()
        self._audio = b""
        self._audio_converter = AudioChunkConverter(rate=16000, width=2, channels=1)


    async def handle_event(self, event: Event) -> bool:
        """Handle the event"""

        if Describe.is_type(event.type):
            await self.write_event( server.get_wyoming_info().event() )
            app.LOGGER.debug("Processed a 'Describe' event: Wyoming info is sent to the client.")
            return True

        if Transcribe.is_type(event.type):
            transcribe = Transcribe.from_event(event)
            if transcribe.language:
                self._language = transcribe.language
                app.LOGGER.debug(f"Processed a 'Transcribe' event: the language is set to '{transcribe.language}'.")
            return True

        if AudioChunk.is_type(event.type):
            if not self._audio:
                app.LOGGER.debug("Processing an 'AudioChunk' event: starting to receive audio chunks.")
            chunk = AudioChunk.from_event(event)
            chunk = self._audio_converter.convert(chunk)
            self._audio += chunk.audio
            return True

        if AudioStop.is_type(event.type):
            app.LOGGER.debug("Processing an 'AudioStop' event: storing the audio in the intermediate file.")
            filename = os.path.join(self._temp_dir.name, f"{time.monotonic_ns()}.wav")
            app.write_wav_file(str(filename), self._audio)

            async with self._model_lock:
                start_time = time.time()
                app.LOGGER.debug("Processing an 'AudioStop' event: starting a transcription.")
                text = self._model.transcribe( str(filename), self._language )
                app.LOGGER.info(f"Processing an 'AudioStop' event: the transcription is completed in {time.time() - start_time:.2f} seconds")

            await self.write_event( Transcript(text=text).event() )
            app.LOGGER.debug("Processed an 'AudioStop' event: data is sent to the client.")

            # Clean up
            self._audio = b""
            self._language = app.cli_args.language
            Path(filename).unlink()
            app.LOGGER.debug(f"Processed an 'AudioStop' event: deleted the intermediate audio file {filename}")

        if Synthesize.is_type(event.type):
            synthesize = Synthesize.from_event(event)
            text = synthesize.text
            if synthesize.voice:
                self._voice = synthesize.voice.name
                self._language = synthesize.voice.language
                app.LOGGER.debug("Processing a 'Synthesize' event: the event conveys a 'voice' object.")
                app.LOGGER.debug(f"Processing a 'Synthesize' event: the voice is set to '{synthesize.voice.name}'.")
                app.LOGGER.debug(f"Processing a 'Synthesize' event: the language is set to '{synthesize.voice.language}'.")
            app.LOGGER.debug(f"Processing a 'Synthesize' event: staring to synthesize the text '{text}' with the voice {self._voice}.")
            audio = client.synthesize(text=text, language=self._language, voice=self._voice)

            app.LOGGER.debug("Processing a 'Synthesize' event: storing the synthesized audio in the intermediate file.")
            filename = os.path.join(self._temp_dir.name, f"{time.monotonic_ns()}.wav")
            app.write_wav_file(str(filename), audio)

        return True
