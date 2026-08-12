import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from database import (
    init_db, register_user, authenticate_user,
    get_all_rooms, create_room, save_message, get_room_history
)
from emoji_utils import parse_emojis, get_emoji_list

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24).hex()

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory tracking of connected users per room
# Dict[room_name, Set[username]]
ROOM_ONLINE_USERS = {}
# Dict[sid, Dict[str, str]] storing session info
CLIENT_SESSIONS = {}


@app.before_request
def setup_db():
    # Ensure database tables exist
    if not getattr(app, '_db_inited', False):
        init_db()
        app._db_inited = True


# ==========================================
# HTTP Routes
# ==========================================

@app.route("/")
def index():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("chat.html", username=session["username"])


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if authenticate_user(username, password):
            session["username"] = username
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "error")
            return render_template("login.html", username=username)

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html", username=username)

        success, msg = register_user(username, password)
        if success:
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash(msg, "error")
            return render_template("register.html", username=username)

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/api/rooms", methods=["GET"])
def api_get_rooms():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    rooms = get_all_rooms()
    return jsonify({"rooms": rooms})


@app.route("/api/rooms", methods=["POST"])
def api_create_room():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json() or request.form
    name = data.get("name", "").strip()
    description = data.get("description", "").strip()
    
    success, msg = create_room(name, description, session["username"])
    if success:
        # Broadcast room creation to all connected clients
        socketio.emit("room_created", {"name": name, "description": description, "created_by": session["username"]})
        return jsonify({"success": True, "message": msg, "room": {"name": name, "description": description}})
    else:
        return jsonify({"success": False, "message": msg}), 400


@app.route("/api/rooms/<room_name>/history", methods=["GET"])
def api_room_history(room_name):
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    history = get_room_history(room_name)
    return jsonify({"room": room_name, "messages": history})


@app.route("/api/emojis", methods=["GET"])
def api_emojis():
    return jsonify({"emojis": get_emoji_list()})


# ==========================================
# SocketIO Events
# ==========================================

@socketio.on("connect")
def handle_connect():
    username = session.get("username")
    if not username:
        return False  # Reject connection if not logged in
    CLIENT_SESSIONS[request.sid] = {"username": username, "current_room": None}


@socketio.on("disconnect")
def handle_disconnect():
    sid_info = CLIENT_SESSIONS.pop(request.sid, None)
    if sid_info:
        username = sid_info["username"]
        current_room = sid_info["current_room"]
        if current_room and current_room in ROOM_ONLINE_USERS:
            ROOM_ONLINE_USERS[current_room].discard(username)
            emit("user_left", {
                "username": username,
                "room": current_room,
                "online_users": list(ROOM_ONLINE_USERS[current_room])
            }, to=current_room)


@socketio.on("join_room")
def handle_join_room(data):
    username = session.get("username")
    if not username:
        return

    room = data.get("room")
    if not room:
        return

    # Leave previous room if any
    sid_info = CLIENT_SESSIONS.get(request.sid)
    if sid_info and sid_info["current_room"]:
        prev_room = sid_info["current_room"]
        leave_room(prev_room)
        if prev_room in ROOM_ONLINE_USERS:
            ROOM_ONLINE_USERS[prev_room].discard(username)
            emit("user_left", {
                "username": username,
                "room": prev_room,
                "online_users": list(ROOM_ONLINE_USERS[prev_room])
            }, to=prev_room)

    # Join new room
    join_room(room)
    if sid_info:
        sid_info["current_room"] = room

    if room not in ROOM_ONLINE_USERS:
        ROOM_ONLINE_USERS[room] = set()
    ROOM_ONLINE_USERS[room].add(username)

    # Broadcast join event and updated user list
    emit("user_joined", {
        "username": username,
        "room": room,
        "online_users": list(ROOM_ONLINE_USERS[room])
    }, to=room)


@socketio.on("leave_room")
def handle_leave_room(data):
    username = session.get("username")
    room = data.get("room")
    if username and room:
        leave_room(room)
        sid_info = CLIENT_SESSIONS.get(request.sid)
        if sid_info and sid_info["current_room"] == room:
            sid_info["current_room"] = None

        if room in ROOM_ONLINE_USERS:
            ROOM_ONLINE_USERS[room].discard(username)
            emit("user_left", {
                "username": username,
                "room": room,
                "online_users": list(ROOM_ONLINE_USERS[room])
            }, to=room)


@socketio.on("send_message")
def handle_send_message(data):
    username = session.get("username")
    room = data.get("room")
    raw_content = data.get("message", "").strip()

    if not username or not room or not raw_content:
        return

    # Parse emoji shortcodes (e.g. :smile: -> 😄)
    parsed_content = parse_emojis(raw_content)

    # Persist message to SQLite
    msg_obj = save_message(room, username, parsed_content)

    # Broadcast message to room
    emit("new_message", msg_obj, to=room)


@socketio.on("typing")
def handle_typing(data):
    username = session.get("username")
    room = data.get("room")
    is_typing = data.get("is_typing", False)

    if username and room:
        emit("user_typing", {
            "username": username,
            "room": room,
            "is_typing": is_typing
        }, to=room, include_self=False)


if __name__ == "__main__":
    init_db()
    print("Starting Chat Application on http://127.0.0.1:5000 ...")
    socketio.run(app, debug=True, host="127.0.0.1", port=5000)
