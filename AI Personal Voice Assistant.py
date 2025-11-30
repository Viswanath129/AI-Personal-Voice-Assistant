import os
import sys
import json
import subprocess
import pyaudio
import time
import pyttsx3
from vosk import Model, KaldiRecognizer
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

class ADBAssistant:
    def __init__(self):
        self.setup_tts()
        self.check_adb_connection()
        self.load_model()
        
        # Dictionary to map spoken app names to their Android package names
        self.APP_MAP = {
            "whatsapp": "com.whatsapp",
            "youtube": "com.google.android.youtube",
            "chrome": "com.android.chrome",
            "spotify": "com.spotify.music",
            "maps": "com.google.android.apps.maps",
            "instagram": "com.instagram.android",
            "camera": "com.android.camera",
            "calculator": "com.google.android.calculator",
            "settings": "com.android.settings"
        }

    def setup_tts(self):
        """Initializes the Text-to-Speech engine."""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 170) # Speed of speech
            # Attempt to set a female voice if available (usually index 1)
            voices = self.engine.getProperty('voices')
            if len(voices) > 1:
                self.engine.setProperty('voice', voices[1].id)
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: TTS could not initialize. Assistant will be silent. ({e})")
            self.engine = None

    def speak(self, text):
        """Speaks the given text using TTS."""
        print(f"{Fore.MAGENTA}Assistant: {text}")
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()

    def check_adb_connection(self):
        """Checks if an Android device is connected via ADB."""
        print(f"{Fore.CYAN}Checking for Android devices...")
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            if 'device\n' not in result.stdout.replace('List of devices attached\n', ''):
                self.speak("I cannot find your phone. Please connect it and enable debugging.")
                print(f"{Fore.RED}No device found! Connect Android phone & enable USB Debugging.")
                sys.exit(1)
            else:
                print(f"{Fore.GREEN}Android Device Connected successfully.")
                self.speak("System online. Connected to device.")
        except FileNotFoundError:
            print(f"{Fore.RED}ADB is not installed or not in your PATH.")
            sys.exit(1)

    def load_model(self):
        """Loads the Vosk speech recognition model."""
        if not os.path.exists("model"):
            print(f"{Fore.RED}Model folder not found. Please download Vosk model and unpack as 'model'.")
            sys.exit(1)
        
        print(f"{Fore.CYAN}Loading Vosk Model...")
        try:
            self.model = Model("model")
            self.recognizer = KaldiRecognizer(self.model, 16000)
            print(f"{Fore.GREEN}Model loaded!")
        except Exception as e:
            print(f"{Fore.RED}Failed to load model: {e}")
            sys.exit(1)

    def execute_adb(self, command):
        """Executes a raw ADB command."""
        # Run in background to not block the main loop
        subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def launch_app(self, app_name):
        """Launches an app based on the APP_MAP."""
        package = self.APP_MAP.get(app_name)
        if package:
            self.speak(f"Opening {app_name}")
            # Monkey command is often more reliable for launching main activities than AM START without specific intent
            self.execute_adb(f"adb shell monkey -p {package} -c android.intent.category.LAUNCHER 1")
        else:
            self.speak(f"I don't know the app {app_name}")

    def process_command(self, text):
        """Advanced command processing logic."""
        text = text.lower()
        print(f"{Fore.BLUE}You said: {text}")

        # --- APP LAUNCHING ---
        if "open" in text:
            for app in self.APP_MAP:
                if app in text:
                    self.launch_app(app)
                    return True

        # --- WEB SEARCH ---
        if "search for" in text or "google" in text:
            # removing 'search for' or 'google' to get the query
            query = text.replace("search for", "").replace("google", "").strip()
            if query:
                self.speak(f"Searching for {query}")
                # Format the URL properly (replace spaces with +)
                url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                self.execute_adb(f"adb shell am start -a android.intent.action.VIEW -d \"{url}\"")
            return True

        # --- MEDIA CONTROLS ---
        if "volume up" in text:
            self.execute_adb("adb shell input keyevent 24")
            self.execute_adb("adb shell input keyevent 24")
        elif "volume down" in text:
            self.execute_adb("adb shell input keyevent 25")
            self.execute_adb("adb shell input keyevent 25")
        elif "play" in text or "pause" in text:
            self.speak("Toggling media")
            self.execute_adb("adb shell input keyevent 85") # KEYCODE_MEDIA_PLAY_PAUSE
        elif "next song" in text or "next track" in text:
            self.speak("Skipping track")
            self.execute_adb("adb shell input keyevent 87") # KEYCODE_MEDIA_NEXT
        elif "previous song" in text:
            self.execute_adb("adb shell input keyevent 88") # KEYCODE_MEDIA_PREVIOUS

        # --- SYSTEM CONTROLS ---
        elif "go home" in text:
            self.execute_adb("adb shell input keyevent 3")
        elif "back" in text:
            self.execute_adb("adb shell input keyevent 4")
        elif "power" in text and "menu" in text:
            self.execute_adb("adb shell input keyevent 5") # Opens power menu? (varies by device, sometimes calls)
        
        # --- PHONE & UTILS ---
        elif "dial" in text or "call" in text:
            # Extract numbers from string
            number = ''.join(filter(str.isdigit, text))
            if number:
                self.speak(f"Dialing {number}")
                self.execute_adb(f"adb shell am start -a android.intent.action.DIAL -d tel:{number}")
            else:
                self.speak("I didn't hear a number.")

        elif "take screenshot" in text:
            self.speak("Taking screenshot")
            filename = f"/sdcard/screenshot_{int(time.time())}.png"
            self.execute_adb(f"adb shell screencap -p {filename}")
            print(f"{Fore.GREEN}Saved to {filename}")

        elif "type" in text:
            msg = text.split("type", 1)[1].strip()
            if msg:
                self.speak("Typing")
                # Escape characters for shell
                formatted_msg = msg.replace(" ", "%s").replace("'", r"\'").replace('"', r'\"')
                self.execute_adb(f"adb shell input text \"{formatted_msg}\"")

        elif "stop" in text or "exit" in text or "shutdown" in text:
            self.speak("Goodbye!")
            return False

        return True

    def start_listening(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()

        self.speak("Listening for commands.")
        print(f"{Fore.GREEN}\nAssistant is listening... (Say 'Stop' to exit)")
        
        running = True
        while running:
            try:
                data = stream.read(4000, exception_on_overflow=False)
                if len(data) == 0:
                    break
                
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        running = self.process_command(text)
            except OSError:
                # Sometimes microphone buffer overflows, just ignore and continue
                continue

        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    try:
        assistant = ADBAssistant()
        assistant.start_listening()
    except KeyboardInterrupt:
        print(f"\n{Fore.MAGENTA}Force exit detected.")
