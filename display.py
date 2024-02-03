"""Periodically read conv.txt and display it in a Taipy app."""

import time
from threading import Thread
from taipy.gui import Gui, State, invoke_callback, get_state_id
import os
from os import PathLike
# from time import time
import asyncio
from typing import Union

from dotenv import load_dotenv
import openai
from deepgram import Deepgram
import pygame
from pygame import mixer
import elevenlabs

#EXTERNALLY LISTEN AND SPEAK
#from listen_and_speak import listen_and_speak

conversation = {"Conversation": []}
state_id_list = []
selected_row = [1]
status = "Idle"
# Load API keys
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
elevenlabs.set_api_key(os.getenv("ELEVENLABS_API_KEY"))

# Initialize APIs
gpt_client = openai.Client(api_key=OPENAI_API_KEY)
deepgram = Deepgram(DEEPGRAM_API_KEY)
# mixer is a pygame module for playing audio
mixer.init()

# Change the context if you want to change Jarvis' personality
# context = "You are Jarvis, Alex's human assistant. You are witty and full of personality. Your answers should be limited to 1-2 short sentences."
# conversation = {"Conversation": []}
# RECORDING_PATH = "audio/recording.wav"

def on_init(state: State) -> None:
    """
    On app initialization, get the state (user) ID
    so that we know which app to update.
    """
    state_id = get_state_id(state)
    state_id_list.append(state_id)


def client_handler(gui: Gui, state_id_list: list) -> None:
    """
    Runs in a separate thread and periodically calls to read conv.txt.

    Args:
        - gui: The GUI object.
        - state_id_list: The list of state IDs.
    """
    while True:
        time.sleep(0.5)
        if len(state_id_list) > 0:
            invoke_callback(gui, state_id_list[0], update_conv, [])


def update_conv(state: State) -> None:
    """
    Read conv.txt and update the conversation table.

    Args:
        - state: The current state of the app.
    """
    with open("status.txt", "r") as f:
        status = f.read()
    state.status = status
    with open("conv.txt", "r") as f:
        conv = f.read()
    conversation["Conversation"] = conv.split("\n")
    if conversation == state.conversation:
        return
    # If the conversation has changed, update it and move to the last row
    state.conversation = conversation
    state.selected_row = [len(state.conversation["Conversation"]) - 1]


def erase_conv(state: State) -> None:
    """
    Erase conv.txt and update the conversation table.

    Args:
        - state: The current state of the app.
    """
    with open("conv.txt", "w") as f:
        f.write("")


def style_conv(state: State, idx: int, row: int) -> str:
    """
    Apply a style to the conversation table depending on the message's author.

    Args:
        - state: The current state of the app.
        - idx: The index of the message in the table.
        - row: The row of the message in the table.

    Returns:
        The style to apply to the message.
    """
    if idx is None:
        return None
    elif idx % 2 == 0:
        return "user_message"
    else:
        return "gpt_message"


page = """
<|layout|columns=300px 1|
<|part|render=True|class_name=sidebar|
# Taipy **Jarvis**{: .color-primary} # {: .logo-text}
<|New Conversation|button|class_name=fullwidth plain|id=reset_app_button|on_action=erase_conv|>
<br/>
<|{status}|text|>
|>

<|part|render=True|class_name=p2 align-item-bottom table|
<|{conversation}|table|style=style_conv|show_all|width=100%|rebuild|selected={selected_row}|>
|>
|>
"""

gui = Gui(page)

# def other_thread_handler():
#     while True:
#         print("Other thread waking ...")
#         time.sleep(0.5)

# Periodically read conv.txt on a separate thread
t = Thread(
    target=client_handler,
    args=(
        gui,
        state_id_list,
    ),
)
t.start()


# EXTERNALLY LISTEN AND SPEAK FOR THE MOMENT

# t2 = Thread(
#     target=listen_and_speak
# )

# t2.start()

gui.run(debug=True, dark_mode=True)
