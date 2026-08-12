/* ==========================================================================
   PulseChat Client JavaScript Engine
   Socket.IO, Room Management, Desktop Notifications, Emoji Picker, Audio Chime
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    // Current User & Active Room State
    const currentUser = window.CURRENT_USERNAME;
    let currentRoom = null;
    let socket = null;
    let unreadCounts = {}; // { roomName: count }
    let typingTimeout = null;
    let isTyping = false;
    let isSoundEnabled = true;
    let isNotifEnabled = Notification && Notification.permission === "granted";

    // DOM Element References
    const roomsList = document.getElementById("rooms-list");
    const roomSearchInput = document.getElementById("room-search-input");
    const currentRoomNameEl = document.getElementById("current-room-name");
    const currentRoomDescEl = document.getElementById("current-room-desc");
    const messageFeed = document.getElementById("message-feed");
    const messagesContainer = document.getElementById("messages-container");
    const emptyState = document.getElementById("empty-state");
    const messageInput = document.getElementById("message-input");
    const sendBtn = document.getElementById("btn-send-message");
    const typingIndicator = document.getElementById("typing-indicator");
    const typingText = document.getElementById("typing-text");

    // Emoji Picker Elements
    const btnEmojiToggle = document.getElementById("btn-emoji-toggle");
    const emojiPicker = document.getElementById("emoji-picker");
    const emojiPickerClose = document.getElementById("emoji-picker-close");
    const emojiGrid = document.getElementById("emoji-grid");

    // Room Modal Elements
    const btnOpenCreateRoom = document.getElementById("btn-open-create-room");
    const createRoomModal = document.getElementById("create-room-modal");
    const btnCloseModal = document.getElementById("btn-close-modal");
    const btnCancelModal = document.getElementById("btn-cancel-modal");
    const createRoomForm = document.getElementById("create-room-form");

    // Right Panel & Actions Elements
    const btnToggleUsers = document.getElementById("btn-toggle-users");
    const headerUserCount = document.getElementById("header-user-count");
    const rightPanel = document.getElementById("right-panel");
    const btnCloseRightPanel = document.getElementById("btn-close-right-panel");
    const onlineUsersList = document.getElementById("online-users-list");

    const btnToggleNotif = document.getElementById("btn-toggle-notif");
    const btnToggleSound = document.getElementById("btn-toggle-sound");

    // Sync Notification Button State
    updateNotifButtonState();

    // ==========================================
    // 1. Web Audio API Synthetic Chime Generator
    // ==========================================
    function playChimeSound() {
        if (!isSoundEnabled) return;
        try {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (!AudioCtx) return;
            const ctx = new AudioCtx();

            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.type = "sine";
            osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
            osc.frequency.exponentialRampToValueAtTime(880.00, ctx.currentTime + 0.15); // A5

            gain.gain.setValueAtTime(0.15, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);

            osc.connect(gain);
            gain.connect(ctx.destination);

            osc.start();
            osc.stop(ctx.currentTime + 0.35);
        } catch (e) {
            console.warn("Audio chime playback error:", e);
        }
    }

    // ==========================================
    // 2. Socket.IO Setup & Event Handlers
    // ==========================================
    function initSocket() {
        socket = io();

        socket.on("connect", () => {
            console.log("Connected to PulseChat Socket.IO server.");
        });

        socket.on("room_created", (data) => {
            loadRoomsList();
        });

        socket.on("user_joined", (data) => {
            if (data.room === currentRoom) {
                renderSystemMessage(`${data.username} joined the room.`);
                updateOnlineUsersList(data.online_users);
            }
        });

        socket.on("user_left", (data) => {
            if (data.room === currentRoom) {
                renderSystemMessage(`${data.username} left the room.`);
                updateOnlineUsersList(data.online_users);
            }
        });

        socket.on("new_message", (msg) => {
            if (msg.room_name === currentRoom) {
                renderSingleMessage(msg);
                scrollToBottom();
                if (msg.username !== currentUser) {
                    playChimeSound();
                    triggerDesktopNotification(msg);
                }
            } else {
                // Increment unread count for other rooms
                unreadCounts[msg.room_name] = (unreadCounts[msg.room_name] || 0) + 1;
                updateRoomItemUnreadBadge(msg.room_name);
                playChimeSound();
                triggerDesktopNotification(msg);
            }
        });

        socket.on("user_typing", (data) => {
            if (data.room === currentRoom) {
                if (data.is_typing) {
                    typingText.textContent = `${data.username} is typing...`;
                    typingIndicator.classList.add("visible");
                } else {
                    typingIndicator.classList.remove("visible");
                }
            }
        });
    }

    // ==========================================
    // 3. Desktop Notification API
    // ==========================================
    function triggerDesktopNotification(msg) {
        if (!isNotifEnabled || document.hasFocus()) return;
        try {
            const notif = new Notification(`PulseChat - #${msg.room_name}`, {
                body: `${msg.username}: ${msg.content}`,
                icon: "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/svgs/solid/comments.svg"
            });
            notif.onclick = () => {
                window.focus();
                switchRoom(msg.room_name);
            };
        } catch (e) {
            console.warn("Desktop notification error:", e);
        }
    }

    function updateNotifButtonState() {
        if (Notification && Notification.permission === "granted") {
            isNotifEnabled = true;
            btnToggleNotif.classList.add("active");
            btnToggleNotif.innerHTML = '<i class="fa-solid fa-bell"></i>';
            btnToggleNotif.title = "Desktop Notifications Enabled";
        } else {
            isNotifEnabled = false;
            btnToggleNotif.classList.remove("active");
            btnToggleNotif.innerHTML = '<i class="fa-solid fa-bell-slash"></i>';
            btnToggleNotif.title = "Enable Desktop Notifications";
        }
    }

    btnToggleNotif.addEventListener("click", () => {
        if (!Notification) {
            alert("Desktop notifications are not supported in this browser.");
            return;
        }
        if (Notification.permission === "granted") {
            alert("Desktop notifications are already enabled.");
        } else if (Notification.permission !== "denied") {
            Notification.requestPermission().then((permission) => {
                updateNotifButtonState();
            });
        } else {
            alert("Notification permissions were blocked in your browser settings.");
        }
    });

    btnToggleSound.addEventListener("click", () => {
        isSoundEnabled = !isSoundEnabled;
        if (isSoundEnabled) {
            btnToggleSound.classList.add("active");
            btnToggleSound.innerHTML = '<i class="fa-solid fa-volume-high"></i>';
            btnToggleSound.title = "Audio Chime (On)";
        } else {
            btnToggleSound.classList.remove("active");
            btnToggleSound.innerHTML = '<i class="fa-solid fa-volume-xmark"></i>';
            btnToggleSound.title = "Audio Chime (Muted)";
        }
    });

    // ==========================================
    // 4. Room Management Logic
    // ==========================================
    async function loadRoomsList() {
        try {
            const response = await fetch("/api/rooms");
            const data = await response.json();
            if (data.rooms) {
                renderRoomsList(data.rooms);
                // Default join first room if none selected
                if (!currentRoom && data.rooms.length > 0) {
                    switchRoom(data.rooms[0].name, data.rooms[0].description);
                }
            }
        } catch (err) {
            console.error("Failed to load rooms:", err);
        }
    }

    function renderRoomsList(rooms) {
        const filterText = roomSearchInput.value.toLowerCase().trim();
        roomsList.innerHTML = "";

        const filtered = rooms.filter(r => r.name.toLowerCase().includes(filterText) || (r.description && r.description.toLowerCase().includes(filterText)));

        if (filtered.length === 0) {
            roomsList.innerHTML = `<div class="rooms-loading">No rooms found.</div>`;
            return;
        }

        filtered.forEach(room => {
            const item = document.createElement("div");
            item.className = `room-item ${room.name === currentRoom ? 'active' : ''}`;
            item.dataset.roomName = room.name;

            const unreadCount = unreadCounts[room.name] || 0;
            const badgeHtml = unreadCount > 0 ? `<span class="unread-counter">${unreadCount}</span>` : '';

            item.innerHTML = `
                <div class="room-item-details">
                    <div class="room-item-title">
                        <span class="hash">#</span> ${escapeHtml(room.name)}
                    </div>
                    <div class="room-item-desc">${escapeHtml(room.description || 'No topic')}</div>
                </div>
                ${badgeHtml}
            `;

            item.addEventListener("click", () => {
                switchRoom(room.name, room.description);
            });

            roomsList.appendChild(item);
        });
    }

    function updateRoomItemUnreadBadge(roomName) {
        const item = roomsList.querySelector(`[data-room-name="${roomName}"]`);
        if (item) {
            const count = unreadCounts[roomName] || 0;
            let badge = item.querySelector(".unread-counter");
            if (count > 0) {
                if (!badge) {
                    badge = document.createElement("span");
                    badge.className = "unread-counter";
                    item.appendChild(badge);
                }
                badge.textContent = count;
            } else if (badge) {
                badge.remove();
            }
        }
    }

    function switchRoom(roomName, description = "") {
        if (currentRoom === roomName) return;

        // Leave current room
        if (currentRoom && socket) {
            socket.emit("leave_room", { room: currentRoom });
        }

        currentRoom = roomName;
        unreadCounts[roomName] = 0;
        updateRoomItemUnreadBadge(roomName);

        // Highlight room item in sidebar
        const roomItems = roomsList.querySelectorAll(".room-item");
        roomItems.forEach(item => {
            item.classList.toggle("active", item.dataset.roomName === roomName);
        });

        // Update Header
        currentRoomNameEl.textContent = `# ${roomName}`;
        currentRoomDescEl.textContent = description || `Topic: Real-time room #${roomName}`;

        // Clear feed & loading history
        messageFeed.innerHTML = "";
        emptyState.classList.add("hidden");

        // Socket Join Room Event
        if (socket) {
            socket.emit("join_room", { room: roomName });
        }

        // Fetch History via REST API
        loadRoomHistory(roomName);
    }

    async function loadRoomHistory(roomName) {
        try {
            const response = await fetch(`/api/rooms/${encodeURIComponent(roomName)}/history`);
            const data = await response.json();

            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(msg => renderSingleMessage(msg));
                scrollToBottom();
            }
        } catch (err) {
            console.error("Failed to load room history:", err);
        }
    }

    roomSearchInput.addEventListener("input", loadRoomsList);

    // ==========================================
    // 5. Message Rendering & Sending
    // ==========================================
    function renderSingleMessage(msg) {
        const isOwn = msg.username === currentUser;

        const row = document.createElement("div");
        row.className = `msg-row ${isOwn ? 'own-msg' : 'other-msg'}`;

        const initial = (msg.username || "?")[0].toUpperCase();
        const formattedTime = formatTimestamp(msg.timestamp);

        row.innerHTML = `
            <div class="msg-avatar" title="${escapeHtml(msg.username)}">${initial}</div>
            <div class="msg-content-wrapper">
                <div class="msg-meta">
                    <span class="msg-sender">${escapeHtml(msg.username)}</span>
                    <span class="msg-time">${formattedTime}</span>
                </div>
                <div class="msg-bubble">${escapeHtml(msg.content)}</div>
            </div>
        `;

        messageFeed.appendChild(row);
    }

    function renderSystemMessage(text) {
        const sysDiv = document.createElement("div");
        sysDiv.className = "msg-system";
        sysDiv.textContent = text;
        messageFeed.appendChild(sysDiv);
        scrollToBottom();
    }

    function sendMessage() {
        const text = messageInput.value.trim();
        if (!text || !currentRoom) return;

        socket.emit("send_message", {
            room: currentRoom,
            message: text
        });

        messageInput.value = "";
        stopTyping();
    }

    sendBtn.addEventListener("click", sendMessage);
    messageInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        } else {
            handleTypingIndicator();
        }
    });

    function handleTypingIndicator() {
        if (!isTyping && currentRoom) {
            isTyping = true;
            socket.emit("typing", { room: currentRoom, is_typing: true });
        }
        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(stopTyping, 2000);
    }

    function stopTyping() {
        if (isTyping && currentRoom) {
            isTyping = false;
            socket.emit("typing", { room: currentRoom, is_typing: false });
        }
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function formatTimestamp(tsStr) {
        if (!tsStr) return "";
        try {
            const d = new Date(tsStr.replace(" ", "T"));
            return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } catch (e) {
            return tsStr;
        }
    }

    function escapeHtml(str) {
        if (!str) return "";
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // ==========================================
    // 6. Emoji Picker Popover
    // ==========================================
    async function loadEmojiPicker() {
        try {
            const res = await fetch("/api/emojis");
            const data = await res.json();
            if (data.emojis) {
                emojiGrid.innerHTML = "";
                data.emojis.forEach(item => {
                    const el = document.createElement("div");
                    el.className = "emoji-item";
                    el.textContent = item.unicode;
                    el.title = item.shortcode;
                    el.addEventListener("click", () => {
                        insertAtCursor(messageInput, item.shortcode);
                        emojiPicker.classList.add("hidden");
                        messageInput.focus();
                    });
                    emojiGrid.appendChild(el);
                });
            }
        } catch (e) {
            console.error("Failed to load emojis:", e);
        }
    }

    btnEmojiToggle.addEventListener("click", (e) => {
        e.stopPropagation();
        emojiPicker.classList.toggle("hidden");
    });
    emojiPickerClose.addEventListener("click", () => {
        emojiPicker.classList.add("hidden");
    });

    document.addEventListener("click", (e) => {
        if (!emojiPicker.contains(e.target) && e.target !== btnEmojiToggle) {
            emojiPicker.classList.add("hidden");
        }
    });

    function insertAtCursor(input, text) {
        const start = input.selectionStart || input.value.length;
        const end = input.selectionEnd || input.value.length;
        const value = input.value;
        input.value = value.substring(0, start) + text + " " + value.substring(end);
        input.selectionStart = input.selectionEnd = start + text.length + 1;
    }

    // ==========================================
    // 7. Right Panel (Online Members)
    // ==========================================
    function updateOnlineUsersList(users) {
        const list = users || [];
        headerUserCount.textContent = list.length;

        onlineUsersList.innerHTML = "";
        list.forEach(user => {
            const item = document.createElement("div");
            item.className = "online-user-item";
            item.innerHTML = `
                <span class="status-indicator online"></span>
                <span class="online-user-name">${escapeHtml(user)}</span>
            `;
            onlineUsersList.appendChild(item);
        });
    }

    btnToggleUsers.addEventListener("click", () => {
        rightPanel.classList.toggle("hidden");
    });
    btnCloseRightPanel.addEventListener("click", () => {
        rightPanel.classList.add("hidden");
    });

    // ==========================================
    // 8. Room Creation Modal Logic
    // ==========================================
    btnOpenCreateRoom.addEventListener("click", () => {
        createRoomModal.classList.remove("hidden");
        document.getElementById("new-room-name").focus();
    });

    function closeModal() {
        createRoomModal.classList.add("hidden");
        createRoomForm.reset();
    }
    btnCloseModal.addEventListener("click", closeModal);
    btnCancelModal.addEventListener("click", closeModal);

    createRoomForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("new-room-name").value.trim();
        const description = document.getElementById("new-room-desc").value.trim();

        if (!name) return;

        try {
            const res = await fetch("/api/rooms", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, description })
            });

            const data = await res.json();
            if (data.success) {
                closeModal();
                await loadRoomsList();
                switchRoom(name, description);
            } else {
                alert(data.message || "Failed to create room.");
            }
        } catch (err) {
            console.error("Room creation error:", err);
            alert("Error creating room.");
        }
    });

    // Initialize Execution
    initSocket();
    loadRoomsList();
    loadEmojiPicker();
});
