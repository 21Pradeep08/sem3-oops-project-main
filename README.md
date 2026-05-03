# 🎙️ Jarvis – Python Voice Assistant

## Overview
Jarvis is a Python-based voice assistant that performs tasks using voice commands. It leverages speech recognition and text-to-speech technologies to interact with users and execute actions such as retrieving information, sending messages, and controlling system functions.

The system is designed with a modular architecture, making it easy to extend and integrate new features.

---

## Features

- 🎤 Voice command recognition  
- 🔊 Text-to-speech response system  
- 🔎 Wikipedia search and information retrieval  
- 💬 WhatsApp messaging automation  
- 🖥️ System control (open applications, files, etc.)  
- 🌐 Web browsing and search  
- ⏰ Time and date queries  
- 🧩 Modular design for scalability  

---

## Methodology

### 1. Speech Recognition
- Captures audio input from the microphone  
- Converts speech to text using SpeechRecognition library  

### 2. Command Processing
- Uses a command-dispatch system to interpret user input  
- Maps commands to specific functions/modules  

### 3. Task Execution
- Executes actions such as opening applications, searching Wikipedia, or sending messages  
- Uses external libraries (e.g., pywhatkit, webbrowser)  

### 4. Response Generation
- Converts text output into speech using pyttsx3  
- Provides real-time feedback to the user  

---

## Tech Stack

- Python  
- SpeechRecognition  
- pyttsx3 (Text-to-Speech)  
- pywhatkit (WhatsApp automation)  
- Wikipedia API  
- OS, webbrowser modules  

