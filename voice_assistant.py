"""
Voice Assistant - OASIS INFOBYTE Python Programming Internship (Task 1)
-----------------------------------------------------------------------
A clean, beginner-friendly Python Voice Assistant that listens to spoken 
commands and performs actions such as greetings, telling the time/date, 
performing web searches, and graceful program exit.

Technologies Used:
- speech_recognition: Captures microphone audio & converts speech to text.
- pyttsx3: Offline Text-to-Speech synthesis.
- datetime: Fetches current system time and date.
- webbrowser: Opens default browser for web searches.
"""

import datetime
import sys
import urllib.parse
import webbrowser
import speech_recognition as sr
import pyttsx3


def initialize_tts_engine() -> pyttsx3.Engine:
    """
    Initialize and configure the pyttsx3 Text-to-Speech engine.
    
    Returns:
        pyttsx3.Engine: Configured TTS engine instance instance.
    """
    try:
        engine = pyttsx3.init()
        # Set speaking rate (words per minute)
        engine.setProperty('rate', 160)
        # Set volume level (0.0 to 1.0)
        engine.setProperty('volume', 1.0)
        return engine
    except Exception as e:
        print(f"Warning: Could not initialize text-to-speech engine: {e}")
        return None


# Global TTS engine instance
engine = initialize_tts_engine()


def speak(text: str) -> None:
    """
    Prints response text to terminal and speaks it aloud using pyttsx3.
    
    Args:
        text (str): The message to print and speak.
    """
    print(f"Assistant: {text}")
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"[Speech Output Error: {e}]")


def listen_command() -> str:
    """
    Captures voice input from the microphone and converts it to text using speech_recognition.
    Handles microphone and recognition errors gracefully.
    
    Returns:
        str: Recognized command string in lowercase, or empty string if failed.
    """
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("\nListening...")
            # Adjust for ambient noise for better recognition accuracy
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            # Listen for user command with a 5-second timeout
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            
    except OSError:
        speak("Microphone is unavailable or not detected. Please check your audio settings.")
        return ""
    except sr.WaitTimeoutError:
        # User was silent or didn't speak in time
        return ""
    except Exception as e:
        speak("An error occurred while accessing the microphone.")
        print(f"[Microphone Error Details: {e}]")
        return ""

    # Convert captured speech to text using Google Speech Recognition API
    try:
        print("Recognizing...")
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")
        return command.lower().strip()
    except sr.UnknownValueError:
        speak("Sorry, I didn't understand that. Please try again.")
        return ""
    except sr.RequestError:
        speak("Sorry, the speech recognition service is currently unavailable. Please check your internet connection.")
        return ""
    except Exception as e:
        speak("An unexpected error occurred during speech recognition.")
        print(f"[Recognition Error Details: {e}]")
        return ""


def handle_greeting() -> None:
    """Responds to user greetings with a friendly spoken message."""
    greeting_response = "Hello! How can I help you today?"
    speak(greeting_response)


def handle_time() -> None:
    """Fetches current system time and speaks it clearly."""
    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M %p")  # Example: 10:28 AM
    speak(f"The current time is {current_time}.")


def handle_date() -> None:
    """Fetches current system date and speaks it clearly."""
    now = datetime.datetime.now()
    current_date = now.strftime("%B %d, %Y")  # Example: August 09, 2026
    day_name = now.strftime("%A")             # Example: Sunday
    speak(f"Today is {day_name}, {current_date}.")


def handle_web_search(command: str) -> None:
    """
    Extracts search query from user command and opens default browser with Google search.
    
    Args:
        command (str): Full recognized command string.
    """
    # Extract search topic by removing trigger keywords
    query = command
    for prefix in ["search for", "search about", "search"]:
        if query.startswith(prefix):
            query = query[len(prefix):].strip()
            break
            
    if not query:
        speak("What would you like me to search for?")
        query = listen_command()
        
    if query:
        speak(f"Searching the web for '{query}'...")
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        webbrowser.open(search_url)
    else:
        speak("No search topic provided.")


def process_command(command: str) -> bool:
    """
    Parses and executes the appropriate action for the user's command.
    
    Args:
        command (str): The recognized input command text.
        
    Returns:
        bool: True if assistant should keep running, False if exit requested.
    """
    if not command:
        # Empty command (timeout or unrecognized speech already handled)
        return True

    # 1. Exit Commands
    if any(word in command for word in ["exit", "quit", "goodbye", "bye", "stop"]):
        speak("Goodbye! Have a great day.")
        return False

    # 2. Greeting Commands
    elif any(word in command for word in ["hello", "hi", "hey"]):
        handle_greeting()

    # 3. Current Time Commands
    elif "time" in command:
        handle_time()

    # 4. Current Date Commands
    elif "date" in command or "today" in command:
        handle_date()

    # 5. Web Search Commands
    elif "search" in command:
        handle_web_search(command)

    # 6. Unsupported / Unknown Commands
    else:
        speak("Sorry, I didn't recognize that command. You can ask for the time, date, web search, or say hello.")

    return True


def main() -> None:
    """Main execution loop for the Voice Assistant."""
    print("=" * 60)
    print("               OASIS INFOBYTE VOICE ASSISTANT               ")
    print("=" * 60)
    
    speak("Voice Assistant started. Say something...")
    
    running = True
    while running:
        try:
            command = listen_command()
            running = process_command(command)
        except KeyboardInterrupt:
            print("\nProgram interrupted by user.")
            speak("Goodbye!")
            break
        except Exception as e:
            print(f"An unexpected error occurred in main loop: {e}")
            speak("An unexpected error occurred. Restarting command loop.")


if __name__ == "__main__":
    main()
