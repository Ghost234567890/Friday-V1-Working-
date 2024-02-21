import webbrowser
import sounddevice as sd
from gtts import gTTS
import subprocess
import requests
from PIL import Image
import io
import random
import datetime
import tempfile
import os
import speech_recognition as sr
import threading

WAKE_WORDS = ['daddy\'s home', 'time to wake up', 'time to go to work', 'friday']
SLEEP_WORDS = ['sleep', 'go to sleep', 'off']
sample_rate = 16000
audio_duration = 5
speaker_initialized = False
conversations = {}  # Dictionary to store ongoing conversations

# Jokes
jokes = [
    "Why don’t scientists trust atoms? Because they make up everything!",
    "Parallel lines have so much in common. It’s a shame they’ll never meet.",
    "What do you call someone with no body and no nose? Nobody knows.",
    "What did the janitor say when he jumped out of the closet? Supplies!",
    "Why was the math book sad? Because it had too many problems.",
    "Why don’t skeletons fight each other? They don’t have the guts.",
    "Why don’t scientists trust atoms? Because they make up everything!",
    "What do you call fake spaghetti? An impasta!",
    "Why did the tomato turn red? Because it saw the salad dressing!",
    "What do you call cheese that isn’t yours? Nacho cheese!",
    "What do you call an alligator in a vest? An in-vest-igator!",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "Why did the golfer bring two pairs of pants? In case he got a hole in one!",
    "What’s orange and sounds like a parrot? A carrot!",
    "Why was the broom late? It overswept!",
    "What do you call a bear with no teeth? A gummy bear!",
    "What do you call a fake noodle? An impasta!",
    "What do you call an alligator in a vest? An investigator!",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "Why was the math book sad? Because it had too many problems!"
]

def init_speaker():
    global speaker_initialized
    speaker_initialized = True

def play_audio(file_path):
    if not speaker_initialized:
        init_speaker()
    subprocess.run(["afplay", file_path])

def greet_based_on_time():
    current_time = datetime.datetime.now().hour
    if 5 <= current_time < 12:
        return 'Good morning, sir!'
    elif 12 <= current_time < 17:
        return 'Good afternoon, sir!'
    elif 17 <= current_time < 21:
        return 'Good evening, sir!'
    else:
        return 'Hello, sir!'

# Placeholder functions
def ask_how_are_you():
    return 'I am functioning optimally. Thank you for asking!'

def respond_to_joke():
    return random.choice(jokes)

def who_are_you():
    return "Hello, I'm your personal assistant. How may I assist you today?"

def suggest_place_to_go():
    places = ['local park', 'museum', 'shopping mall']
    return f"How about visiting the {random.choice(places)} today?"

def search_on_json_engine(query):
    # Replace 'YOUR_SEARCH_ENGINE_ID' and 'YOUR_API_KEY' with your actual values
    search_engine_id = '6000d18f0ae06416b'
    api_key = 'AIzaSyAUVgG_RAuPVdkhgH3uu3kLO_jJRJ6d-Zg'
    url = f'https://www.googleapis.com/customsearch/v1?q={query}&cx={search_engine_id}&key={api_key}'
    response = requests.get(url)
    results = response.json().get('items', [])
    return results

def search_and_display_images(query):
    # Replace 'YOUR_SEARCH_ENGINE_ID' and 'YOUR_API_KEY' with your actual values
    search_engine_id = '6000d18f0ae06416b'
    api_key = 'AIzaSyAUVgG_RAuPVdkhgH3uu3kLO_jJRJ6d-Zg'
    url = f'https://www.googleapis.com/customsearch/v1?q={query}&cx={search_engine_id}&key={api_key}&searchType=image'
    response = requests.get(url)
    results = response.json().get('items', [])

    if not results:
        return 'No images found.'

    for idx, result in enumerate(results[:3], 1):
        image_url = result.get('link')
        image_data = requests.get(image_url).content
        image = Image.open(io.BytesIO(image_data))
        image.show(title=f"Image {idx}")

    return 'Images displayed.'

# Define a global variable to indicate if speech is currently playing
speech_playing = False

def interrupt_speech():
    global speech_playing
    while True:
        if speech_playing:
            # Listen for user input while speech is playing
            user_input = recognize_speech()
            if user_input:
                # If user input is detected, stop speech playback
                subprocess.run(["pkill", "afplay"])
                speech_playing = False
                # Process the user input
                handle_conversation(user_input)
                # Exit the loop to stop listening for further user input
                break

def tts_response(response):
    # Save the response as a temporary audio file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    tts = gTTS(response)
    tts.save(temp_file.name)

    # Play the saved audio file
    play_audio(temp_file.name)

    # Start a new thread to listen for user input while speech is playing
    thread = threading.Thread(target=interrupt_speech)
    thread.start()

    # Set speech_playing to True to indicate that speech is currently playing
    global speech_playing
    speech_playing = True

    # Clean up the temporary file
    os.remove(temp_file.name)

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            print("Listening...")
            audio_data = recognizer.listen(source, timeout=5)
            print("Recognizing...")
            user_input = recognizer.recognize_google(audio_data)
            print("You said:", user_input)
            return user_input.lower()
        except sr.UnknownValueError:
            print("Didn't catch that. What's on your mind?")
            return ""

def listen_for_wake_word():
    print("Listening for wake word...")
    while True:
        user_input = recognize_speech()
        if user_input and any(word in user_input for word in WAKE_WORDS):
            print("Wake word detected! Now processing user command...")
            response = greet_based_on_time()
            tts_response(response)
            handle_conversation(user_input)
            break  # Exit the loop if a command was processed

def handle_conversation(user_input):
    global conversations
    context = conversations.get(user_input, None)

    while True:
        if context:
            print("User said:", user_input)
        else:
            print("Listening for user command...")
            user_input = recognize_speech()
            print("User said:", user_input)

        if any(word in user_input.lower() for word in SLEEP_WORDS):
            response = 'Going to sleep. Goodbye!'
            tts_response(response)
            exit()  # Exit the program if sleep command is heard

        if 'how are you' in user_input:
            response = ask_how_are_you()
        elif 'joke' in user_input:
            response = respond_to_joke()
        elif 'who are you' in user_input:
            response = who_are_you()
        elif 'go' in user_input:
            response = suggest_place_to_go()
        elif 'search for' in user_input:
            query = user_input.split('search for', 1)[1].strip()
            results = search_on_json_engine(query)
            response = f"Search results: {', '.join(result['title'] for result in results)}"
        elif 'show me' in user_input:
            query = user_input.split('show me', 1)[1].strip()
            response = search_and_display_images(query)
        elif 'play' in user_input.lower() and any(platform in user_input.lower() for platform in ['netflix', 'hulu', 'peacock', 'disney plus', 'hbo max', 'youtube']):
            platform = None
            query = None
            for p in ['netflix', 'hulu', 'peacock', 'disney plus', 'hbo max', 'youtube']:
                if p in user_input.lower():
                    platform = p
                    query = user_input.lower().split('play', 1)[1].replace(f'on {platform}', '').strip()
                    break
            if platform:
                globals()[f'search_on_{platform.replace(" ", "_")}(query)']
                response = f"Searching for '{query}' on {platform}."
            else:
                response = "I'm not sure which streaming service you want me to use."
        else:
            response = "I'm not sure how to respond to that. Ask me something else."

        print(response)
        tts_response(response)

if __name__ == "__main__":
    listen_for_wake_word()

