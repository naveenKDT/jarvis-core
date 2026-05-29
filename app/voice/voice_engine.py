import speech_recognition as sr
import pyttsx3

from app.core.brain import JarvisBrain


class JarvisVoiceAgent:

    def __init__(self):

        self.recognizer = sr.Recognizer()

        self.microphone = sr.Microphone()

        self.engine = pyttsx3.init()

        self.brain = JarvisBrain()

        self.setup_voice()

    def setup_voice(self):

        voices = self.engine.getProperty("voices")

        if voices:
            self.engine.setProperty("voice", voices[0].id)

        self.engine.setProperty("rate", 175)

        self.engine.setProperty("volume", 1)

    def speak(self, text):

        print(f"\nJARVIS: {text}\n")

        self.engine.say(text)

        self.engine.runAndWait()

    async def process_command(self, command):

        result = await self.brain.think(command)

        response = result["response"]

        self.speak(response)

    async def listen(self):

        with self.microphone as source:

            print("Listening...")

            self.recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            audio = self.recognizer.listen(source)

        try:

            command = self.recognizer.recognize_google(audio)

            print(f"\nYOU: {command}\n")

            await self.process_command(command)

        except sr.UnknownValueError:

            self.speak("I did not understand that.")

        except Exception as ex:

            print(ex)

            self.speak("An error occurred.")

    async def start(self):

        self.speak("Jarvis online.")

        while True:

            await self.listen()