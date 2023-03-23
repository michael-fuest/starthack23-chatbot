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


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name='static')

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
dg_client = Deepgram(os.getenv('DEEPGRAM_API_KEY'))

templates = Jinja2Templates(directory="templates")

async def process_audio(fast_socket: WebSocket):
    async def get_transcript(data: Dict) -> None:
        if 'channel' in data:
            transcript = data['channel']['alternatives'][0]['transcript']
            print(f"Transcript: '{transcript}'")
        
            if transcript:
                gpt_response = process_response(transcript)
                await fast_socket.send_text("Transcript: " + transcript + "\n")
                await fast_socket.send_text("GPT RESPONSE: " + gpt_response + "\n")
        else:
            print('no transcript')

    deepgram_socket = await connect_to_deepgram(get_transcript)
    return deepgram_socket


def process_response(prompt: str):
    global is_talking
    response = get_response(prompt)
    is_talking = True
    play_response(response)
    is_talking = False
    return response


def change_voice(engine, language, gender='VoiceGenderFemale'):
    for voice in engine.getProperty('voices'):
        if language in voice.languages and gender == voice.gender:
            engine.setProperty('voice', voice.id)
            return True

    raise RuntimeError("Language '{}' for gender '{}' not found".format(language, gender))

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

async def connect_to_deepgram(transcript_received_handler: Callable[[Dict], None]):
    try:
        socket = await dg_client.transcription.live({
            'punctuate': True,
            'interim_results': False,
            'language': 'de',
            'endpoint': 200
        })
        socket.registerHandler(socket.event.CLOSE, lambda c: print(f'Connection closed with code {c}.'))
        socket.registerHandler(socket.event.TRANSCRIPT_RECEIVED, transcript_received_handler)
        
        return socket
    except Exception as e:
        raise Exception(f'Could not open socket: {e}')
    
def get_response(message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a friendly conversational partner that occasionally asks follow-up questions and replies in german only."
            },
            {
                "role": "user",
                "content": message
            },
        ],
        temperature=0.5,
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
            deepgram_socket.send(data)
    except Exception as e:
        raise Exception(f'Could not process audio: {e}')
    finally:
        await websocket.close()