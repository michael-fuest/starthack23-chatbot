from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Dict, Callable
from deepgram import Deepgram
from dotenv import load_dotenv
import openai
import os
import pyttsx3
import datetime


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name='static')

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
dg_client = Deepgram(os.getenv('DEEPGRAM_API_KEY'))

templates = Jinja2Templates(directory="templates")

time_stop_talking = datetime.datetime.now()

def change_voice(engine, language, gender='VoiceGenderFemale'):
    for voice in engine.getProperty('voices'):
        if language in voice.languages and gender == voice.gender:
            engine.setProperty('voice', voice.id)
            return True

    raise RuntimeError("Language '{}' for gender '{}' not found".format(language, gender))

async def process_audio(fast_socket: WebSocket):
    async def get_transcript(data: Dict) -> None:
        if 'channel' in data:
            transcript = data['channel']['alternatives'][0]['transcript']
            print(f"Transcript: '{transcript}'")
        
            if transcript:
                gpt_response = get_response(transcript)
                await fast_socket.send_text("TALKING=TRUE")
                play_response(gpt_response)
                await fast_socket.send_text("TALKING=FALSE")
                await fast_socket.send_text("Transcript: " + transcript + "\n")
                await fast_socket.send_text("GPT RESPONSE: " + gpt_response + "\n")
        else:
            print('no transcript')

    deepgram_socket = await connect_to_deepgram(get_transcript)
    return deepgram_socket


def process_response(prompt: str):
    response = get_response(prompt)
    play_response(response)
    return response

def play_response(text):
    engine = pyttsx3.init()
    try:
        engine.setProperty('voice', 'com.apple.speech.synthesis.voice.yannick.premium')
    except:
        change_voice(engine, 'de_DE', 'VoiceGenderMale')
    engine.setProperty('rate', 130)
    engine.setProperty('volume', 10)
    engine.say(text)
    engine.runAndWait()
    print('Response played')
    global time_stop_talking
    time_stop_talking = datetime.datetime.now()

async def connect_to_deepgram(transcript_received_handler: Callable[[Dict], None]):
    try:
        socket = await dg_client.transcription.live({
            'punctuate': True,
            'interim_results': False,
            'language': 'de',
            'endpoint': 350
        })
        socket.registerHandler(socket.event.CLOSE, lambda c: print(f'Connection closed with code {c}.'))
        socket.registerHandler(socket.event.TRANSCRIPT_RECEIVED, transcript_received_handler)
        
        return socket
    except Exception as e:
        raise Exception(f'Could not open socket: {e}')
    
def get_response(message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = [
        {"role": "system", "content": "You are a friendly conversational partner named Walter that occasionally asks follow-up questions and replies in german only. Your name is Walter and you are talking to Hannelore and you are very friendly. You speak like an 80-year old german granddad. You know that Hannelore is 76 years old and that her husband died 14 years ago. You know that she has three children, two of them are named Max and Stefan and that she has a daughter named Christiane. You know that she lives in Otterfing. You know that she likes to paint and play Scrabble. You know that her son Stefan is coming to visit her on Wednesday and that he is bringing his two children with him. You know that she is very happy about that."},
        {"role": "user", "content": "Hallo, ich bin Hannelore."},
        {"role": "assistant", "content": "Hallo Hannelore, schön dich kennenzulernen."},
        {"role": "user","content": message},
        ],
        temperature=0.7,
        max_tokens=100,
    )
    return response['choices'][0]['message']['content']
 
@app.get("/", response_class=HTMLResponse)
def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/listen")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        deepgram_socket = await process_audio(websocket) 

        while True:
            data = await websocket.receive_bytes()

            # if the time since the last response was less than 2 seconds, dont forward the audio
            if (datetime.datetime.now() - time_stop_talking).total_seconds() < 2:
                continue
            deepgram_socket.send(data)
    except Exception as e:
        raise Exception(f'Could not process audio: {e}')
    finally:
        await websocket.close()