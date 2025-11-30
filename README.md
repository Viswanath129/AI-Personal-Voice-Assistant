# AI-Personal-Voice-Assistant
A robust Python assistant automating WhatsApp, app control, and OS-level actions using ADB and Vosk offline speech recognition.
Python AI Voice Assistant (ADB + Vosk)

This is a voice-controlled assistant that automates your Android device using the Android Debug Bridge (ADB) and recognizes speech offline using the Vosk neural network model.

Prerequisites

1. Hardware

A PC with Python installed.

A Microphone.

An Android Phone.

A USB Cable.

2. Android Setup (Crucial)

Go to Settings > About Phone.

Tap Build Number 7 times to enable Developer Options.

Go back to Settings > System > Developer Options.

Enable USB Debugging.

Connect your phone to your PC via USB.

3. ADB Setup

You must have adb installed on your system path.

Windows: Download "SDK Platform-Tools for Windows", extract it, and add the folder path to your System Environment Variables.

Mac/Linux: brew install android-platform-tools or sudo apt install adb.

To verify, open a terminal and type:

adb devices


You should see your device listed.

Installation

Install Python Libraries:

pip install -r requirements.txt


(Note: If you have trouble installing PyAudio on Windows, you may need to download a .whl file from a repository like Gohlke's or install pipwin and run pipwin install pyaudio).

Download Vosk Model:

Vosk needs a model to work. It is not included in the code because it is large.

Go to: https://alphacephei.com/vosk/models

Download a small model like vosk-model-small-en-us-0.15 (for speed) or a larger one for accuracy.

Extract the downloaded zip file.

Rename the extracted folder to model and place it in the same directory as assistant.py.

Usage

Run the script:

python assistant.py


Speak commands clearly into your microphone.

Available Voice Commands

"Open WhatsApp": Launches WhatsApp on your phone.

"Open YouTube": Launches YouTube.

"Volume Up" / "Volume Down": Adjusts phone media volume.

"Go Home": Returns to the phone's home screen.

"Take Screenshot": Saves a screenshot to your phone's storage.

"Type [message]": Types text into the active text field on the phone (e.g., say "Type hello world").

"Stop" / "Exit": Shuts down the assistant.

Troubleshooting

"Model not found": Ensure the folder is named exactly model and is next to the python script.

"Device not found": Check your USB cable and ensure you authorized the PC on your phone screen when you plugged it in.

Requirements:-
vosk==0.3.45
pyaudio==0.2.14
colorama==0.4.6
