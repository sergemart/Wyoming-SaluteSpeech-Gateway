__package__ = 'wyoming_salutespeech_gateway'

import os
# noinspection PyUnresolvedReferences
from . import app
# noinspection PyUnresolvedReferences
from . import client


app.parse_arguments()
app.setup_custom_logger("root")
client.setup_ca_cert()

audio = client.synthesize(text="Восемнадцать ежей.", language="ru-RU", voice="Ost_24000")
filename = os.path.dirname(os.path.abspath(__file__)) + "/samples/result.wav"
with open(filename, 'wb') as audiofile:
    audiofile.write(audio)
