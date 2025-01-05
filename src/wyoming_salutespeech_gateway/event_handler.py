__package__ = 'wyoming_salutespeech_gateway'

import asyncio
import time

from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioChunkConverter, AudioStart, AudioStop
from wyoming.event import Event
from wyoming.info import Describe
from wyoming.server import AsyncEventHandler
from wyoming.tts import Synthesize

from . import app, server, client


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

        self._model_lock = model_lock
        self._language = app.cli_args.language
        self._voice = app.cli_args.salutespeech_voice
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
            async with self._model_lock:
                start_time = time.time()
                app.LOGGER.debug("Processing an 'AudioStop' event: starting a transcription.")
                text = client.recognize(self._audio, self._language)
                app.LOGGER.info(f"Processing an 'AudioStop' event: the transcription is completed in {time.time() - start_time:.2f} seconds.")

            await self.write_event( Transcript(text=text).event() )
            app.LOGGER.debug("Processed an 'AudioStop' event: the recognized text is sent to a Wyoming client.")

            # Clean up
            self._audio = b""
            self._language = app.cli_args.language

        if Synthesize.is_type(event.type):
            synthesize = Synthesize.from_event(event)
            text = synthesize.text
            if synthesize.voice:
                app.LOGGER.debug("Processing a 'Synthesize' event: the event conveys a 'voice' object.")
                self._voice = synthesize.voice.name if synthesize.voice.name else app.cli_args.salutespeech_voice
                self._language = synthesize.voice.language if synthesize.voice.language else app.cli_args.language
                app.LOGGER.debug(f"Processing a 'Synthesize' event: the voice is set to '{self._voice}'.")
                app.LOGGER.debug(f"Processing a 'Synthesize' event: the language is set to '{self._language}'.")
            start_time = time.time()
            app.LOGGER.debug(f"Processing a 'Synthesize' event: starting to synthesize the text '{text}'.")
            audio = client.synthesize(text=text, language=self._language, voice=self._voice)
            app.LOGGER.info(f"Processing a 'Synthesize' event: the synthesis is completed in {time.time() - start_time:.2f} seconds.")
            chunks = server.split_audio_into_chunks(audio)

            # Send the result to a Wyoming client
            await self.write_event(
                AudioStart(rate=24000, width=2, channels=1).event(),
            )
            for chunk in chunks:
                await self.write_event(
                    AudioChunk(audio=chunk, rate=24000, width=2, channels=1).event(),
                )
            await self.write_event(AudioStop().event())
            app.LOGGER.debug("Processed a 'Synthesize' event: the synthesized audio is sent to a Wyoming client.")

            # Clean up
            self._voice = app.cli_args.salutespeech_voice
            self._language = app.cli_args.language

        return True
