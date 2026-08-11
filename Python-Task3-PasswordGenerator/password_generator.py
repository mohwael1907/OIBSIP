"""
password_generator.py - Random Password Generator (GUI & CLI)
Advanced Tier Implementation featuring:
- Tkinter GUI with modern dark aesthetic
- Cryptographically secure secrets module backend
- Guaranteed character inclusion per selected set
- Ambiguous character filtering
- Real-time password strength meter & entropy calculator
- Pyperclip clipboard integration with auto-copy feature
- In-memory session history (last 5 passwords)
- Full CLI mode support via argparse
"""

import argparse
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

# Import core generator logic
from generator_core import (
    PasswordGenerator,
    SessionHistoryManager,
    eval_password_strength,
)

# Clipboard support using pyperclip with fallback
try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    pyperclip = None
    HAS_PYPERCLIP = False


def copy_to_clipboard(text: str, root_win: Optional[tk.Tk] = None) -> bool:
    """Copy text to system clipboard using pyperclip or tkinter fallback."""
    if not text:
        return False
    
    success = False
    if HAS_PYPERCLIP and pyperclip is not None:
        try:
            pyperclip.copy(text)
            success = True
        except Exception:
            success = False

    if not success and root_win is not None:
        try:
            root_win.clipboard_clear()
            root_win.clipboard_append(text)
            root_win.update()
            success = True
        except Exception:
            success = False

    return success


class PasswordGeneratorGUI:
    """Modern Tkinter GUI for Random Password Generator."""

    COLOR_BG = "#181825"        # Deep Charcoal
    COLOR_CARD = "#1E1E2E"      # Dark Card Frame
    COLOR_BORDER = "#313244"    # Subtle Border
    COLOR_TEXT = "#CDD6F4"      # Soft White Text
    COLOR_SUBTEXT = "#A6ADC8"   # Muted Gray Text
    COLOR_ACCENT = "#89B4FA"    # Vibrant Blue
    COLOR_ACCENT_HOVER = "#74C7EC"
    COLOR_SUCCESS = "#A6E3A1"   # Soft Mint Green
    COLOR_BUTTON = "#313244"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Cryptographic Password Generator")
        self.root.geometry("560x780")
        self.root.minsize(500, 680)
        self.root.configure(bg=self.COLOR_BG)

        # Core State
        self.history_mgr = SessionHistoryManager(max_items=5)
        self.current_password = ""
        self.current_meta = {}
        self.is_password_visible = True

        # GUI Variables
        self.var_length = tk.IntVar(value=16)
        self.var_uppercase = tk.BooleanVar(value=True)
        self.var_lowercase = tk.BooleanVar(value=True)
        self.var_digits = tk.BooleanVar(value=True)
        self.var_symbols = tk.BooleanVar(value=True)
        self.var_exclude_ambiguous = tk.BooleanVar(value=False)
        self.var_auto_copy = tk.BooleanVar(value=True)

        self._configure_styles()
        self._build_ui()
        self.generate_new_password()

    def _configure_styles(self):
        """Setup ttk styles for custom widgets."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # General frame style
        self.style.configure("TFrame", background=self.COLOR_BG)
        self.style.configure("Card.TFrame", background=self.COLOR_CARD, relief="flat")

        # Checkbutton style
        self.style.configure(
            "TCheckbutton",
            background=self.COLOR_CARD,
            foreground=self.COLOR_TEXT,
            font=("Segoe UI", 10),
            focuscolor=self.COLOR_CARD,
        )
        self.style.map(
            "TCheckbutton",
            foreground=[("active", "#FFFFFF")],
            background=[("active", self.COLOR_CARD)],
        )

        # Label style
        self.style.configure(
            "TLabel",
            background=self.COLOR_CARD,
            foreground=self.COLOR_TEXT,
            font=("Segoe UI", 10),
        )
        self.style.configure(
            "Header.TLabel",
            background=self.COLOR_BG,
            foreground=self.COLOR_TEXT,
            font=("Segoe UI", 18, "bold"),
        )
        self.style.configure(
            "SubHeader.TLabel",
            background=self.COLOR_BG,
            foreground=self.COLOR_SUBTEXT,
            font=("Segoe UI", 9),
        )

        # Scale / Slider
        self.style.configure(
            "Horizontal.TScale",
            background=self.COLOR_CARD,
            troughcolor=self.COLOR_BORDER,
            sliderlength=20,
        )

        # Spinbox
        self.style.configure(
            "TSpinbox",
            fieldbackground=self.COLOR_BORDER,
            background=self.COLOR_CARD,
            foreground=self.COLOR_TEXT,
            arrowcolor=self.COLOR_TEXT,
            font=("Segoe UI", 10, "bold"),
        )

    def _build_ui(self):
        """Construct the GUI layout."""
        # Main Container Canvas / Frame with Padding
        main_container = tk.Frame(self.root, bg=self.COLOR_BG, padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Header Title
        title_label = ttk.Label(
            main_container,
            text="🔐 Password Generator",
            style="Header.TLabel",
        )
        title_label.pack(anchor="w", pady=(0, 2))

        subtitle_label = ttk.Label(
            main_container,
            text="Cryptographically secure random passwords using Python's secrets module",
            style="SubHeader.TLabel",
        )
        subtitle_label.pack(anchor="w", pady=(0, 15))

        # --- Card 1: Password Display & Quick Actions ---
        card_display = tk.Frame(
            main_container,
            bg=self.COLOR_CARD,
            bd=1,
            relief="solid",
            highlightbackground=self.COLOR_BORDER,
            highlightthickness=1,
            padx=15,
            pady=15,
        )
        card_display.pack(fill=tk.X, pady=(0, 15))

        display_header_frame = tk.Frame(card_display, bg=self.COLOR_CARD)
        display_header_frame.pack(fill=tk.X, pady=(0, 8))

        lbl_disp_title = tk.Label(
            display_header_frame,
            text="GENERATED PASSWORD",
            bg=self.COLOR_CARD,
            fg=self.COLOR_SUBTEXT,
            font=("Segoe UI", 8, "bold"),
        )
        lbl_disp_title.pack(side=tk.LEFT)

        self.lbl_toast = tk.Label(
            display_header_frame,
            text="",
            bg=self.COLOR_CARD,
            fg=self.COLOR_SUCCESS,
            font=("Segoe UI", 9, "bold"),
        )
        self.lbl_toast.pack(side=tk.RIGHT)

        # Output Entry Field
        pwd_field_frame = tk.Frame(card_display, bg=self.COLOR_BORDER, padx=2, pady=2)
        pwd_field_frame.pack(fill=tk.X, pady=(0, 10))

        self.entry_pwd = tk.Entry(
            pwd_field_frame,
            font=("Consolas", 15, "bold"),
            bg="#11111B",
            fg="#89B4FA",
            bd=0,
            relief="flat",
            justify="center",
            insertbackground="#89B4FA",
        )
        self.entry_pwd.pack(fill=tk.X, ipady=8, padx=5)

        # Quick Action Buttons Frame
        actions_frame = tk.Frame(card_display, bg=self.COLOR_CARD)
        actions_frame.pack(fill=tk.X)

        self.btn_toggle_vis = tk.Button(
            actions_frame,
            text="👁 Hide",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLOR_BORDER,
            fg=self.COLOR_TEXT,
            activebackground="#45475A",
            activeforeground="#FFFFFF",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.toggle_password_visibility,
        )
        self.btn_toggle_vis.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_copy = tk.Button(
            actions_frame,
            text="📋 Copy to Clipboard",
            font=("Segoe UI", 9, "bold"),
            bg="#89B4FA",
            fg="#11111B",
            activebackground="#B4BEFE",
            activeforeground="#11111B",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.copy_current_password,
        )
        self.btn_copy.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_generate = tk.Button(
            actions_frame,
            text="🔄 Generate",
            font=("Segoe UI", 9, "bold"),
            bg="#A6E3A1",
            fg="#11111B",
            activebackground="#94E2D5",
            activeforeground="#11111B",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.generate_new_password,
        )
        self.btn_generate.pack(side=tk.RIGHT)

        # --- Card 2: Password Strength Indicator ---
        card_strength = tk.Frame(
            main_container,
            bg=self.COLOR_CARD,
            bd=1,
            relief="solid",
            highlightbackground=self.COLOR_BORDER,
            highlightthickness=1,
            padx=15,
            pady=12,
        )
        card_strength.pack(fill=tk.X, pady=(0, 15))

        str_top_frame = tk.Frame(card_strength, bg=self.COLOR_CARD)
        str_top_frame.pack(fill=tk.X, pady=(0, 5))

        lbl_str_heading = tk.Label(
            str_top_frame,
            text="STRENGTH ASSESSMENT",
            bg=self.COLOR_CARD,
            fg=self.COLOR_SUBTEXT,
            font=("Segoe UI", 8, "bold"),
        )
        lbl_str_heading.pack(side=tk.LEFT)

        self.lbl_strength_rating = tk.Label(
            str_top_frame,
            text="STRONG",
            bg=self.COLOR_CARD,
            fg=self.COLOR_SUCCESS,
            font=("Segoe UI", 10, "bold"),
        )
        self.lbl_strength_rating.pack(side=tk.RIGHT)

        # Custom Canvas Progress Bar
        self.canvas_meter = tk.Canvas(
            card_strength,
            height=10,
            bg=self.COLOR_BORDER,
            bd=0,
            highlightthickness=0,
        )
        self.canvas_meter.pack(fill=tk.X, pady=5)

        self.lbl_entropy_tip = tk.Label(
            card_strength,
            text="Entropy: 0 bits",
            bg=self.COLOR_CARD,
            fg=self.COLOR_TEXT,
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
            wraplength=480,
        )
        self.lbl_entropy_tip.pack(fill=tk.X, pady=(4, 0))

        # --- Card 3: Criteria & Controls ---
        card_controls = tk.Frame(
            main_container,
            bg=self.COLOR_CARD,
            bd=1,
            relief="solid",
            highlightbackground=self.COLOR_BORDER,
            highlightthickness=1,
            padx=15,
            pady=15,
        )
        card_controls.pack(fill=tk.X, pady=(0, 15))

        # Length slider & spinbox
        len_header_frame = tk.Frame(card_controls, bg=self.COLOR_CARD)
        len_header_frame.pack(fill=tk.X, pady=(0, 5))

        lbl_len_title = tk.Label(
            len_header_frame,
            text="PASSWORD LENGTH",
            bg=self.COLOR_CARD,
            fg=self.COLOR_SUBTEXT,
            font=("Segoe UI", 8, "bold"),
        )
        lbl_len_title.pack(side=tk.LEFT)

        # Spinbox synchronized with length variable
        self.spin_length = ttk.Spinbox(
            len_header_frame,
            from_=4,
            to=64,
            textvariable=self.var_length,
            width=5,
            command=self._on_control_changed,
        )
        self.spin_length.pack(side=tk.RIGHT)

        # Slider frame
        slider_frame = tk.Frame(card_controls, bg=self.COLOR_CARD)
        slider_frame.pack(fill=tk.X, pady=(0, 12))

        self.scale_length = ttk.Scale(
            slider_frame,
            from_=4,
            to=64,
            variable=self.var_length,
            command=lambda val: self._on_slider_move(val),
        )
        self.scale_length.pack(fill=tk.X)

        # Checkboxes Grid
        chk_grid = tk.Frame(card_controls, bg=self.COLOR_CARD)
        chk_grid.pack(fill=tk.X, pady=(0, 8))

        chk_upper = ttk.Checkbutton(
            chk_grid,
            text="Uppercase (A-Z)",
            variable=self.var_uppercase,
            command=self._on_control_changed,
        )
        chk_upper.grid(row=0, column=0, sticky="w", padx=(0, 20), pady=4)

        chk_lower = ttk.Checkbutton(
            chk_grid,
            text="Lowercase (a-z)",
            variable=self.var_lowercase,
            command=self._on_control_changed,
        )
        chk_lower.grid(row=0, column=1, sticky="w", pady=4)

        chk_digits = ttk.Checkbutton(
            chk_grid,
            text="Digits (0-9)",
            variable=self.var_digits,
            command=self._on_control_changed,
        )
        chk_digits.grid(row=1, column=0, sticky="w", padx=(0, 20), pady=4)

        chk_symbols = ttk.Checkbutton(
            chk_grid,
            text="Symbols (!@#$)",
            variable=self.var_symbols,
            command=self._on_control_changed,
        )
        chk_symbols.grid(row=1, column=1, sticky="w", pady=4)

        # Additional options
        chk_ambig = ttk.Checkbutton(
            card_controls,
            text="Exclude Ambiguous Characters (0, O, l, 1, I, |)",
            variable=self.var_exclude_ambiguous,
            command=self._on_control_changed,
        )
        chk_ambig.pack(anchor="w", pady=4)

        chk_autocopy = ttk.Checkbutton(
            card_controls,
            text="Auto-copy to clipboard on generation",
            variable=self.var_auto_copy,
        )
        chk_autocopy.pack(anchor="w", pady=4)

        # --- Card 4: Session History ---
        card_history = tk.Frame(
            main_container,
            bg=self.COLOR_CARD,
            bd=1,
            relief="solid",
            highlightbackground=self.COLOR_BORDER,
            highlightthickness=1,
            padx=15,
            pady=12,
        )
        card_history.pack(fill=tk.BOTH, expand=True)

        hist_header = tk.Frame(card_history, bg=self.COLOR_CARD)
        hist_header.pack(fill=tk.X, pady=(0, 8))

        lbl_hist_title = tk.Label(
            hist_header,
            text="RECENT SESSION HISTORY (LAST 5)",
            bg=self.COLOR_CARD,
            fg=self.COLOR_SUBTEXT,
            font=("Segoe UI", 8, "bold"),
        )
        lbl_hist_title.pack(side=tk.LEFT)

        btn_clear_hist = tk.Button(
            hist_header,
            text="Clear",
            font=("Segoe UI", 8),
            bg=self.COLOR_BORDER,
            fg=self.COLOR_SUBTEXT,
            activebackground="#45475A",
            activeforeground="#FFFFFF",
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.clear_history,
        )
        btn_clear_hist.pack(side=tk.RIGHT)

        self.frame_history_items = tk.Frame(card_history, bg=self.COLOR_CARD)
        self.frame_history_items.pack(fill=tk.BOTH, expand=True)

    def _on_slider_move(self, val):
        """Update spinbox variable when slider is moved."""
        try:
            int_val = int(float(val))
            self.var_length.set(int_val)
            self.generate_new_password()
        except ValueError:
            pass

    def _on_control_changed(self):
        """Regenerate password whenever controls/checkboxes change."""
        self.generate_new_password()

    def generate_new_password(self):
        """Generate password with current criteria and update UI."""
        length = self.var_length.get()
        use_upper = self.var_uppercase.get()
        use_lower = self.var_lowercase.get()
        use_digits = self.var_digits.get()
        use_symbols = self.var_symbols.get()
        exclude_ambig = self.var_exclude_ambiguous.get()

        try:
            pwd, meta = PasswordGenerator.generate(
                length=length,
                use_uppercase=use_upper,
                use_lowercase=use_lower,
                use_digits=use_digits,
                use_symbols=use_symbols,
                exclude_ambiguous=exclude_ambig,
            )
            self.current_password = pwd
            self.current_meta = meta

            # Add to history
            self.history_mgr.add(pwd, meta)

            # Update display
            self._update_display()
            self._update_strength_meter()
            self._update_history_ui()

            # Auto-copy if enabled
            if self.var_auto_copy.get():
                copy_to_clipboard(pwd, self.root)
                self.show_toast("Auto-copied!")

        except ValueError as err:
            self.lbl_toast.config(text=str(err), fg="#FF5252")

    def _update_display(self):
        """Update password entry field based on show/hide state."""
        self.entry_pwd.config(state="normal")
        self.entry_pwd.delete(0, tk.END)
        if self.is_password_visible:
            self.entry_pwd.insert(0, self.current_password)
        else:
            self.entry_pwd.insert(0, "●" * len(self.current_password))

    def toggle_password_visibility(self):
        """Toggle between masked and unmasked password text."""
        self.is_password_visible = not self.is_password_visible
        if self.is_password_visible:
            self.btn_toggle_vis.config(text="👁 Hide")
        else:
            self.btn_toggle_vis.config(text="👁 Show")
        self._update_display()

    def copy_current_password(self):
        """Manual copy button action."""
        if not self.current_password:
            return
        if copy_to_clipboard(self.current_password, self.root):
            self.show_toast("Copied to clipboard!")
        else:
            self.show_toast("Failed to copy", error=True)

    def show_toast(self, msg: str, error: bool = False):
        """Display temporary toast feedback."""
        color = "#FF5252" if error else self.COLOR_SUCCESS
        self.lbl_toast.config(text=msg, fg=color)
        self.root.after(2000, lambda: self.lbl_toast.config(text=""))

    def _update_strength_meter(self):
        """Redraw canvas meter and strength labels."""
        meta = self.current_meta
        if not meta:
            return

        rating = meta.get("rating", "Unknown")
        color = meta.get("color", "#888888")
        score_percent = meta.get("score_percent", 0.0)
        entropy = meta.get("entropy_bits", 0.0)
        tips = meta.get("tips", [])

        # Label updates
        self.lbl_strength_rating.config(text=rating.upper(), fg=color)
        tip_text = f"Entropy: {entropy} bits  •  {tips[0]}" if tips else f"Entropy: {entropy} bits"
        self.lbl_entropy_tip.config(text=tip_text)

        # Redraw canvas bar
        self.canvas_meter.delete("all")
        self.root.update_idletasks()
        w = self.canvas_meter.winfo_width()
        h = self.canvas_meter.winfo_height()

        if w <= 1:
            w = 480  # fallback initial width

        fill_w = int(w * (score_percent / 100.0))
        # Draw background track
        self.canvas_meter.create_rectangle(0, 0, w, h, fill=self.COLOR_BORDER, width=0)
        # Draw progress bar
        if fill_w > 0:
            self.canvas_meter.create_rectangle(0, 0, fill_w, h, fill=color, width=0)

    def _update_history_ui(self):
        """Render recent history items."""
        for child in self.frame_history_items.winfo_children():
            child.destroy()

        history = self.history_mgr.get_history()
        if not history:
            lbl_empty = tk.Label(
                self.frame_history_items,
                text="No passwords generated yet.",
                bg=self.COLOR_CARD,
                fg=self.COLOR_SUBTEXT,
                font=("Segoe UI", 9, "italic"),
            )
            lbl_empty.pack(anchor="w", pady=5)
            return

        for idx, item in enumerate(history):
            item_frame = tk.Frame(self.frame_history_items, bg=self.COLOR_CARD)
            item_frame.pack(fill=tk.X, pady=3)

            # Badge color indicator
            lbl_badge = tk.Label(
                item_frame,
                text="●",
                bg=self.COLOR_CARD,
                fg=item["color"],
                font=("Segoe UI", 10),
            )
            lbl_badge.pack(side=tk.LEFT, padx=(0, 6))

            # Masked password preview
            pwd = item["password"]
            display_str = pwd[:4] + "••••" + pwd[-4:] if len(pwd) > 8 else "••••••••"
            lbl_pwd = tk.Label(
                item_frame,
                text=display_str,
                bg=self.COLOR_CARD,
                fg=self.COLOR_TEXT,
                font=("Consolas", 10, "bold"),
            )
            lbl_pwd.pack(side=tk.LEFT, padx=(0, 10))

            # Time tag
            lbl_time = tk.Label(
                item_frame,
                text=item["timestamp"],
                bg=self.COLOR_CARD,
                fg=self.COLOR_SUBTEXT,
                font=("Segoe UI", 8),
            )
            lbl_time.pack(side=tk.LEFT)

            # Individual copy button
            btn_item_copy = tk.Button(
                item_frame,
                text="Copy",
                font=("Segoe UI", 8),
                bg=self.COLOR_BORDER,
                fg=self.COLOR_TEXT,
                activebackground="#45475A",
                activeforeground="#FFFFFF",
                bd=0,
                padx=8,
                pady=2,
                cursor="hand2",
                command=lambda p=pwd: self._copy_history_item(p),
            )
            btn_item_copy.pack(side=tk.RIGHT)

    def _copy_history_item(self, pwd: str):
        """Copy selected history password to clipboard."""
        if copy_to_clipboard(pwd, self.root):
            self.show_toast("History password copied!")
        else:
            self.show_toast("Copy failed", error=True)

    def clear_history(self):
        """Clear history records."""
        self.history_mgr.clear()
        self._update_history_ui()
        self.show_toast("History cleared!")


def run_cli_mode(args):
    """Execute headlessly in Command-Line Interface mode."""
    try:
        password, meta = PasswordGenerator.generate(
            length=args.length,
            use_uppercase=not args.no_upper,
            use_lowercase=not args.no_lower,
            use_digits=not args.no_digits,
            use_symbols=not args.no_symbols,
            exclude_ambiguous=args.exclude_ambiguous,
        )

        print("\n=== Cryptographic Password Generator ===")
        print(f"Generated Password : {password}")
        print(f"Length             : {len(password)}")
        print(f"Strength Rating    : {meta['rating']}")
        print(f"Entropy (bits)     : {meta['entropy_bits']}")
        print("Tips               : " + " | ".join(meta['tips']))

        if args.copy:
            if copy_to_clipboard(password):
                print("[+] Password copied to clipboard!")
            else:
                print("[-] Could not copy to clipboard.")

    except ValueError as err:
        print(f"[Error] {err}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Cryptographically Secure Random Password Generator (GUI & CLI)"
    )
    parser.add_argument("--cli", action="store_true", help="Run in CLI headless mode")
    parser.add_argument("-l", "--length", type=int, default=16, help="Password length (default: 16)")
    parser.add_argument("--no-upper", action="store_true", help="Exclude uppercase letters")
    parser.add_argument("--no-lower", action="store_true", help="Exclude lowercase letters")
    parser.add_argument("--no-digits", action="store_true", help="Exclude digits")
    parser.add_argument("--no-symbols", action="store_true", help="Exclude special symbols")
    parser.add_argument("-a", "--exclude-ambiguous", action="store_true", help="Exclude ambiguous characters (0, O, l, 1, I, |)")
    parser.add_argument("-c", "--copy", action="store_true", help="Copy password to clipboard automatically (CLI mode)")

    args = parser.parse_args()

    # Force CLI mode if --cli flag passed or arguments explicitly given
    if args.cli or any([
        args.no_upper, args.no_lower, args.no_digits, args.no_symbols,
        args.exclude_ambiguous, args.copy
    ]):
        run_cli_mode(args)
    else:
        root = tk.Tk()
        app = PasswordGeneratorGUI(root)
        root.mainloop()


if __name__ == "__main__":
    main()
