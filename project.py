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
import psutil

# Abstract class
class Command:
    def execute(self):
        pass

# Send WhatsApp message
class WhatsAppCommand(Command):
    def __init__(self, assistant):
        self.__assistant = assistant
        self.__assistant.speak("Please say the WhatsApp number including the country code.")
        number = self.__assistant.listen()
        message = ""
        self.invalid_number = False
        try:
            self.number = self.check_number(number)
        except ValueError as e:
            self.__assistant.speak(str(e))
            self.invalid_number = True
            return
        self.__assistant.speak("Please say the message you want to send.")
        message = self.__assistant.listen()
        self.message = message

    def check_number(self, number):
        number = number.replace(" ", "")
        if not number.startswith("+"):
            number = "+91" + number
        if not number[1:].isdigit():
            raise ValueError("Invalid phone number format. Please provide only digits after the country code.")
        if len(number) != 13:
            raise ValueError("Invalid phone number length. It should be 13 characters long including the '+'.")
        return number
    
    def execute(self):
        if self.invalid_number:
            return
        self.__assistant.speak("Sending message on WhatsApp...")
        current_time = time.localtime()
        minutes_to_send = current_time.tm_min + 2
        if minutes_to_send >= 60:
            minutes_to_send -= 60
            hours_to_send = (current_time.tm_hour + 1) % 24
        else:
            hours_to_send = current_time.tm_hour
        try:
            kit.sendwhatmsg(self.number, self.message, hours_to_send, minutes_to_send)
            self.__assistant.speak("Message sent successfully!")
        except Exception as e:
            self.__assistant.speak(f"An error occurred: {e}")
            return

# Time
class TimeCommand(Command):
    def __init__(self, assistant):
        self.__assistant = assistant

    def execute(self):
        current_time = datetime.datetime.now().strftime("%I:%M:%S")
        print("The current time is", current_time)
        self.__assistant.speak(f"The current time is {current_time}")

# Date 
class DateCommand(Command):
    def __init__(self, assistant):
        self.__assistant = assistant

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
        self.__assistant.speak(formatted_date)

# Search on wikipedia
class WikipediaCommand(Command):
    def __init__(self, assistant):
        self.__assistant = assistant

    def execute(self):
        self.__assistant.speak("What topic do you want to search for on Wikipedia?")
        query = self.__assistant.listen().strip().title()
        if not query:
            self.__assistant.speak("You didn't say any topic to search for. Please try again.")
            return
        try:
            print(f"Searching for '{query}' on Wikipedia. Please wait...")
            self.__assistant.speak(f"Searching for '{query}' on Wikipedia. Please wait...")
            summary = wikipedia.summary(query, sentences=4)
            print(f"Summary for '{query}':\n{summary}")
            self.__assistant.speak(f"Here is the summary for '{query}':")
            self.__assistant.speak(summary)
        except wikipedia.exceptions.DisambiguationError as e:
            self.__assistant.speak("The term is ambiguous. Here are some options:")
            print("Ambiguous options:", e.options)
            options = ', '.join(e.options[:5])
            self.__assistant.speak(f"You can choose one of these: {options}.")
        except wikipedia.exceptions.PageError:
            self.__assistant.speak("Sorry, I couldn't find any page matching your query on Wikipedia.")
        except Exception as e:
            self.__assistant.speak("An unexpected error occurred while fetching the Wikipedia summary.")
            print("Error:", e)

# Open a website
class OpenWebsiteCommand(Command):
    def __init__(self, assistant, site_name):
        self.__assistant = assistant
        self.site_name = site_name.strip().lower()

    def execute(self):
        urls = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "stack overflow": "https://stackoverflow.com",
            "iiitv-icd": "http://diu.iiitvadodara.ac.in/",
            "institute website": "http://diu.iiitvadodara.ac.in/",
            "moodle": "https://diumoodle.iiitvadodara.ac.in/",
            "chat gpt": "https://chat.openai.com/",
            "google classroom": "https://classroom.google.com/",
            "whatsapp" : "https://web.whatsapp.com/"
        }
        url = urls.get(self.site_name)
        if url:
            self.__assistant.speak(f"Opening {self.site_name}.")
            print(f"Opening {url}")
            wb.open(url)
        else:
            formatted_site_name = self.site_name.replace(" ", "")
            constructed_url = f"https://{formatted_site_name}.com"
            self.__assistant.speak(f"{self.site_name} is not in my known list. Attempting to open {constructed_url}.")
            print(f"Attempting to open {constructed_url}, please check your browser.")
            wb.open(constructed_url)

# Play music
class PlayMusicCommand(Command):
    def __init__(self, assistant):
        self.__assistant = assistant

    def execute(self):
        song_dir = os.path.expanduser("~\\Music\\ForZira")
        try:
            songs = os.listdir(song_dir)
            if not songs:
                self.__assistant.speak("The music folder is empty. Please add some songs.")
                return
        except FileNotFoundError:
            self.__assistant.speak("The music folder does not exist. Please create a folder named 'ForZira' in your Music directory.")
            return

        self.__assistant.speak("Please tell me the name of the song you want to play.")
        song_name = self.__assistant.listen()
        chosen_song = None
        for song in songs:
            if song_name.lower() in song.lower():
                chosen_song = song
                break

        if chosen_song:
            self.__assistant.speak(f"Playing {chosen_song}.")
        else:
            chosen_song = random.choice(songs)
            self.__assistant.speak(f"Could not find a song named {song_name}. Playing a random song instead.")
        song_path = os.path.join(song_dir, chosen_song)
        os.startfile(song_path)

        self.__assistant.speak("Enjoy the music! I'll wait for it to finish.")
        self.wait_for_music_to_end()
        self.__assistant.speak("The music has ended. Ready for the next command.")


    def wait_for_music_to_end(self):
        print("Waiting for the music to finish...")
        time.sleep(7)
        while self.is_music_app_running():
            time.sleep(2)

    def is_music_app_running(self):
        music_player_processes = ["microsoft.media.player.exe", "vlc.exe"]
        for process in psutil.process_iter(['name']):
            try:
                if process.info['name'] and any(player in process.info['name'].lower() for player in music_player_processes):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
             
# Take screenshots
class ScreenshotCommand(Command):
    def __init__(self, assistant):
        self.__assistant = assistant

    def execute(self):
        try:
            img = pyautogui.screenshot()
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")
            save_dir = os.path.expanduser("~\\Pictures")
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            img_path = os.path.join(save_dir, f"Screenshot {timestamp}.png")
            img.save(img_path)
            self.__assistant.speak("Screenshot taken successfully! It has been saved to your Pictures folder.")
            os.startfile(img_path)
        except Exception as e:
            print("Error:", e)
            self.__assistant.speak("Sorry, I was unable to take the screenshot due to an error.")

# Weather
class WeatherCommand(Command):
    def __init__(self, assistant, query):
        self.__assistant = assistant
        self.city = self.city_name(query)

    def city_name(self, query):
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
        try:
            response = requests.get(base_url)
            data = response.json()
            if data['cod'] == 200:
                weather_desc = data['weather'][0]['description'].capitalize()
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                humidity = data['main']['humidity']
                wind_speed = data['wind']['speed']
                print(f"\n--- Weather Report for {self.city.title()} ---")
                print(f"Description  : {weather_desc}")
                print(f"Temperature  : {temp}°C")
                print(f"Feels Like   : {feels_like}°C")
                print(f"Humidity     : {humidity}%")
                print(f"Wind Speed   : {wind_speed} m/s")
                print(f"------------------------------\n")
                self.__assistant.speak(
                    f"The current weather in {self.city.title()} is {weather_desc}. "
                    f"The temperature is {temp} degrees Celsius, but it feels like {feels_like} degrees. "
                    f"Humidity is at {humidity} percent, with wind speeds of {wind_speed} meters per second."
                )
            else:
                self.__assistant.speak(f"Sorry, I couldn't find the weather data for {self.city}.")
                print(f"Error: {data.get('message', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            self.__assistant.speak("There was a problem connecting to the weather service. Please check your internet connection.")
            print(f"Network Error: {e}")

# Tell a joke
class JokeCommand(Command):
    def __init__(self, assistant):
        self.__assistant = assistant

    def execute(self):
        try:
            response = requests.get("https://official-joke-api.appspot.com/random_joke")
            joke = response.json()
            print(f"Here's a joke: {joke['setup']} - {joke['punchline']}")
            self.__assistant.speak(f"Here's a joke: {joke['setup']} - {joke['punchline']}")
        except Exception as e:
            self.__assistant.speak("Sorry, I couldn't fetch a joke right now.")

# Riddle
class RiddleCommand(Command):
    def __init__(self, assistant):
        self.__assistant = assistant
        self.backup_riddles = {
            "What has keys but can't open locks?": "A Piano",
            "What comes once in a minute, twice in a moment, but never in a thousand years?": "Letter M",
            "I speak without a mouth and hear without ears. I have nobody, but I come alive with the wind. What am I?": "An echo"
        }

    def fetch_riddle(self):
        api_url = "https://riddles-api.vercel.app/random"
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                return data.get("riddle"), data.get("answer")
            else:
                print("Error fetching riddles from API:", response.status_code)
                return None
        except requests.exceptions.RequestException as e:
            print("Network error while fetching riddles:", e)
            return None

    def execute(self):
        riddle_data = self.fetch_riddle()
        if riddle_data:
            riddle, answer = riddle_data
        else:
            riddle, answer = random.choice(list(self.backup_riddles.items()))
        print(f"Riddle: {riddle}")
        self.__assistant.speak(f"Here's a riddle: {riddle}")
        print("Give the answer when ready.")
        self.__assistant.speak("Take your time to think about the answer.")
        answer_given = self.__assistant.listen()
        if answer_given.lower() == answer.lower():
            self.__assistant.speak("That's correct!")
        else:
            self.__assistant.speak(f"Oops! The correct answer was {answer}.")

# Log all commands executed
class Logger:
    def __init__(self, log_filename="logs.txt"):
        self.log_filename = log_filename
        timestamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        log_entry = "-"*16 + f"{timestamp} - Log Start" + "-"*16 + "\n"
        
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
        self.__assistant = assistant
        self.logger = Logger()

    def feature(self, query):
        query = query.lower()
        command = None

        if "who are you" in query or "who r u" in query:
            print(f"I'm {self.__assistant.name} and I'm a desktop voice assistant.")
            self.__assistant.speak(f"I'm {self.__assistant.name} and I'm a desktop voice assistant.")
            self.__assistant.speak("Here are some things I can do.")
            print("Tell date and time, search on Wikipedia, open websites, play music, take a screenshot, "
                  "jokes and riddles, or send a WhatsApp message.")
            self.__assistant.speak("I can tell you the date and time. "
                                   "search for a topic on Wikipedia. "
                                   "open a website. "
                                   "play some music. "
                                   "take a screenshot. "
                                   "tell you jokes and ask riddles. "
                                   "or send a WhatsApp message.")
        elif "how are you" in query or "how r u" in query:
            print("I'm fine! What about you?")
            self.__assistant.speak("Thank you for asking! I'm fine, What about you?")
        elif "not fine" in query or "not good" in query:
            print("I'm sorry to hear that.")
            self.__assistant.speak("I'm sorry to hear that. All days have their ups and downs. This too shall pass.")
        elif "fine" in query or "good" in query:
            print("Glad to hear that!")
            self.__assistant.speak("I'm glad to hear that!")
        elif "thanks" in query or "thank" in query:
            print("You're welcome!")
            self.__assistant.speak("You're most welcome! Anything else I can help you with?")
        elif "riddle" in query:
            command = RiddleCommand(self.__assistant)
        elif "joke" in query:
            command = JokeCommand(self.__assistant)
        elif "time" in query:
            command = TimeCommand(self.__assistant)
        elif "date" in query:
            command = DateCommand(self.__assistant)
        elif "weather" in query:
            command = WeatherCommand(self.__assistant, query)
        elif "wikipedia" in query or "information" in query:
            command = WikipediaCommand(self.__assistant)
        elif "open" in query:
            query_copy = query.replace("open ", "").strip().lower()
            command = OpenWebsiteCommand(self.__assistant, query_copy)
        elif "play" in query and "music" in query:
            command = PlayMusicCommand(self.__assistant)
        elif "screenshot" in query:
            command = ScreenshotCommand(self.__assistant)
        elif "message" in query or "whatsapp" in query:
            command = WhatsAppCommand(self.__assistant)
        elif "offline" in query or "exit" in query or "quit" in query or "end" in query or "stop" in query or "bye" in query:
            self.__assistant.speak("Going offline. Goodbye!")
            with open("logs.txt", "a") as log_file:
                log_file.write("-" * 63 + "\n\n")
            exit(1)
        else:
            self.__assistant.speak("I am not sure how to handle that request yet.")

        if command is not None:
            self.logger.log(query)
            command.execute()


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
        self.greet()
        while True:
            query = self.listen()
            if query:
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

    def listen(self):
        command = sr.Recognizer()
        with sr.Microphone() as source:
            #print("Adjusting for ambient noise, please wait...")
            command.adjust_for_ambient_noise(source)
            print("Listening...")
            command.pause_threshold = 1
            audio = command.listen(source)
        try:
            print("Recognizing...")
            query = command.recognize_google(audio, language="en-in")
            print("You:", query) 
        except Exception as e:
            print("Sorry, I didn't understand.")
            #self.speak("Sorry, I didn't understand.")
            return ""
        return query.lower()


if __name__ == "__main__":
    va = VoiceAssistant()
    va.run()
