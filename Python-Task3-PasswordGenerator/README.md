# 🔐 Cryptographic Random Password Generator (Advanced Tier)

A high-security, cryptographically sound Python password generation application with a modern Tkinter GUI, real-time password strength meter, clipboard integration, ambiguous character exclusion, session history, and full CLI support.

---

## ✨ Features Checklist (Advanced Tier)

- [x] **Tkinter GUI Window**: Modern dark-themed user interface with synchronized slider and spinbox length control (4–64 characters) and individual checkboxes for character type selection (Uppercase, Lowercase, Digits, Symbols).
- [x] **Cryptographically Secure (`secrets` module)**: Built using Python's standard `secrets` module (`secrets.choice` and `secrets.SystemRandom().shuffle`) rather than pseudo-random `random` for high security.
- [x] **Guaranteed Character Inclusion**: Security rules strictly guaranteed — every generated password contains at least one character from each selected character set.
- [x] **Password Strength & Entropy Assessment**: Real-time visual progress meter and status badge (`Weak`, `Medium`, `Strong`, `Very Strong`) calculated from bit entropy ($E = L \times \log_2(N)$) and character diversity, accompanied by actionable security tips.
- [x] **Clipboard Integration (`pyperclip`)**: Dedicated "Copy to Clipboard" button and optional "Auto-copy on generation" setting using `pyperclip` (with Tkinter fallback).
- [x] **Ambiguous Character Exclusion**: Checkbox option to filter out confusing/ambiguous characters (`0`, `O`, `o`, `l`, `1`, `I`, `|`).
- [x] **Session History (In-Memory)**: Displays the last 5 generated passwords during the active session with individual copy buttons and masked previews. Strictly kept in-memory and cleared on application exit for security.
- [x] **CLI & GUI Modes**: Supports headless command-line execution (`--cli`, `-l`, `-a`, `-c`) as well as interactive GUI mode.
- [x] **Automated Unit Tests**: Suite of 7 unit tests verifying randomness, security guarantees, entropy scoring, ambiguous character exclusion, and history limits.

---

## 🛠️ Installation & Requirements

### Prerequisites
- Python **3.8+** (Uses built-in `tkinter` and `secrets` modules)

### Install Dependencies
```bash
pip install -r requirements.txt
```
*(Dependencies: `pyperclip>=1.8.2` for system clipboard access, `pytest>=7.0.0` for testing)*

---

## 🚀 How to Run

### 1. Launch Interactive GUI Mode
```bash
python password_generator.py
```

### 2. Run Headless CLI Mode
Generate a 24-character password excluding ambiguous characters and copying to clipboard:
```bash
python password_generator.py --cli --length 24 --exclude-ambiguous --copy
```

#### CLI Command Options:
- `-l, --length <N>`: Set password length (default: 16)
- `-a, --exclude-ambiguous`: Exclude ambiguous characters (`0, O, l, 1, I, |`)
- `-c, --copy`: Automatically copy output password to clipboard
- `--no-upper`: Omit uppercase letters
- `--no-lower`: Omit lowercase letters
- `--no-digits`: Omit digits
- `--no-symbols`: Omit special symbols

---

## 🧪 Running Unit Tests

Run the automated test suite with `unittest` or `pytest`:
```bash
python -m unittest test_generator.py
```
or
```bash
pytest test_generator.py
```

---

## 📐 Architecture & Security Design

```
task3/
├── password_generator.py   # GUI Application & CLI entry point
├── generator_core.py       # Cryptographic generation, entropy math & history manager
├── test_generator.py       # Comprehensive unit tests
├── requirements.txt        # Package dependencies
└── README.md               # Documentation
```

### Cryptographic Foundation
Standard pseudo-random number generators (PRNGs) like Python's `random` module (Mersenne Twister) are deterministic and predictable given sufficient outputs. This project uses `secrets.choice()` backed by OS-level entropy sources (`/dev/urandom` or CryptGenRandom/BCryptGenRandom on Windows).

### Bit Entropy Formula
Password strength is quantified using Shannon entropy in bits:
$$E = L \times \log_2(N)$$
Where:
- $L$ = Length of generated password
- $N$ = Number of unique available characters in active pool after applying ambiguity filters
