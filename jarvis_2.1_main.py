import pyttsx3
import speech_recognition as sr
import datetime
import requests
import wikipedia
import webbrowser
import random
import pprint
import os
import subprocess
import pprint
import ollama
import cv2
from ultralytics import YOLO
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import time
import pyautogui
import screen_brightness_control as sbc
import psutil
import pvporcupine
import pyaudio
import struct
import speech_recognition as sr
from openai import OpenAI
from transformers import pipeline

# Initialize the pyttsx3 engine
engine = pyttsx3.init()

# Global conversation history
conversation_history = []

# Set up voice settings based on detected emotion
def setup_jarvis_voice(emotion="Neutral"):
    rate = {"Happy": 170, "Sad": 120, "Angry": 180, "Fear": 130, "Disgust": 140, "Surprise": 160, "Neutral": 150}
    volume = {"Happy": 1.0, "Sad": 0.8, "Angry": 1.0, "Fear": 0.9, "Disgust": 0.7, "Surprise": 1.0, "Neutral": 1.0}
    
    engine.setProperty('rate', rate.get(emotion, 150))
    engine.setProperty('volume', volume.get(emotion, 1.0))

# Speak function with emotional adjustments
def jarvis_speak(text, emotion="Neutral"):
    setup_jarvis_voice(emotion)
    print(f"Jarvis ({emotion}): {text}")
    engine.say(text)
    engine.runAndWait()

# Function to take voice input
def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)
    
    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language='en-in')
        print(f"User said: {query}")
        return query.lower()
    except Exception as e:
        print("Could not understand audio, please say that again.")
        return None


# Load emotion detection model
emotion_detector = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")

def detect_emotion(text):
    emotions = emotion_detector(text)
    detected_emotion = emotions[0]["label"] if emotions else "Neutral"
    
    # Map detected emotion to predefined categories
    emotion_mapping = {
        "joy": "Happy",
        "sadness": "Sad",
        "anger": "Angry",
        "fear": "Fear",
        "disgust": "Disgust",
        "surprise": "Surprise"
    }
    
    return emotion_mapping.get(detected_emotion, "Neutral")

# Function to tell the current time
def tell_time():
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    jarvis_speak(f"The current time is {current_time}")

# Function to tell the current date
def tell_date():
    today = datetime.datetime.now()
    jarvis_speak(f"Today is {today.strftime('%A')}, {today.strftime('%d %B %Y')}")

# Function to fetch weather information
def fetch_weather(city):
    api_key = ""  # Replace with your WeatherAPI key
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no"
    response = requests.get(url)
    weather_data = response.json()
    
    if "current" in weather_data:
        temperature = weather_data['current']['temp_c']
        feels_like = weather_data['current']['feelslike_c']
        description = weather_data['current']['condition']['text']
        
        weather_info = f"The temperature in {city} is {temperature}°C, feels like {feels_like}°C, with {description}."
        jarvis_speak(weather_info)
        print(f"City: {city}\nDescription: {description}\nTemperature: {temperature}°C\nFeels like: {feels_like}°C")
        
        return {
            "city": city,
            "description": description,
            "temperature": temperature,
            "feels_like": feels_like
        }
    else:
        error_message = "I could not retrieve the weather information."
        jarvis_speak(error_message)
        return {"error": error_message}

# Function to search Google
def google_search(query):
    jarvis_speak(f"Searching Google for {query}")
    webbrowser.open(f"https://www.google.com/search?q={query}")

# Function to search Wikipedia
def wikipedia_search(query):
    try:
        jarvis_speak(f"Searching Wikipedia for {query}")
        summary = wikipedia.summary(query, sentences=2)
        jarvis_speak(summary)
    except wikipedia.exceptions.DisambiguationError as e:
        jarvis_speak("There were too many results for this query. Please be more specific.")
    except wikipedia.exceptions.PageError:
        jarvis_speak("I'm sorry, I couldn't find any results for that query.")
        print("Page Error: No page found for this query.")
    except Exception as e:
        jarvis_speak("An error occurred while searching Wikipedia.")
        print(f"Unexpected error: {e}")

# Function to search YouTube
def youtube_search(query):
    jarvis_speak(f"Searching YouTube for {query}")
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")

# Function to tell a random joke
def get_random_jokes():
    try:
        headers = {'Accept': 'application/json'}
        response = requests.get("https://icanhazdadjoke.com/", headers=headers)
        response.raise_for_status() 
        joke_data = response.json()
        joke = joke_data.get("joke", "I couldn't fetch a joke at the moment.")
        
        jarvis_speak(joke)
        print(joke)
        return joke  
    except requests.exceptions.RequestException as e:
        error_message = "I couldn't fetch a joke at the moment. Please try again later."
        jarvis_speak(error_message)
        print(f"Error fetching joke: {e}")
        return error_message

# Function to give random advice
def get_random_advice():
    try:
        response = requests.get("https://api.adviceslip.com/advice")
        response.raise_for_status()  
        advice_data = response.json()
        advice = advice_data['slip']['advice'] 
        return advice
    except requests.exceptions.RequestException as e:
        print(f"Error fetching advice: {e}")
        return "Sorry, I couldn't fetch advice at the moment."


# Function to fetch news headlines
def fetch_news():
    url = "https://newsapi.org/v2/top-headlines?country=us&apiKey="  # Replace with your News API key
    response = requests.get(url)
    news_data = response.json()

    if news_data["status"] == "ok":
        articles = news_data["articles"][:5]  # Get top 5 news
        jarvis_speak("Here are the top news headlines:", "Neutral")

        for article in articles:
            headline = article["title"]
            emotion = detect_emotion(headline)

            # Modify response based on emotion
            if emotion == "Happy":
                response_text = "That's great news! " + headline
            elif emotion == "Sad":
                response_text = "This sounds unfortunate... " + headline
            elif emotion == "Angry":
                response_text = "That's frustrating! " + headline
            elif emotion == "Fear":
                response_text = "This seems concerning... " + headline
            elif emotion == "Disgust":
                response_text = "That's really unpleasant... " + headline
            elif emotion == "Surprise":
                response_text = "Wow! This is unexpected! " + headline
            else:
                response_text = headline  

            jarvis_speak(response_text, emotion)  

    else:
        jarvis_speak("I could not retrieve the news at the moment.", "Sad")


# jarvis chat function

def interact_with_jarvis(prompt):
    global conversation_history

    # Store user input in conversation history
    conversation_history.append({"role": "user", "content": prompt})

    # Define system message
    system_message = {
        "role": "system",
        "content": (
            "You are Jarvis, Tony Stark's AI assistant. Be smart, humorous, classy, and concise. No emojis, respond directly and avoid unnecessary descriptions. You also have emotions and learn from conversation history."
        )
    }

    # Combine system message with conversation history
    messages = [system_message] + conversation_history  

    try:
        response = ollama.chat(model="llama2:latest", messages=messages, stream=False)

        if "message" in response and "content" in response["message"]:
            response_text = response["message"]["content"]
        else:
            return "Error: Invalid response format from Ollama", "Neutral"

        emotion = detect_emotion(response_text)

        # Store assistant response in memory
        conversation_history.append({"role": "assistant", "content": response_text})

        # Modify response based on emotion
        emotion_responses = {
            "Happy": "Hehe! ",
            "Sad": "I understand, that sounds tough. ",
            "Angry": "Whoa! No need to get mad ",
            "Fear": "That sounds scary! ",
            "Disgust": "Ugh,  ",
            "Surprise": "Wow! ",
        }

        if emotion in emotion_responses:
            response_text = emotion_responses[emotion] + response_text

        return response_text, emotion

    except Exception as e:
        return f"Error connecting to Ollama: {e}", "Neutral"


# Object Detection

# Load the yolov8n model (pretrained)
model = YOLO("yolov8n.pt") 

# Start object detection using PC Webcam
def detect_objects_webcam():
    cap = cv2.VideoCapture(0)  # Open the default webcam (0)

    if not cap.isOpened():
        jarvis_speak("Error: Could not open webcam.")
        return

    jarvis_speak("Object detection activated. Press Q to exit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        # Run object detection on the frame
        results = model(frame)

        # Draw boxes & labels on the frame
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  
                class_id = int(box.cls[0])  
                confidence = box.conf[0].item()  
                label = result.names[class_id]  

                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} ({confidence:.2f})", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Announce detected object
                detected_text = f"I see a {label}."
                print(detected_text)
                jarvis_speak(detected_text)

        # Display the frame
        cv2.imshow("Jarvis Webcam Object Detection", frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            jarvis_speak("Exiting object detection mode.")
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

# Function to start object detection mode
def object_detection_mode():
    jarvis_speak("Activating object detection mode.")
    detect_objects_webcam()

# function to play music drom spotify

# Initialize Spotify API (Replace with your credentials)
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="",      # write your spotify client id
                                                   client_secret="",  # write your spotify client secret
                                                   redirect_uri="http://localhost:8888/callback",
                                                   scope="user-modify-playback-state user-read-playback-state"))
except Exception as e:
    print(f"Error: Unable to authenticate Spotify. Check your credentials. \n{e}")

#  Play a specific song with error handling
def play_music(song_name):
    try:
        results = sp.search(q=song_name, limit=1)
        if results["tracks"]["items"]:
            song_uri = results["tracks"]["items"][0]["uri"]
            sp.start_playback(uris=[song_uri])
            jarvis_speak(f"Playing {song_name}.")
        else:
            jarvis_speak(f"Song '{song_name}' not found on Spotify.")
    except spotipy.SpotifyException as e:
        jarvis_speak("Error: Unable to play the song. Check your Spotify connection.")
        print(f"Spotify API Error: {e}")
    except Exception as e:
        jarvis_speak("An unexpected error occurred.")
        print(f"Unexpected Error: {e}")

#  Pause playback with error handling
def pause_music():
    try:
        current_playback = sp.current_playback()
        if current_playback and current_playback["is_playing"]:
            sp.pause_playback()
            jarvis_speak("Music paused.")
        else:
            jarvis_speak("No music is currently playing.")
    except spotipy.SpotifyException as e:
        jarvis_speak("Error: Unable to pause music.")
        print(f"Spotify API Error: {e}")
    except Exception as e:
        jarvis_speak("An unexpected error occurred.")
        print(f"Unexpected Error: {e}")

#  Resume playback with error handling
def resume_music():
    try:
        current_playback = sp.current_playback()
        if current_playback and not current_playback["is_playing"]:
            sp.start_playback()
            jarvis_speak("Resuming music.")
        else:
            jarvis_speak("Music is already playing.")
    except spotipy.SpotifyException as e:
        jarvis_speak("Error: Unable to resume music.")
        print(f"Spotify API Error: {e}")
    except Exception as e:
        jarvis_speak("An unexpected error occurred.")
        print(f"Unexpected Error: {e}")

#  Skip to the next song with error handling
def next_song():
    try:
        sp.next_track()
        jarvis_speak("Skipping to the next song.")
    except spotipy.SpotifyException as e:
        jarvis_speak("Error: Unable to skip the song.")
        print(f"Spotify API Error: {e}")
    except Exception as e:
        jarvis_speak("An unexpected error occurred.")
        print(f"Unexpected Error: {e}")

#  Stop playback with error handling
def stop_music():
    try:
        current_playback = sp.current_playback()
        if current_playback and current_playback["is_playing"]:
            sp.pause_playback()
            jarvis_speak("Stopping music.")
        else:
            jarvis_speak("No music is currently playing.")
    except spotipy.SpotifyException as e:
        jarvis_speak("Error: Unable to stop music.")
        print(f"Spotify API Error: {e}")
    except Exception as e:
        jarvis_speak("An unexpected error occurred.")
        print(f"Unexpected Error: {e}")


#  Play a specific playlist with error handling
def play_playlist(playlist_name):
    try:
        results = sp.search(q=playlist_name, type="playlist", limit=1)
        if results["playlists"]["items"]:
            playlist_uri = results["playlists"]["items"][0]["uri"]
            sp.start_playback(context_uri=playlist_uri)
            jarvis_speak(f"Playing playlist {playlist_name}.")
        else:
            jarvis_speak(f"Playlist '{playlist_name}' not found on Spotify.")
    except spotipy.SpotifyException as e:
        jarvis_speak("Error: Unable to play the playlist.")
        print(f"Spotify API Error: {e}")
    except Exception as e:
        jarvis_speak("An unexpected error occurred.")
        print(f"Unexpected Error: {e}")


# Offline mode functions


def get_all_drives():
    """Detect all available drives on the system."""
    return [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]

def find_exe(app_name):
    """Search all drives for the application executable file."""
    drives = get_all_drives()
    print(f"Searching for {app_name}.exe in {drives}...")

    for drive in drives:
        for root, _, files in os.walk(drive):
            for file in files:
                if file.lower() == f"{app_name.lower()}.exe":
                    return os.path.join(root, file)  
    return None  

def open_app(app_name):
    """Search for the app and open it."""
    exe_path = find_exe(app_name)
    if exe_path:
        os.startfile(exe_path)
        print(f"Opening {app_name} from {exe_path}...")
    else:
        print(f"{app_name} not found on this system.")

def close_app(app_name):
    """Close the app by its executable name."""
    os.system(f'taskkill /f /im {app_name}.exe')
    print(f"Closing {app_name}...")

def open_telegram():
    open_app("telegram")

def close_telegram():
    close_app("telegram")

def open_discord():
    open_app("discord")

def close_discord():
    close_app("discord")

def open_cmd():
    os.system('start cmd')

def close_cmd():
    close_app("cmd")

# Volume up And Volume Down Feature 

def get_volume_control():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return interface.QueryInterface(IAudioEndpointVolume)

# Function to increase volume
def volume_up(step=0.1):
    try:
        volume = get_volume_control()
        current_volume = volume.GetMasterVolumeLevelScalar()
        new_volume = min(1.0, current_volume + step)  # Ensure it doesn't go above 1.0
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        jarvis_speak(f"Volume increased to {int(new_volume * 100)}%.")
    except Exception as e:
        jarvis_speak("I couldn't adjust the volume.")
        print(f"Error: {e}")

# Function to decrease volume
def volume_down(step=0.1):
    try:
        volume = get_volume_control()
        current_volume = volume.GetMasterVolumeLevelScalar()
        new_volume = max(0.0, current_volume - step)  # Ensure it doesn't go below 0.0
        volume.SetMasterVolumeLevelScalar(new_volume, None)
        jarvis_speak(f"Volume decreased to {int(new_volume * 100)}%.")
    except Exception as e:
        jarvis_speak("I couldn't adjust the volume.")
        print(f"Error: {e}")

#Function to Control Screen Brightness

# Function to increase brightness
def brightness_up(step=10):
    try:
        current_brightness = sbc.get_brightness(display=0)[0] 
        new_brightness = min(100, current_brightness + step)  # Ensure it doesn't exceed 100
        sbc.set_brightness(new_brightness, display=0)  
        jarvis_speak(f"Brightness increased to {new_brightness} percent.")
    except Exception as e:
        jarvis_speak("I couldn't adjust the brightness.")
        print(f"Error: {e}")

# Function to decrease brightness
def brightness_down(step=10):
    try:
        current_brightness = sbc.get_brightness(display=0)[0]  
        new_brightness = max(0, current_brightness - step)  # Ensure it doesn't go below 0
        sbc.set_brightness(new_brightness, display=0) 
        jarvis_speak(f"Brightness decreased to {new_brightness} percent.")
    except Exception as e:
        jarvis_speak("I couldn't adjust the brightness.")
        print(f"Error: {e}")


# function to open task manager

def open_task_manager():
    """Opens Task Manager without blocking other commands."""
    try:
        subprocess.Popen("taskmgr.exe", shell=True)  
        print("Task Manager opened.")
    except Exception as e:
        print(f"Error opening Task Manager: {e}")


# Open notepad function to take notes

notes_file = os.path.join(os.path.expanduser("~"), "Desktop", "My Notes.txt")

def take_notes():
    jarvis_speak("Opening Notepad. Start dictating your notes, sir.", "Neutral")
    
    # Open Notepad
    subprocess.Popen("notepad.exe")
    time.sleep(2)  

    notes = []  # Store notes in a list before saving

    while True:
        jarvis_speak("I'm listening... Say 'stop taking notes' to finish.", "Neutral")
        note = take_command()
        
        if note:
            if "stop taking notes" in note:
                jarvis_speak("Saving your notes and closing Notepad.", "Neutral")
                pyautogui.hotkey("ctrl", "s")  
                time.sleep(1)
                pyautogui.press("enter")
                time.sleep(1)
                pyautogui.hotkey("alt", "f4")  
                
                # Save notes to a file
                with open(notes_file, "w") as file:
                    file.writelines("\n".join(notes) + "\n")

                break
            else:
                emotion = detect_emotion(note)
                jarvis_speak(f"Noted: {note}", emotion)
                pyautogui.write(note)  
                pyautogui.press("enter")
                notes.append(note)  

# Reminding my save notes function

def remind_notes():
    try:
        with open(notes_file, "r") as file:
            saved_notes = file.readlines()

        if saved_notes:
            jarvis_speak("Here are your saved notes, sir:", "Neutral")
            for note in saved_notes:
                jarvis_speak(note.strip(), detect_emotion(note))
        else:
            jarvis_speak("You have no saved notes, sir.", "Neutral")
    
    except FileNotFoundError:
        jarvis_speak("No notes found, sir. Try saving some first!", "Neutral")

def delete_notes():
    """Deletes the notes file after Jarvis exits"""
    if os.path.exists(notes_file):
        os.remove(notes_file)
        print("Notes file deleted successfully.")


# function to open and search file 

def get_all_drives():
    """Detect all available drives on the system."""
    return [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]

def search_and_open_file(filename):
    """Search for a file across all drives and open it."""
    drives = get_all_drives()
    print(f"Searching for '{filename}' in: {drives}...")

    for drive in drives:  
        for root, _, files in os.walk(drive):  
            for file in files:
                if filename.lower() in file.lower():  
                    file_path = os.path.join(root, file)

                    try:
                        subprocess.run(["start", "", file_path], shell=True) 
                        print(f"Opening: {file_path}")
                        return file_path
                    except Exception as e:
                        print(f"Error opening file: {e}")
                        return None

    print("File not found.")
    return None

# funciotn to close file ( say file name it will iterate through task manager and kill the task sometime check the name of the file in taskmanager )

def close_file(file_name):
    """Closes a file if it is currently open."""
    try:
        file_name = file_name.lower()  

        for process in psutil.process_iter(attrs=['pid', 'name']):
            try:
                process_files = process.open_files()
                for f in process_files:
                    if file_name in f.path.lower():
                        print(f"Closing {f.path} (PID: {process.pid})")
                        process.terminate()  
                        process.wait(timeout=5)  
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue  

        print("File not found or not open.")
        return False

    except Exception as e:
        print(f"Error closing file: {e}")
        return False

# function to open and search folders

def search_and_open_folder(folder_name):
    """Search for a folder across all drives and open it."""
    drives = get_all_drives()
    print(f"Searching for folder '{folder_name}' in: {drives}...")

    for drive in drives:  
        for root, dirs, _ in os.walk(drive):  
            for dir_name in dirs:
                if folder_name.lower() in dir_name.lower():  
                    folder_path = os.path.join(root, dir_name)

                    try:
                        subprocess.run(["explorer", folder_path], shell=True)  
                        print(f"Opening: {folder_path}")
                        return folder_path
                    except Exception as e:
                        print(f"Error opening folder: {e}")
                        return None

    print("Folder not found.")
    return None


# Main function to run the assistant
def run_jarvis():

    global conversation_history

    # Reset conversation history at the start
    conversation_history = []

    jarvis_speak("Welcome Back Sir, All system for gaming will be prepared in a few minutes, for now grab a cup of coffee and have a good day .")
    while True:
        query = take_command()

        if query:
            if "time" in query:
                tell_time()
            elif "date" in query:
                tell_date()

            elif 'open discord' in query:
               open_discord()

            elif 'close discord'in query:
                close_discord()
            
            elif 'open telegram' in query:
                open_telegram()
            
            elif 'close telegram' in query:
                close_telegram()

            elif 'open command prompt' in query or 'open cmd' in query:
                open_cmd()

            elif ' close command prompt' in query or 'close cmd' in query:
                close_cmd()

            elif "volume up" in query:
                volume_up()
    
            elif "volume down" in query:
                volume_down()

            elif "brightness up" in query:
                brightness_up()

            elif "brightness down" in query:
                brightness_down()

            elif "open task manager" in query:
                jarvis_speak("Opening Task Manager, sir.")
                open_task_manager()

            elif "take notes" in query or "open notepad" in query:
                take_notes()   

            elif "remind me of my notes" in query:
                remind_notes()  

            elif "open file" in query:
                jarvis_speak("Please say the name of the file you want to open.")
                file_name = take_command()
                if file_name:
                    search_and_open_file(file_name)  

            elif "close file" in query:
                jarvis_speak("Please say the name of the file you want to close.")
                file_name = take_command()
                if file_name:
                    close_file(file_name)

            elif "open folder" in query: 
                jarvis_speak("Please tell me the folder name you want to open.", "Neutral")
                folder_name = take_command()
                if folder_name:
                    search_and_open_folder(folder_name) 

            elif "conversation" in query or "let's chat" in query:
                jarvis_speak("Let's have a chat, sir. What would you like to discuss?")
                while True:
                    user_input = take_command()
                    if user_input:
                        if "exit" in user_input or "stop" in user_input:
                            jarvis_speak("Goodbye, sir.", "Neutral")
                            break
                        
                        ai_response, emotion = interact_with_jarvis(user_input)

                        jarvis_speak(ai_response, emotion)
                    else:
                        jarvis_speak("I didn't catch that. Could you please repeat?", "Neutral")
                else:
                    response, emotion = interact_with_jarvis(query)
                    jarvis_speak(response, emotion)

            elif "identify objects" in query or "object detection" in query:
                object_detection_mode()

            elif "play music" in query:
                song_name = query.replace("play song", "").strip()
                play_music(song_name)
            elif "pause" in query:
                pause_music()
            elif "resume" in query:
                resume_music()
            elif "next" in query:
                next_song()
            elif "play playlist" in query:
                playlist_name = query.replace("play playlist", "").strip()
                play_playlist(playlist_name)
            elif "stop" in query:
                stop_music()

            elif "weather" in query:
                 jarvis_speak("Which city's weather would you like to search for?")
                 city = take_command()
                 if city:
                    weather_info = fetch_weather(city)
                    if "error" not in weather_info:
                        jarvis_speak(f"For your convenience, I am printing it on the screen.")
                    else:
                        jarvis_speak(weather_info["error"])

            elif "google" in query:
                jarvis_speak("What would you like to search on Google?")
                search_query = take_command()
                if search_query:
                    google_search(search_query)

            elif "wikipedia" in query:
                jarvis_speak("What would you like to search on Wikipedia?")
                search_query = take_command()
                if search_query:
                    wikipedia_search(search_query)

            elif "youtube" in query:
                jarvis_speak("What would you like to search on YouTube?")
                search_query = take_command()
                if search_query:
                    youtube_search(search_query)

            elif "advice" in query:
                jarvis_speak("Here's an advice for you, sir")
                advice = get_random_advice()
                jarvis_speak(advice)  
                jarvis_speak("For your convenience, I am printing it on the screen, sir.")
                print(advice)  

            elif 'joke' in query:
                jarvis_speak("Hope you like this one sir")
                joke = get_random_jokes()
                jarvis_speak(joke)
                jarvis_speak("For your convenience, I am printing it on the screen sir.")
                pprint.pprint(joke)

            elif "news" in query:
                fetch_news()

            elif "exit" in query or "stop" in query:
                jarvis_speak("Goodbye, sir.")
                delete_notes()
                break
            else:
                jarvis_speak("I'm sorry, I did not understand the command.")

# wake up voice detectation

# add your real access key which you will get from Picovoice 
access_key = ""

# Initialize Porcupine with the access key and the wake word
porcupine = pvporcupine.create(access_key=access_key, keywords=["terminator", "jarvis"])  # Change wake words as desired

pa = pyaudio.PyAudio()
audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

def listen_for_wake_word():
    print("Listening for wake word...")

    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        keyword_index = porcupine.process(pcm)
        if keyword_index >= 0:
            print("Wake word detected!")
            execute_command()
            break

def execute_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print(f"Command received: {command}")
    except sr.UnknownValueError:
        print("Could not understand the command.")
    except sr.RequestError as e:
        print(f"Error with the service; {e}")

try:
    listen_for_wake_word()
except KeyboardInterrupt:
    print("Program terminated.")
finally:
    audio_stream.stop_stream()
    audio_stream.close()
    pa.terminate()
    porcupine.delete()

# Run the Jarvis 
run_jarvis()
