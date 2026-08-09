# OASIS INFOBYTE — Python Voice Assistant

## Project Overview

This project is a simple Python Voice Assistant developed as part of the **OASIS INFOBYTE Python Programming Internship**.

The idea behind the project is to create a small voice-controlled application that can listen to the user's commands through a microphone, convert the speech into text, perform a specific action, and respond using both text and speech.

The assistant is designed as a beginner-friendly project and focuses on basic Python programming, speech recognition, text-to-speech, and simple browser automation.

## What the Assistant Can Do

The current version of the assistant supports the following commands:

* Responds to greetings such as `hello`, `hi`, and `hey`.
* Tells the current system time.
* Tells the current date and day.
* Searches the web using Google through the default browser.
* Responds to unsupported commands.
* Exits when the user says `exit`, `quit`, `goodbye`, `bye`, or `stop`.
* Handles common microphone and speech recognition errors.

## How It Works

The assistant follows a simple process:

1. It starts the text-to-speech engine.
2. It listens to the user's voice through the microphone.
3. Ambient noise is adjusted before recording.
4. The recorded audio is sent to Google's speech recognition service.
5. The recognized text is converted to lowercase.
6. The command is checked to determine what action should be performed.
7. The assistant performs the requested action.
8. The response is printed in the terminal and spoken aloud.
9. The process continues until the user asks the assistant to exit.

## Technologies Used

The project uses the following Python libraries:

* **Python** — Main programming language.
* **SpeechRecognition** — Captures audio from the microphone and converts speech into text.
* **PyAudio** — Provides microphone access through `SpeechRecognition`.
* **pyttsx3** — Converts the assistant's responses into spoken audio.
* **datetime** — Retrieves the current time and date.
* **urllib.parse** — Encodes search queries for use in URLs.
* **webbrowser** — Opens Google search results in the default browser.
* **sys** — Included as part of the Python project imports.

## Project Structure

```text
Python-Task1-VoiceAssistant/
│
├── voice_assistant.py
├── requirements.txt
├── README.md
└── screenshots/
```

## Installation

### 1. Install Python

Make sure Python 3 is installed on your computer.

You can check the installed version by running:

```bash
python --version
```

### 2. Install the Required Libraries

From the project directory, install the required packages with:

```bash
python -m pip install -r requirements.txt
```

The main packages required by the application are:

```text
SpeechRecognition
PyAudio
pyttsx3
```

`datetime`, `urllib.parse`, `webbrowser`, and `sys` are part of Python's standard library and do not need to be installed separately.

### 3. Microphone

The application requires a working microphone.

If the microphone is not detected, check your Windows audio settings and make sure Python or your terminal application has permission to access the microphone.

## Running the Assistant

After installing the required dependencies, run:

```bash
python voice_assistant.py
```

The program will display:

```text
============================================================
               OASIS INFOBYTE VOICE ASSISTANT
============================================================
```

It will then start listening for commands.

## Supported Commands

### Greetings

The assistant recognizes:

```text
Hello
Hi
Hey
```

Example:

```text
You said: hello
Assistant: Hello! How can I help you today?
```

### Time

You can ask questions containing the word `time`, for example:

```text
What is the time?
What time is it?
What is the time now?
```

Example response:

```text
Assistant: The current time is 11:39 AM.
```

### Date

The assistant can respond to commands containing `date` or `today`.

Examples:

```text
What is the date?
What is today's date?
What is the date today?
```

Example response:

```text
Assistant: Today is Sunday, August 09, 2026.
```

### Web Search

The assistant supports commands beginning with:

```text
Search
Search for
Search about
```

For example:

```text
Search for Python tutorials
Search about machine learning
Search Python
```

The assistant extracts the search topic, creates a Google search URL, and opens it using the computer's default web browser.

Example:

```text
You said: search for Python tutorial
Assistant: Searching the web for 'python tutorial'...
```

### Exit

The assistant can be stopped using any of the following commands:

```text
Exit
Quit
Goodbye
Bye
Stop
```

The assistant responds:

```text
Assistant: Goodbye! Have a great day.
```

## Speech Recognition

The project uses the `SpeechRecognition` library to process voice input.

Before listening, the assistant adjusts for ambient noise for a short period to help improve recognition.

The recorded speech is then processed using:

```python
recognizer.recognize_google(audio)
```

This means that an internet connection is required when converting the recorded speech into text using Google's speech recognition service.

## Text-to-Speech

The assistant uses `pyttsx3` to speak its responses.

The speech engine is configured with:

* A speaking rate of **160 words per minute**.
* A volume level of **1.0**.

The assistant also prints every response to the terminal, so the user can see what it is saying.

## Error Handling

The application includes basic error handling to make the assistant continue running when common problems occur.

### Microphone Errors

If the microphone is unavailable or cannot be accessed, the assistant displays an appropriate message instead of immediately crashing.

For example:

```text
Assistant: Microphone is unavailable or not detected. Please check your audio settings.
```

### Unrecognized Speech

If the speech recognition service cannot understand the recorded audio:

```text
Assistant: Sorry, I didn't understand that. Please try again.
```

### Speech Recognition Service Error

If the speech recognition service cannot be reached, the assistant informs the user that the service may be unavailable or that an internet connection should be checked.

### Unsupported Commands

If the assistant receives a command that is not currently supported, it responds with:

```text
Assistant: Sorry, I didn't recognize that command. You can ask for the time, date, web search, or say hello.
```

### Keyboard Interrupt

The user can also stop the application manually with `Ctrl + C`. The program handles the interruption and exits with a goodbye message.

## Example Run

A typical session may look like this:

```text
============================================================
               OASIS INFOBYTE VOICE ASSISTANT
============================================================

Assistant: Voice Assistant started. Say something...

Listening...
Recognizing...
You said: hello
Assistant: Hello! How can I help you today?

Listening...
Recognizing...
You said: what is the time now
Assistant: The current time is 11:39 AM.

Listening...
Recognizing...
You said: what is the date today
Assistant: Today is Sunday, August 09, 2026.

Listening...
Recognizing...
You said: search for Python tutorial
Assistant: Searching the web for 'python tutorial'...

Listening...
Recognizing...
You said: goodbye
Assistant: Goodbye! Have a great day.
```

## Screenshots

Screenshots can be added to the `screenshots/` folder to show the application running.

Some useful screenshots include:

1. The Voice Assistant startup screen.
2. A greeting command and response.
3. A time command and response.
4. A date command and response.
5. A web search command.
6. The assistant exiting successfully.

## OASIS INFOBYTE Internship Task

This project was developed for the **OASIS INFOBYTE Python Programming Internship — Task 1: Voice Assistant**.

The implementation covers the main requirements of the task, including:

* Taking voice input from a microphone.
* Converting speech to text.
* Responding to greetings.
* Providing the current time.
* Providing the current date.
* Performing web searches.
* Providing spoken responses.
* Handling common recognition and microphone errors.
* Allowing the user to exit the program gracefully.

## Possible Future Improvements

The current version focuses on basic voice assistant functionality. It could be extended in the future with features such as:

* More voice commands.
* Weather information.
* Additional web/API integrations.
* Better natural language understanding.
* A graphical user interface.
* More advanced conversational functionality.

These features are not part of the current implementation but could be added as future improvements.

## Author

Developed as part of the **OASIS INFOBYTE Python Programming Internship**.
