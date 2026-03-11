import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser as wb
import os
import random
import pyautogui
import pywhatkit as kit
import time
import requests


# Abstract command interface
class Command:
    def execute(self):  #Virtual function
        pass

# Send WhatsApp message
class WhatsAppCommand(Command):
    def __init__(self, assistant):
        self.assistant = assistant
        # Prepend the India country code if not present
        self.assistant.speak("Please say the WhatsApp number including the country code.")
        number = self.assistant.listen()
        self.assistant.speak("Please say the message you want to send.")
        message = self.assistant.listen()
        
        if not number.startswith("+"):
            self.number = "+91" + number
        else:
            self.number = number
        self.message = message

    def execute(self):
        self.assistant.speak("Sending message on WhatsApp...")
        kit.sendwhatmsg_instantly(self.number, self.message, time.localtime().tm_hour, time.localtime().tm_min + 1)
        self.assistant.speak("Message sent successfully!")

# Time
class TimeCommand(Command):
    def __init__(self, assistant):
        self.assistant = assistant

    def execute(self):
        current_time = datetime.datetime.now().strftime("%I:%M:%S")
        print("The current time is", current_time)
        self.assistant.speak(f"The current time is {current_time}")

# Date 
class DateCommand(Command):
    def __init__(self, assistant):
        self.assistant = assistant

    def execute(self):
        now = datetime.datetime.now()
        day = now.day
        month = now.month
        month_name = now.strftime("%B")
        year = now.year

        if 11 <= day <= 13:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

        formatted_date = f"Today is the {day}{suffix} day of {month_name}, {year}."
        print(f"Today's date is {day}/{month}/{year}.")
        self.assistant.speak(formatted_date)

# Wikipedia search
class WikipediaCommand(Command):
    def __init__(self, assistant):
        self.assistant = assistant

    def execute(self):
        self.assistant.speak("What topic do you want to search for on Wikipedia?")
        query = self.assistant.listen()
        
        try:
            print(f"Searching for {query} on Wikipedia. Please wait...")
            self.assistant.speak(f"Searching for {query} on Wikipedia. Please wait...")
            summary = wikipedia.summary(query, sentences = 4)
            print(summary)
            self.assistant.speak(summary)
        except wikipedia.exceptions.DisambiguationError as e:
            self.assistant.speak("The term is ambiguous. Please choose a more specific topic.")
            print("Ambiguous options:", e.options)
        except wikipedia.exceptions.PageError:
            self.assistant.speak("Sorry, no matching page was found on Wikipedia.")
        except Exception as e:
            self.assistant.speak("An error occurred while fetching the summary.")
            print("Error:", e)


# Opening websites
class OpenWebsiteCommand(Command):
    def __init__(self, assistant, site_name):
        self.assistant = assistant
        self.site_name = site_name

    def execute(self):
        urls = {
            "youtube": "youtube.com",
            "google": "google.com",
            "stack overflow": "stackoverflow.com",
            "iiitv-icd": "http://diu.iiitvadodara.ac.in/",
            "diu moodle": "https://diumoodle.iiitvadodara.ac.in/",
            "chat GPT": "https://chatgpt.com/",
            "google classroom": "https://classroom.google.com/"
        }
        url = urls.get(self.site_name)
        if url:
            self.assistant.speak(f"Opening {self.site_name}")
            wb.open(url)
        else:
            try:
                self.assistant.speak(f"Opening {self.site_name} dot com")
                site_name = self.site_name + ".com"
                wb.open(site_name)
            except Exception as e:
                print("Error:", e)
                self.assistant.speak(f"Sorry, I couldn't find {self.site_name}.")

# Play music
class PlayMusicCommand(Command):
    def __init__(self, assistant):
        self.assistant = assistant

    def execute(self):
        song_dir = os.path.expanduser("~\\Music\\ForZira")
        songs = os.listdir(song_dir)
        
        self.assistant.speak("Please tell me the name of the song you want to play.")
        song_name = self.assistant.listen()
        chosen_song = None
        for song in songs:
            if song_name.lower() in song.lower():
                chosen_song = song
                break

        if chosen_song:
            self.assistant.speak(f"Playing {song_name}.")
        else:
            chosen_song = random.choice(songs)
            self.assistant.speak(f"Could not find {song_name}. Playing a random song instead.")

        song_path = os.path.join(song_dir, chosen_song)
        os.startfile(song_path)

        # Wait for the music application to close
        print("Waiting for the music to finish...")
        time.sleep(7)
        while True:
            if not self.is_music_app_running():
                break
            time.sleep(2)

        self.assistant.speak("Music has ended. Ready for the next command.")

    def is_music_app_running(self):
        import psutil
        music_player_processes = ["microsoft.media.player.exe"]
        for process in psutil.process_iter(['name']):
            try:
                process_name = process.info['name'].lower()
                if any(player in process_name for player in music_player_processes):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False
                

# Take screenshots
class ScreenshotCommand(Command):
    def __init__(self, assistant):
        self.assistant = assistant

    def execute(self):
        img = pyautogui.screenshot()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")
        img_path = os.path.expanduser(f"~\\Pictures\\Screenshot {timestamp}.png")
        img.save(img_path)
        self.assistant.speak("Screenshot taken and saved to your \'Pictures\' folder.")
        os.startfile(img_path)

# Weather
class WeatherCommand(Command):
    def __init__(self, assistant, query):
        self.assistant = assistant
        self.city = self.extract_city_name(query)

    def extract_city_name(self, query):
        # Find the keyword 'in' to isolate the city name
        words = query.split()
        if 'in' in words:
            city_index = words.index('in') + 1
            return ' '.join(words[city_index:])
        elif 'of' in words:
            city_index = words.index('of') + 1
            return ' '.join(words[city_index:])
        return words[-1]

    def execute(self):
        api_key = 'bef2557ec918dd24ee4a236cddc26ee3'
        base_url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={api_key}&units=metric"
        response = requests.get(base_url)
        data = response.json()

        if data['cod'] == 200:
            weather_desc = data['weather'][0]['description']
            temp = data['main']['temp']
            print(f"Weather in {self.city}: {weather_desc}, {temp}°C")
            self.assistant.speak(f"The weather in {self.city} is {weather_desc} with a temperature of {temp} degrees Celsius.")
        else:
            self.assistant.speak(f"Sorry, I couldn't find the weather data for {self.city}.")
            print("Error fetching weather data.")


# Tell a joke
class JokeCommand(Command):
    def __init__(self, assistant):
        self.assistant = assistant

    def execute(self):
        try:
            response = requests.get("https://official-joke-api.appspot.com/random_joke")
            joke = response.json()
            print(f"Here's a joke: {joke['setup']} - {joke['punchline']}")
            self.assistant.speak(f"Here's a joke: {joke['setup']} - {joke['punchline']}")
        except Exception as e:
            self.assistant.speak("Sorry, I couldn't fetch a joke right now.")

# Riddle
class RiddleCommand(Command):
    def __init__(self, assistant):
        self.assistant = assistant
        self.riddles = {
            "What has keys but can't open locks?": "A Piano",
            "What comes once in a minute, twice in a moment, but never in a thousand years?": "Letter M",
            "I speak without a mouth and hear without ears. I have nobody, but I come alive with the wind. What am I?": "An echo"
        }

    def execute(self):
        riddle, answer = random.choice(list(self.riddles.items()))
        print(f"Riddle: {riddle}")
        self.assistant.speak(f"Here's a riddle: {riddle}")
        print("Give the answer when ready.")
        self.assistant.speak("Take your time to think about the answer.")
        answer_given = self.assistant.listen()
        
        if answer_given.lower() == answer.lower():
            self.assistant.speak("That's correct!")
        else:
            self.assistant.speak(f"Oops! The correct answer was {answer}.")

# Log all commands executed
class Logger:
    def __init__(self, log_filename="logs.txt"):
        self.log_filename = log_filename
        timestamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        log_entry = "="*20 + f"{timestamp} - Log Start" + "="*20 + "\n"
        
        with open(self.log_filename, "a") as log_file:
            log_file.write(log_entry)
    
    def log(self, command):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} [Command] {command}\n"
        
        with open(self.log_filename, "a") as log_file:
            log_file.write(log_entry)

# Main Task Manager that uses commands
class TaskManager:
    def __init__(self, assistant):
        self.assistant = assistant
        self.logger = Logger()

    def feature(self, query):
        command = None

        if "who are you" in query or "who" in query:
            print(f"I'm {self.assistant.name} and I'm a desktop voice assistant.")
            self.assistant.speak(f"I'm {self.assistant.name} and I'm a desktop voice assistant.")
            self.assistant.speak("Here are some things I can do")
            print("Tell date and time, search on Wikipedia, open websites, play music, take a screenshot"
                  "or send a WhatsApp message")
            self.assistant.speak("I can tell you the date and time,"
                                 "search for a topic on Wikipedia,"
                                 "open a website,"
                                 "play some music,"
                                 "take a screenshot,"
                                 "or send a WhatsApp message.")

        elif "how are you" in query or "how" in query:
            print("I'm fine! What about you?")
            self.assistant.speak("Thank you for asking! I'm fine, What about you?")
        elif "not fine" in query or "not good" in query:
            print("I'm sorry to hear that.")
            self.assistant.speak("I'm sorry to hear that. All days have their ups and downs."
                                 " This too shall pass.")
        elif "fine" in query or "good" in query:
            print("Glad to hear that!")
            self.assistant.speak("I'm glad to hear that!")
        elif "thanks" in query or "thank" in query:
            print("You're welcome!")
            self.assistant.speak("You're most welcome! Anything else I can help you with?")
        elif "riddle" in query:
            command = RiddleCommand(self.assistant)
        elif "joke" in query:
            command = JokeCommand(self.assistant)
        elif "time" in query:
            command = TimeCommand(self.assistant)
        elif "date" in query:
            command = DateCommand(self.assistant)
        elif "weather" in query:
            command = WeatherCommand(self.assistant, query)
        elif "wikipedia" in query or "information" in query:
            command = WikipediaCommand(self.assistant)
        elif "open" in query:
            query = query.replace("open ", "").strip().lower()
            query = query.replace(" ", "")
            command = OpenWebsiteCommand(self.assistant, query)
        #elif "youtube" in query:
        #    command = OpenWebsiteCommand(self.assistant, "youtube")
        elif "google" in query:
            command = OpenWebsiteCommand(self.assistant, "google")
        elif "iiitv icd" in query or "institute website" in query:
            command = OpenWebsiteCommand(self.assistant, "iiitv-icd")
        elif "diu moodle" in query:
            command = OpenWebsiteCommand(self.assistant, "diu moodle")
        elif "stack overflow" in query:
            command = OpenWebsiteCommand(self.assistant, "stack overflow")
        elif "chat gpt" in query:
            command = OpenWebsiteCommand(self.assistant, "chat GPT")
        elif "classroom" in query:
            command = OpenWebsiteCommand(self.assistant, "google classroom")
        elif "play music" in query:
            command = PlayMusicCommand(self.assistant)
        elif "screenshot" in query:
            command = ScreenshotCommand(self.assistant)
        elif "message" in query or "whatsapp" in query:
            command = WhatsAppCommand(self.assistant)

        elif "offline" in query or "exit" in query or "quit" in query or "end" in query or "stop" in query:
            self.assistant.speak("Going offline. Goodbye!")
            quit()
        else:
            self.assistant.speak("I am not sure how to handle that request yet.")

        if command:
            command.execute()
            self.logger.log(query)


class VoiceAssistant:
    def __init__(self, name="Zira"):
        self.engine = pyttsx3.init()
        self.name = name
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "female" in voice.name.lower() or "zira" in voice.id.lower():
                self.engine.setProperty('voice', voice.id)
                break
        self.task_manager = TaskManager(self)

    def run(self):
        #if not self.login():
        #    return
        
        self.greet()
        while True:
            query = self.listen()
            self.task_manager.feature(query)

    def speak(self, audio):
        self.engine.say(audio)
        self.engine.runAndWait()

    def greet(self):
        hour: int = datetime.datetime.now().hour
        if 4 <= hour < 12:
            print("Good Morning!")
            self.speak("Good Morning!")
        elif 12 <= hour < 16:
            print("Good Afternoon!")
            self.speak("Good Afternoon!")
        elif 16 <= hour < 24:
            print("Good Evening!")
            self.speak("Good Evening!")
        print(f"{self.name} at your service! How may I help you today?")
        self.speak(f"{self.name} at your service! How may I help you today?")
        #self.speak(f"Welcome back! {self.name} at your service. Please tell me how may I help you.")
        #print(f"Welcome back! {self.name} at your service.")

    def listen(self):
        command = sr.Recognizer()
        with sr.Microphone() as source:
            #print("Adjusting for ambient noise, please wait...")
            #command.adjust_for_ambient_noise(source)
            print("Listening...")
            command.pause_threshold = 0.5
            audio = command.listen(source)
        try:
            print("Recognizing...")
            query = command.recognize_google(audio, language="en-in")
            print("You:", query) 
        except Exception as e:
            print("Sorry, I didn't understand.")
            self.speak("Sorry, I didn't understand.")
            return ""
        return query.lower()


if __name__ == "__main__":
    va = VoiceAssistant()
    va.run()
    with open("logs.txt", "a") as log_file:
            log_file.write("\n")
