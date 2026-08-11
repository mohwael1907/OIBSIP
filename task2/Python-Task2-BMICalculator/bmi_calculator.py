"""
Advanced BMI Calculator - Dashboard Edition
--------------------------------------------
A desktop GUI dashboard built with Python 3, Tkinter, SQLite, and Matplotlib.
Includes multi-user tracking, local database persistence, CSV export, live updates,
and 3 embedded real-data charts:
  1. BMI Category Highlight Chart
  2. BMI Trend Line Graph
  3. Weight vs. BMI Correlation Chart

OASIS INFOBYTE Python Programming Internship - Task 2 (Advanced Tier)
"""

import os
import csv
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class DatabaseManager:
    """Handles all SQLite database operations for storing, retrieving, exporting, and resetting BMI records."""

    def __init__(self, db_path="bmi_records.db"):
        """Initialize database connection and ensure the required table exists."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(script_dir, db_path)
        self.create_table()

    def get_connection(self):
        """Returns a connection to the SQLite database."""
        return sqlite3.connect(self.db_path)

    def create_table(self):
        """Creates the bmi_records table automatically if it does not exist."""
        try:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS bmi_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        weight REAL NOT NULL,
                        height REAL NOT NULL,
                        bmi REAL NOT NULL,
                        category TEXT NOT NULL,
                        timestamp TEXT NOT NULL
                    )
                """)
                conn.commit()
            finally:
                conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {e}")

    def add_record(self, username, weight, height, bmi, category):
        """Inserts a new BMI calculation record into the database."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO bmi_records (username, weight, height, bmi, category, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (username.strip().title(), weight, height, bmi, category, timestamp))
                conn.commit()
                return True
            finally:
                conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save record: {e}")
            return False

    def get_user_records(self, username=None):
        """
        Retrieves BMI records. If a username is provided, filters by user.
        Otherwise returns all records.
        """
        try:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                if username and username != "All Users":
                    cursor.execute("""
                        SELECT id, username, weight, height, bmi, category, timestamp 
                        FROM bmi_records 
                        WHERE username = ? 
                        ORDER BY id ASC
                    """, (username.strip().title(),))
                else:
                    cursor.execute("""
                        SELECT id, username, weight, height, bmi, category, timestamp 
                        FROM bmi_records 
                        ORDER BY id ASC
                    """)
                return cursor.fetchall()
            finally:
                conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch records: {e}")
            return []

    def get_all_usernames(self):
        """Returns a sorted list of unique usernames stored in the database."""
        try:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT username FROM bmi_records ORDER BY username ASC")
                rows = cursor.fetchall()
                return [row[0] for row in rows]
            finally:
                conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch users: {e}")
            return []

    def delete_record(self, record_id):
        """Deletes a specific record by ID."""
        try:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM bmi_records WHERE id = ?", (record_id,))
                conn.commit()
                return True
            finally:
                conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete record: {e}")
            return False

    def clear_user_history(self, username=None):
        """Clears all records for a specific user or all users."""
        try:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                if username and username != "All Users":
                    cursor.execute("DELETE FROM bmi_records WHERE username = ?", (username.strip().title(),))
                else:
                    cursor.execute("DELETE FROM bmi_records")
                conn.commit()
                return True
            finally:
                conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to clear history: {e}")
            return False

    def export_to_csv(self, filepath, username=None):
        """Exports user BMI records to a CSV file."""
        records = self.get_user_records(username)
        if not records:
            return 0
        try:
            with open(filepath, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Record ID", "Timestamp", "User Name", "Weight (kg)", "Height (m)", "BMI", "Category"])
                for row in records:
                    # row: (id, username, weight, height, bmi, category, timestamp)
                    writer.writerow([row[0], row[6], row[1], row[2], row[3], row[4], row[5]])
            return len(records)
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV file: {e}")
            return -1


def calculate_bmi(weight_kg, height_m):
    """
    Calculates BMI using standard formula: weight / (height ** 2)
    and returns (rounded_bmi, category_name).
    """
    bmi = weight_kg / (height_m ** 2)
    rounded_bmi = round(bmi, 2)

    if rounded_bmi < 18.5:
        category = "Underweight"
    elif rounded_bmi < 25.0:
        category = "Normal Weight"
    elif rounded_bmi < 30.0:
        category = "Overweight"
    else:
        category = "Obese"

    return rounded_bmi, category


def get_category_color(category):
    """Returns hex colors for category visualization (fg_color, bg_color)."""
    color_map = {
        "Underweight": ("#1d6f8a", "#e0f2fe"),    # Soft Blue
        "Normal Weight": ("#15803d", "#dcfce7"),  # Soft Green
        "Overweight": ("#c2410c", "#ffedd5"),     # Soft Orange
        "Obese": ("#b91c1c", "#fee2e2")           # Soft Red
    }
    return color_map.get(category, ("#1f2937", "#f3f4f6"))


class EmbeddedChartsFrame(tk.Frame):
    """Frame housing 3 real-data Matplotlib charts embedded directly into the application."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg="#f8fafc")

        # Container layout for 3 subplots in a 2x2 grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Create Matplotlib Figures
        self.fig1 = Figure(figsize=(5.2, 2.7), dpi=90, facecolor='#f8fafc')
        self.ax1 = self.fig1.add_subplot(111)

        self.fig2 = Figure(figsize=(5.2, 2.7), dpi=90, facecolor='#f8fafc')
        self.ax2 = self.fig2.add_subplot(111)

        self.fig3 = Figure(figsize=(10.6, 2.7), dpi=90, facecolor='#f8fafc')
        self.ax3 = self.fig3.add_subplot(111)

        # Embedded Canvases
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self)
        self.canvas1.get_tk_widget().grid(row=0, column=0, padx=6, pady=6, sticky="nsew")

        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self)
        self.canvas2.get_tk_widget().grid(row=0, column=1, padx=6, pady=6, sticky="nsew")

        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=self)
        self.canvas3.get_tk_widget().grid(row=1, column=0, columnspan=2, padx=6, pady=6, sticky="nsew")

        self.draw_empty_placeholders()

    def draw_empty_placeholders(self, message="Calculate or select a user to render charts"):
        """Renders initial placeholder text on canvases."""
        for ax, title in [(self.ax1, "1. BMI Category Distribution"),
                          (self.ax2, "2. BMI Trend Over Time"),
                          (self.ax3, "3. Weight vs. BMI Correlation")]:
            ax.clear()
            ax.set_title(title, fontsize=10, fontweight="bold", color="#334155")
            ax.text(0.5, 0.5, message, ha="center", va="center", color="#94a3b8", fontsize=9)
            ax.set_xticks([])
            ax.set_yticks([])

        self.canvas1.draw()
        self.canvas2.draw()
        self.canvas3.draw()

    def update_all_charts(self, username, records, current_category=None):
        """
        Updates all 3 embedded Matplotlib charts with real historical user data.

        :param username: Current selected user name
        :param records: List of record tuples (id, username, weight, height, bmi, category, timestamp)
        :param current_category: Active calculated category (optional)
        """
        if not records:
            self.draw_empty_placeholders(f"No records found for '{username}'")
            return

        # ----------------------------------------------------
        # CHART 1: BMI Category Highlight Bar Chart
        # ----------------------------------------------------
        self.ax1.clear()
        categories = ["Underweight\n(<18.5)", "Normal\n(18.5-24.9)", "Overweight\n(25-29.9)", "Obese\n(≥30)"]
        cat_keys = ["Underweight", "Normal Weight", "Overweight", "Obese"]

        # Count occurrences or highlight current active category
        if current_category is None:
            current_category = records[-1][5]

        category_colors = []
        for key in cat_keys:
            if key == current_category:
                fg, bg = get_category_color(key)
                category_colors.append(fg)
            else:
                category_colors.append("#cbd5e1")  # Light gray for non-active

        # Count occurrences in user history
        counts = [sum(1 for r in records if r[5] == k) for k in cat_keys]

        bars = self.ax1.bar(categories, counts, color=category_colors, width=0.55, edgecolor="#475569")
        self.ax1.set_title(f"1. Category Distribution ({username})", fontsize=10, fontweight="bold", color="#0f172a")
        self.ax1.set_ylabel("Count", fontsize=8, fontweight="bold")
        self.ax1.tick_params(axis='both', labelsize=8)
        self.ax1.grid(axis='y', linestyle='--', alpha=0.4)

        # Add data labels above bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                self.ax1.annotate(f"{int(height)}", (bar.get_x() + bar.get_width() / 2, height),
                                  xytext=(0, 2), textcoords="offset points", ha='center', fontsize=8, fontweight='bold')

        self.fig1.tight_layout()
        self.canvas1.draw()

        # ----------------------------------------------------
        # CHART 2: BMI Trend Line Graph
        # ----------------------------------------------------
        self.ax2.clear()
        dates = []
        bmis = []
        for idx, r in enumerate(records):
            ts = r[6]
            try:
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                dates.append(dt.strftime("%m/%d %H:%M"))
            except ValueError:
                dates.append(f"#{idx+1}")
            bmis.append(r[4])

        self.ax2.plot(dates, bmis, marker='o', color='#2563eb', linewidth=2, markersize=6, label="BMI")
        self.ax2.set_title(f"2. BMI Trend for {username}", fontsize=10, fontweight="bold", color="#0f172a")
        self.ax2.set_ylabel("BMI (kg/m²)", fontsize=8, fontweight="bold")
        self.ax2.tick_params(axis='x', rotation=25, labelsize=7)
        self.ax2.tick_params(axis='y', labelsize=8)
        self.ax2.grid(True, linestyle='--', alpha=0.4)

        # Add point annotations
        for i, val in enumerate(bmis):
            self.ax2.annotate(f"{val:.1f}", (dates[i], bmis[i]), xytext=(0, 5),
                              textcoords="offset points", ha='center', fontsize=7, fontweight='bold')

        self.fig2.tight_layout()
        self.canvas2.draw()

        # ----------------------------------------------------
        # CHART 3: Weight vs. BMI Correlation Graph
        # ----------------------------------------------------
        self.ax3.clear()
        weights = [r[2] for r in records]
        bmis_corr = [r[4] for r in records]

        # Sort points by weight for clean line plotting
        sorted_pairs = sorted(zip(weights, bmis_corr), key=lambda x: x[0])
        sw = [p[0] for p in sorted_pairs]
        sb = [p[1] for p in sorted_pairs]

        self.ax3.plot(sw, sb, color="#0d9488", linestyle="-", marker="s", markersize=6, linewidth=2, label="Weight vs BMI")
        self.ax3.scatter(weights, bmis_corr, color="#0f766e", s=40, zorder=5)

        self.ax3.set_title(f"3. Weight (kg) vs. BMI Correlation for {username}", fontsize=10, fontweight="bold", color="#0f172a")
        self.ax3.set_xlabel("Weight (kg)", fontsize=8, fontweight="bold")
        self.ax3.set_ylabel("BMI Value", fontsize=8, fontweight="bold")
        self.ax3.tick_params(axis='both', labelsize=8)
        self.ax3.grid(True, linestyle='--', alpha=0.4)

        for w, b in zip(weights, bmis_corr):
            self.ax3.annotate(f"({w:.1f}kg, {b:.1f})", (w, b), xytext=(4, 4),
                              textcoords="offset points", fontsize=7, color="#1e293b")

        self.fig3.tight_layout()
        self.canvas3.draw()


class BMICalculatorApp:
    """Main Desktop Dashboard Application for the Advanced BMI Calculator."""

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced BMI Calculator - Analytics Dashboard")
        self.root.geometry("1180x760")
        self.root.minsize(1000, 680)
        self.root.configure(bg="#f1f5f9")

        # Initialize Database Manager
        self.db_manager = DatabaseManager()

        # Style configuration
        self.setup_styles()

        # Build GUI layout
        self.create_widgets()

        # Load initial user records into UI
        self.refresh_dashboard()

    def setup_styles(self):
        """Configure TTK widget styles."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("TNotebook", background="#f1f5f9", borderwidth=0)
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[14, 6])
        self.style.map("TNotebook.Tab", background=[("selected", "#ffffff")], foreground=[("selected", "#2563eb")])

        self.style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#e2e8f0", foreground="#1e293b")
        self.style.configure("Treeview", font=("Segoe UI", 9), rowheight=24)

    def create_widgets(self):
        """Construct main dashboard layout."""
        # Top Header Banner
        header = tk.Frame(self.root, bg="#1e293b", pady=12, padx=20)
        header.pack(fill=tk.X)

        title = tk.Label(
            header,
            text="⚖️ Advanced BMI Calculator & Analytics Dashboard",
            font=("Segoe UI", 16, "bold"),
            fg="#ffffff",
            bg="#1e293b"
        )
        title.pack(side=tk.LEFT)

        subtitle = tk.Label(
            header,
            text="Oasis Infobyte Internship Task 2 (Advanced Tier)",
            font=("Segoe UI", 9, "italic"),
            fg="#94a3b8",
            bg="#1e293b"
        )
        subtitle.pack(side=tk.RIGHT, pady=(4, 0))

        # Main Body Container (Split into Left Sidebar Form and Right Notebook Dashboard)
        main_body = tk.Frame(self.root, bg="#f1f5f9", pady=10, padx=12)
        main_body.pack(fill=tk.BOTH, expand=True)

        # ----------------------------------------------------
        # LEFT SIDEBAR PANEL (Controls & Summary Metrics)
        # ----------------------------------------------------
        left_panel = tk.Frame(main_body, bg="#ffffff", bd=1, relief=tk.SOLID, padx=16, pady=16)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.config(width=310)

        tk.Label(left_panel, text="User Input Form", font=("Segoe UI", 12, "bold"), bg="#ffffff", fg="#0f172a").pack(anchor=tk.W, pady=(0, 10))

        # User Name Field
        tk.Label(left_panel, text="User Name:", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#475569").pack(anchor=tk.W)
        self.name_var = tk.StringVar()
        self.name_combo = ttk.Combobox(left_panel, textvariable=self.name_var, font=("Segoe UI", 10), width=26)
        self.name_combo.pack(fill=tk.X, pady=(2, 10))
        self.name_combo.bind("<<ComboboxSelected>>", lambda e: self.on_user_selected())

        # Weight Field (kg)
        tk.Label(left_panel, text="Weight (kg):", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#475569").pack(anchor=tk.W)
        self.weight_var = tk.StringVar()
        self.weight_entry = ttk.Entry(left_panel, textvariable=self.weight_var, font=("Segoe UI", 10))
        self.weight_entry.pack(fill=tk.X, pady=(2, 10))

        # Height Field (meters)
        tk.Label(left_panel, text="Height (meters):", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#475569").pack(anchor=tk.W)
        self.height_var = tk.StringVar()
        self.height_entry = ttk.Entry(left_panel, textvariable=self.height_var, font=("Segoe UI", 10))
        self.height_entry.pack(fill=tk.X, pady=(2, 14))

        # Action Buttons
        calc_btn = tk.Button(
            left_panel, text="Calculate & Save BMI", font=("Segoe UI", 10, "bold"),
            bg="#2563eb", fg="#ffffff", activebackground="#1d4ed8", activeforeground="#ffffff",
            relief=tk.FLAT, pady=7, cursor="hand2", command=self.handle_calculate
        )
        calc_btn.pack(fill=tk.X, pady=(0, 6))

        clear_btn = tk.Button(
            left_panel, text="Clear Form", font=("Segoe UI", 9, "bold"),
            bg="#64748b", fg="#ffffff", activebackground="#475569", activeforeground="#ffffff",
            relief=tk.FLAT, pady=6, cursor="hand2", command=self.clear_fields
        )
        clear_btn.pack(fill=tk.X, pady=(0, 14))

        # Separator
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=6)

        # Quick Summary Cards Panel
        tk.Label(left_panel, text="Current Metrics", font=("Segoe UI", 11, "bold"), bg="#ffffff", fg="#0f172a").pack(anchor=tk.W, pady=(4, 6))

        self.summary_card = tk.Frame(left_panel, bg="#f8fafc", bd=1, relief=tk.SOLID, pady=10, padx=10)
        self.summary_card.pack(fill=tk.X, pady=(0, 10))

        self.bmi_val_lbl = tk.Label(self.summary_card, text="--.--", font=("Segoe UI", 22, "bold"), bg="#f8fafc", fg="#0f172a")
        self.bmi_val_lbl.pack()

        self.category_badge = tk.Label(
            self.summary_card, text="No calculation yet", font=("Segoe UI", 9, "bold"),
            bg="#e2e8f0", fg="#475569", padx=8, pady=3
        )
        self.category_badge.pack(pady=4)

        self.metrics_lbl = tk.Label(
            self.summary_card, text="Height: -- m | Weight: -- kg", font=("Segoe UI", 8),
            bg="#f8fafc", fg="#64748b"
        )
        self.metrics_lbl.pack(pady=(2, 0))

        # Additional Management Buttons on Left
        csv_btn = tk.Button(
            left_panel, text="📁 Export History to CSV", font=("Segoe UI", 9, "bold"),
            bg="#0d9488", fg="#ffffff", activebackground="#0f766e", activeforeground="#ffffff",
            relief=tk.FLAT, pady=6, cursor="hand2", command=self.export_csv
        )
        csv_btn.pack(fill=tk.X, pady=(4, 6))

        reset_btn = tk.Button(
            left_panel, text="🗑 Clear User History", font=("Segoe UI", 9, "bold"),
            bg="#ef4444", fg="#ffffff", activebackground="#dc2626", activeforeground="#ffffff",
            relief=tk.FLAT, pady=6, cursor="hand2", command=self.reset_history
        )
        reset_btn.pack(fill=tk.X)

        # ----------------------------------------------------
        # RIGHT MAIN AREA (Notebook with Charts & History Table)
        # ----------------------------------------------------
        right_panel = tk.Frame(main_body, bg="#f1f5f9")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # TAB 1: Analytics Dashboard (Embedded Charts)
        self.tab_charts = tk.Frame(self.notebook, bg="#f8fafc")
        self.notebook.add(self.tab_charts, text="📊 Analytics Dashboard")

        self.charts_frame = EmbeddedChartsFrame(self.tab_charts)
        self.charts_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # TAB 2: History Records Table
        self.tab_history = tk.Frame(self.notebook, bg="#ffffff", padx=10, pady=10)
        self.notebook.add(self.tab_history, text="📜 History Records & Data")

        self.setup_history_tab()

    def setup_history_tab(self):
        """Constructs History Table, Filters, and Management tools in Tab 2."""
        top_filter = tk.Frame(self.tab_history, bg="#ffffff", pady=6)
        top_filter.pack(fill=tk.X)

        tk.Label(top_filter, text="Filter by User:", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#475569").pack(side=tk.LEFT, padx=(0, 6))

        self.history_user_var = tk.StringVar(value="All Users")
        self.history_user_combo = ttk.Combobox(
            top_filter, textvariable=self.history_user_var, state="readonly", width=20, font=("Segoe UI", 10)
        )
        self.history_user_combo.pack(side=tk.LEFT, padx=4)
        self.history_user_combo.bind("<<ComboboxSelected>>", lambda e: self.load_history_table())

        refresh_btn = ttk.Button(top_filter, text="Refresh", command=self.refresh_dashboard)
        refresh_btn.pack(side=tk.LEFT, padx=6)

        del_record_btn = tk.Button(
            top_filter, text="Delete Selected Record", font=("Segoe UI", 9),
            bg="#ef4444", fg="#ffffff", relief=tk.FLAT, padx=8, pady=4, cursor="hand2",
            command=self.delete_selected_record
        )
        del_record_btn.pack(side=tk.RIGHT)

        # Table Treeview
        tree_container = tk.Frame(self.tab_history, bg="#ffffff", bd=1, relief=tk.SOLID)
        tree_container.pack(fill=tk.BOTH, expand=True, pady=8)

        columns = ("id", "timestamp", "username", "weight", "height", "bmi", "category")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=16)

        self.tree.heading("id", text="ID")
        self.tree.heading("timestamp", text="Date / Time")
        self.tree.heading("username", text="User Name")
        self.tree.heading("weight", text="Weight (kg)")
        self.tree.heading("height", text="Height (m)")
        self.tree.heading("bmi", text="BMI")
        self.tree.heading("category", text="Category")

        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("timestamp", width=150, anchor=tk.CENTER)
        self.tree.column("username", width=120, anchor=tk.W)
        self.tree.column("weight", width=100, anchor=tk.CENTER)
        self.tree.column("height", width=100, anchor=tk.CENTER)
        self.tree.column("bmi", width=80, anchor=tk.CENTER)
        self.tree.column("category", width=130, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def refresh_user_comboboxes(self):
        """Updates user suggestions in input combobox and filter combobox."""
        users = self.db_manager.get_all_usernames()
        self.name_combo["values"] = users
        self.history_user_combo["values"] = ["All Users"] + users

    def refresh_dashboard(self):
        """Refreshes dropdowns, history table, and embedded Matplotlib charts."""
        self.refresh_user_comboboxes()
        self.load_history_table()
        self.update_embedded_charts()

    def on_user_selected(self):
        """Triggers chart updates when user chooses a name from dropdown."""
        user = self.name_var.get().strip()
        if user:
            self.history_user_var.set(user)
            self.refresh_dashboard()

    def update_embedded_charts(self, current_category=None):
        """Fetches active user records and renders all 3 embedded charts."""
        active_user = self.name_var.get().strip() or self.history_user_var.get()
        if active_user == "All Users" or not active_user:
            users = self.db_manager.get_all_usernames()
            active_user = users[0] if users else "All Users"

        records = self.db_manager.get_user_records(active_user)
        self.charts_frame.update_all_charts(active_user, records, current_category)

    def load_history_table(self):
        """Populates Treeview with SQLite database rows."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        selected_user = self.history_user_var.get()
        records = self.db_manager.get_user_records(selected_user)

        for row in records:
            # row: (id, username, weight, height, bmi, category, timestamp)
            self.tree.insert("", tk.END, values=(
                row[0], row[6], row[1], f"{row[2]:.1f}", f"{row[3]:.2f}", f"{row[4]:.2f}", row[5]
            ))

    def validate_inputs(self):
        """
        Validates user inputs.
        Rejects empty, non-numeric, <= 0, and unrealistic values.
        """
        raw_name = self.name_var.get().strip()
        raw_weight = self.weight_var.get().strip()
        raw_height = self.height_var.get().strip()

        if not raw_name:
            messagebox.showerror("Input Error", "Please enter a User Name.")
            self.name_combo.focus_set()
            return False, None, None, None

        if not raw_weight:
            messagebox.showerror("Input Error", "Please enter Weight in kilograms.")
            self.weight_entry.focus_set()
            return False, None, None, None

        if not raw_height:
            messagebox.showerror("Input Error", "Please enter Height in meters.")
            self.height_entry.focus_set()
            return False, None, None, None

        try:
            weight = float(raw_weight)
        except ValueError:
            messagebox.showerror("Input Error", "Weight must be a valid numeric number (e.g., 70.5).")
            self.weight_entry.focus_set()
            return False, None, None, None

        try:
            height = float(raw_height)
        except ValueError:
            messagebox.showerror("Input Error", "Height must be a valid numeric number (e.g., 1.75).")
            self.height_entry.focus_set()
            return False, None, None, None

        if weight <= 0:
            messagebox.showerror("Input Error", "Weight must be greater than zero.")
            self.weight_entry.focus_set()
            return False, None, None, None

        if height <= 0:
            messagebox.showerror("Input Error", "Height must be greater than zero.")
            self.height_entry.focus_set()
            return False, None, None, None

        if height > 3.0:
            messagebox.showwarning(
                "Height Warning",
                "Height is entered in meters (e.g., 1.75 m). Please make sure height is not in centimeters!"
            )
            return False, None, None, None

        if weight > 500.0 or weight < 10.0:
            messagebox.showwarning("Range Warning", "Please enter a realistic body weight in kilograms (10kg - 500kg).")
            return False, None, None, None

        return True, raw_name, weight, height

    def handle_calculate(self):
        """Calculates BMI, persists to SQLite DB, and updates UI & all 3 embedded charts instantly."""
        is_valid, username, weight, height = self.validate_inputs()
        if not is_valid:
            return

        bmi, category = calculate_bmi(weight, height)

        saved = self.db_manager.add_record(username, weight, height, bmi, category)
        if saved:
            fg_color, bg_color = get_category_color(category)

            # Update Metrics Display
            self.bmi_val_lbl.config(text=f"{bmi:.2f}", fg=fg_color)
            self.category_badge.config(text=f"Category: {category}", bg=bg_color, fg=fg_color)
            self.metrics_lbl.config(text=f"Height: {height:.2f} m | Weight: {weight:.1f} kg")

            # Update filter to current user and refresh dashboard + charts
            self.history_user_var.set(username)
            self.refresh_dashboard()
            self.update_embedded_charts(current_category=category)

            messagebox.showinfo("Success", f"BMI calculated for '{username}': {bmi:.2f} ({category})\nRecord saved to database!")

    def clear_fields(self):
        """Resets input entries."""
        self.name_var.set("")
        self.weight_var.set("")
        self.height_var.set("")
        self.bmi_val_lbl.config(text="--.--", fg="#0f172a")
        self.category_badge.config(text="No calculation yet", bg="#e2e8f0", fg="#475569")
        self.metrics_lbl.config(text="Height: -- m | Weight: -- kg")
        self.name_combo.focus_set()

    def export_csv(self):
        """Prompts for save location and exports BMI records to CSV."""
        selected_user = self.history_user_var.get()
        default_filename = f"BMI_History_{selected_user.replace(' ', '_')}.csv"

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialfile=default_filename,
            title="Export BMI History to CSV"
        )

        if filepath:
            count = self.db_manager.export_to_csv(filepath, selected_user)
            if count > 0:
                messagebox.showinfo("Export Successful", f"Successfully exported {count} record(s) to:\n{filepath}")
            elif count == 0:
                messagebox.showwarning("Export Warning", f"No records found to export for '{selected_user}'.")

    def delete_selected_record(self):
        """Deletes highlighted record in Treeview table."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a record from the history table to delete.")
            return

        record_values = self.tree.item(selected_item[0], "values")
        record_id = record_values[0]
        user_name = record_values[2]

        if messagebox.askyesno("Confirm Delete", f"Delete record ID #{record_id} for '{user_name}'?"):
            if self.db_manager.delete_record(record_id):
                self.refresh_dashboard()

    def reset_history(self):
        """Clears all records for active user or all users."""
        selected_user = self.history_user_var.get()
        target_name = f"user '{selected_user}'" if selected_user != "All Users" else "ALL users"

        if messagebox.askyesno("Confirm Reset", f"Are you sure you want to PERMANENTLY delete history for {target_name}?"):
            if self.db_manager.clear_user_history(selected_user):
                messagebox.showinfo("Reset Complete", f"History for {target_name} has been cleared.")
                self.refresh_dashboard()


def main():
    """Main entry point for running the Advanced Dashboard BMI Calculator."""
    root = tk.Tk()
    app = BMICalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
