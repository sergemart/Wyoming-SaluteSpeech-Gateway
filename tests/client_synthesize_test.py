__package__ = 'wyoming_salutespeech_gateway'

import os, wave
# noinspection PyUnresolvedReferences
from . import app
# noinspection PyUnresolvedReferences
from . import client


app.parse_arguments()
app.setup_custom_logger("root")
client.setup_ca_cert()

audio = client.synthesize(text="7 ежей.", language="ru-RU", voice="Ost_24000")
filename = os.path.dirname(os.path.abspath(__file__)) + "/samples/result.wav"
#with open(filename, 'wb') as audiofile:
#    audiofile.write(audio)
wav_file: wave.Wave_write = wave.open(filename, "wb")
with wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(24000)
    wav_file.writeframes(audio)