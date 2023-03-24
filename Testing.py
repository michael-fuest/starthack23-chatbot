import speech_recognition as sr
import pyaudio as pa
import openai
import os
import gtts
import pyttsx3

openai.api_key = os.environ["OPENAI_API_KEY"]

def recognize_speech():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print('Listening...')
        recognizer.pause_threshold = 1
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout = 5)
        print('Done listening!')

    response = {
            "success": True,
            "error": None,
            "transcription": None
        }

    try:
        print('transcribing...')
        response["transcription"] = recognizer.recognize_whisper_api(audio)
        print('transcription received!')
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
        print(response["error"])
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"
        print(response["error"])
    return response


def get_response(message, message_hist = None):
    if message_hist:
        messages = message_hist
    else:
        messages = [
        {"role": "system", "content": "You are a friendly conversational partner that occasionally asks follow-up questions and replies in german only. Your name is Walter and you are talking to Hannelore and you are very friendly. You speak like an 80-year old german granddad"},
        {"role": "user", "content": "Hallo, ich bin Hannelore. Ich habe drei Kinder, die heißen Max, Stefan und Christiane. Ich wohne in Otterfing, bin 76 Jahre alt und mein Mann ist vor 14 Jahren an Krebs verstorben. Ich male gerne und spiele viel Scrabble. Mein Sohn Stefan kommt mich am Mittwoch besuchen. Er bringt seine zwei Kinder mit. Ich freue mich sehr darauf."},
        {"role": "user", "content": message},
        ]
    print('responding...')
    try:
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages = messages, max_tokens = 100)
        print('response received!')
    except: 
        print('response failed')
        return ('Sorry, ich habe dich nicht verstanden. Bitte versuche es noch einmal.', messages)
    return (response['choices'][0]['message']['content'], messages)


def text_to_speech(text):
    engine = pyttsx3.init()
    engine.setProperty('voice', 'com.apple.eloquence.de-DE.Reed')
    engine.setProperty('rate', 130)
    engine.setProperty('volume', 10)
    engine.say(text)
    engine.runAndWait()
    print('text spoken!')
    return

def add_to_msg_history(message, message_history, user = False):
    message_history.append({"role": "assistant", "content": message})
    return message_history


if __name__ == "__main__":
    #Initialization without message history
    text_to_speech('Hallo, ich bin dein digitaler Begleiter. Wie kann ich dir helfen?')
    print("Start talking!")
    guess = recognize_speech()['transcription']
    print('Your prompt: ', guess)
    reply, hist = get_response(guess)
    print(reply)
    hist = add_to_msg_history(reply, hist)
    while True:
        print("Start talking!")
        guess = recognize_speech()['transcription']
        print('Your prompt: ', guess)
        reply, hist = get_response(guess, message_hist=hist)
        print('Response: ', reply)
        hist = add_to_msg_history(reply, hist)
        hist = add_to_msg_history(guess, hist, user= True)
        text_to_speech(reply)
        
        


        
