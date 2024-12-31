from wyoming_salutespeech_gateway import salutespeech_adapter

with open('samples/sample2.mp3', 'rb') as audio_file:
    print ( salutespeech_adapter.recognize( audio=audio_file.read() ) )