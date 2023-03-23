from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, Callable
from deepgram import Deepgram
from dotenv import load_dotenv
import openai
import os
import pyttsx3

openai.api_key = os.environ["OPENAI_API_KEY"]

load_dotenv()
app = FastAPI()
dg_client = Deepgram(os.getenv('DEEPGRAM_API_KEY'))
engine = pyttsx3.init()
engine.setProperty('voice', 'com.apple.eloquence.de-DE.Reed')
engine.setProperty('rate', 130)
engine.setProperty('volume', 10)

templates = Jinja2Templates(directory="templates")

async def process_audio(fast_socket: WebSocket):
    async def get_transcript(data: Dict) -> None:
        #print('-' * 20)
        if 'channel' in data:
            transcript = data['channel']['alternatives'][0]['transcript']
            print('trans:', transcript)
        
            if transcript:
                gpt_response = await process_response(transcript, fast_socket)
                print('res:', gpt_response)
                await fast_socket.send_text(transcript + '\n' + gpt_response)

    deepgram_socket = await connect_to_deepgram(get_transcript)
    return deepgram_socket

async def process_response(prompt: str, fast_socket: WebSocket):
    global is_talking
    response = await get_response(prompt)
    is_talking = True
    play_response(response)
    is_talking = False
    await fast_socket.send_text(response)
    return response

def play_response(text):
    engine = pyttsx3.init()
    engine.setProperty('voice', 'com.apple.eloquence.de-DE.Reed')
    engine.setProperty('rate', 130)
    engine.setProperty('volume', 10)
    engine.say(text)
    engine.runAndWait()
    return

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
    
async def get_response(message):
    response = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a friendly conversational partner that occasionally asks follow-up questions and replies in german only."},
        {"role": "user", "content": message},
        ]
    ,temperature = 0.5,
    max_tokens = 100,
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
            if not is_talking:
                data = await websocket.receive_bytes()
                deepgram_socket.send(data)

    except Exception as e:
        raise Exception(f'Could not process audio: {e}')
    finally:
        await websocket.close()