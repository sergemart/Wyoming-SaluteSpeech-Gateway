__package__ = 'wyoming_salutespeech_gateway'

import logging
from . import client


_LOGGER = logging.getLogger("root")


class SaluteSpeechModel:
	""" Instance of this class is consumed by Wyoming server within an event handler """

	def __init__(self) -> None:
		""" Constructor """

		#self._args = args


	def transcribe(self, filename: str, language: str=None) -> str:
		""" Do the STT job """

		with open(filename, 'rb') as audio:
			return client.recognize( audio.read(), language )
