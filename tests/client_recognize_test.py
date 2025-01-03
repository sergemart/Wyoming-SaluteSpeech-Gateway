__package__ = 'wyoming_salutespeech_gateway'

import os
# noinspection PyUnresolvedReferences
from . import app
# noinspection PyUnresolvedReferences
from . import client


app.parse_arguments()
app.setup_custom_logger("root")
client.setup_ca_cert()

filename = os.path.dirname(os.path.abspath(__file__)) + "/samples/sample2.wav"
with open(filename, 'rb') as audiofile:
    audio = audiofile.read()
text = client.recognize(audio=audio, language="ru-RU")

print(text)
