__package__ = 'wyoming_salutespeech_gateway'

from . import client


class SaluteSpeechModel:
	""" Instance of this class is consumed by Wyoming server within an event handler """

	def transcribe(self, filename: str, language: str) -> str:
		""" Do the STT job """

		with open(filename, 'rb') as audio:
			return client.recognize( audio.read(), language )
