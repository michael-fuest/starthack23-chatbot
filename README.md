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

2. Create a virtual environment with the following command:

    ```
    python -m venv venv
    ```

3. Activate the virtual environment with the following command:

    ```
    source venv/bin/activate
    ```

4. Install all the dependencies with the following command:

    ```
    pip install -r requirements.txt
    ```

5. To start the application, navigate to the server folder and start the web app with the following command:

    ```
    cd server
    uvicorn main:app --reload
    ```

## Folder Structure

    ├-env
    ├-server
    │ ├── __pycache__
    │ ├── static
    │   ├── styles.css
    │   ├── leise.gif
    │   └── sprechen.gif
    │ ├── templates
    │   └── index.html
    │ ├── .env
    │ └── main.py
    ├── .gitignore
    ├── face.png
    ├── README.md
    ├── requirements.txt
    └── Testing.py

## Creators

- Thomas Boehm
- Michael Fuest
- Nicolas Neudeck"""