# PulseChat

A simple Flask-based chat application with Socket.IO room chat, emoji shortcode parsing, user authentication, and message persistence using SQLite.

## Features

- User registration and login
- Real-time chat rooms powered by Socket.IO
- Room creation and browsing
- Message history stored in SQLite
- Emoji shortcode support (e.g. `:smile:`)
- Typing status indicators
- Desktop notifications and audio chime for incoming messages
- Online user list per room

## Project Structure

- `app.py`: Main Flask application and Socket.IO server
- `database.py`: SQLite database helpers and models for users, rooms, and messages
- `emoji_utils.py`: Emoji shortcode parsing utilities
- `templates/`: HTML pages for login, registration, and chat UI
- `static/`: CSS and JavaScript assets for the frontend
- `chat.db`: SQLite database file (created automatically)

## Requirements

- Python 3.8+
- Flask
- Flask-SocketIO
- Werkzeug

## Setup

1. Open a terminal in the project directory.

2. Create a virtual environment (recommended):

```bash
python -m venv venv
```

3. Activate the virtual environment:

- Windows:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- macOS / Linux:
  ```bash
  source venv/bin/activate
  ```

4. Install required packages:

```bash
pip install flask flask-socketio werkzeug
```

> Optional: install `eventlet` or `gevent` for improved Socket.IO performance in production.

## Running the App

Run the application from the project directory:

```bash
python app.py
```

Then open your browser to:

```text
http://127.0.0.1:5000
```

## Usage

1. Register a new account, or log in with an existing username.
2. Browse available chat rooms.
3. Create a room with a name and description.
4. Join a room and send messages in real time.
5. Use emoji shortcodes like `:fire:` or `:thumbsup:` to insert emoji.

## Notes

- The app uses an SQLite database file named `chat.db` in the project root.
- The server initializes database tables automatically when started.
- Socket.IO is used to broadcast new messages and room activity to connected clients.

## Customization

- Add more emoji shortcodes in `emoji_utils.py`
- Update templates in `templates/` to change UI layout or branding
- Extend database models in `database.py` for additional chat features

## License

This project is provided as-is for learning and experimentation.
