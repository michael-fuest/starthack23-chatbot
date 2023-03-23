import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    # engine.setProperty('voice', voice.id)
    print(f"voice if: {voice.id}, gernder: {voice.gender}, languages: {voice.languages}")