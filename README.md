# StartHack23 - Chatbot Project with Antler

This project is part of the StartHack23 Chatbot project with Antler. Our goal is to create a visual and audio chatbot to help combat loneliness among the elderly. To get started, we followed this tutorial: https://github.com/deepgram-devs/live-transcription-fastapi.

![face.png](face.png)

## Required API Keys
In order to get this project to run, you will need to sign up for a free OpenAI and Deepgram account. Once you do, you will be able to generate API keys for authentication. These keys are required to get this project to run.

## Setup Instructions

To set up the project, follow these steps:

1. Create a `.env` file in the root folder with the following structure:

    ```
    OPENAI_API_KEY=<your openai api key>
    DEEPGRAM_API_KEY=<your deepgram api key>
    ```

2. Create a virtual environment and activate it:

    ```
    python -m venv venv
    source venv/bin/activate
    ```

3. Install all the dependencies:

    ```
    pip install -r requirements.txt
    ```

4. To start the application, navigate to the server folder and start the web app:

    ```
    cd server
    uvicorn main:app --reload
    ```

5. Open up a browser and access the app under `127.0.0.1:8000`


## Creators

- Thomas Boehm
- Michael Fuest
- Nicolas Neudeck"""