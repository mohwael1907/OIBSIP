# Advanced BMI Calculator - Desktop Analytics Dashboard

> **OASIS INFOBYTE Python Programming Internship — Task 2 (Advanced Tier)**  
> A desktop Body Mass Index (BMI) calculator application built with Python 3, Tkinter, SQLite, and Matplotlib.

---

## 📌 Project Overview & Objective

The **Advanced BMI Calculator** is a multi-user desktop dashboard application designed to calculate, track, analyze, and visualize Body Mass Index (BMI) data. Built using native Python tools (`tkinter`, `sqlite3`, and `matplotlib`), the application features real-time embedded data visualizations and CSV export capabilities.

### Key Objectives
1. **Accurate Calculation**: Calculate precise BMI values using standard formulas and categorize health ranges according to WHO criteria.
2. **Embedded Real-Time Analytics**: Render 3 live Matplotlib charts directly inside the GUI application dashboard.
3. **Data Persistence**: Store calculation records locally in a SQLite database (`bmi_records.db`).
4. **Data Management & Export**: Allow multi-user filtering, record deletion, history clearing, and CSV exports.

---

## ⭐ Key Features (Required Checklist)

### 1. 📊 BMI Category Chart (Embedded)
- An embedded Matplotlib bar chart showing the standard WHO BMI categories (*Underweight*, *Normal Weight*, *Overweight*, *Obese*).
- **Dynamic Category Highlight**: Automatically highlights the user's active calculated category in vibrant color while keeping other categories muted.

### 2. 📈 BMI Trend Graph (Embedded)
- A live line chart tracking individual user BMI progression over time.
- **X-axis**: Calculation timestamp (date/time).
- **Y-axis**: Calculated BMI value.
- Automatically updates upon every calculation or user selection.

### 3. ⚖️ Weight vs. BMI Graph (Embedded)
- A correlation chart showing the direct relationship between body weight (kg) on the X-axis and BMI on the Y-axis.
- Renders historical weight-to-BMI data points for the active user.

### 4. 🗄️ Persistent BMI History (SQLite)
- Automatically creates and manages a local SQLite database (`bmi_records.db`).
- Stores User Name, Weight (kg), Height (m), BMI, Category, and Timestamp.
- Prevents data loss when closing and reopening the application.

### 5. 📁 CSV Export Capability
- Export user calculation history to a standard `.csv` file via a native file dialog (`filedialog.asksaveasfilename`).
- Useful for external medical records, spreadsheet analysis, or personal backups.

---

## 🚀 Additional Advanced Features

- **Responsive Two-Panel Dashboard**: Features an input control sidebar alongside a tabbed main area (`ttk.Notebook`).
- **Interactive Data Table (`ttk.Treeview`)**: View, filter by user name, or delete individual historical records.
- **Reset / Clear History**: Safely wipe calculation logs for a specific user or all users with confirmation prompts.
- **Strict Input Validation**:
  - Detects empty fields.
  - Rejects non-numeric characters.
  - Rejects zero and negative numbers.
  - Warns if height is entered in centimeters instead of meters (> 3.0 m).
  - Validates realistic weight ranges (10 kg – 500 kg).

---

## 🛠️ Technologies Used

| Technology | Purpose |
| :--- | :--- |
| **Python 3** | Core programming language |
| **Tkinter & TTK** | Native desktop GUI framework & dashboard layout |
| **SQLite3** | Relational database for persistent storage (Standard Library) |
| **Matplotlib** | Data visualization library (`FigureCanvasTkAgg` embedded canvas) |
| **CSV Module** | Standard library module for exporting data files |

---

## 📐 BMI Calculation & Categories

The application uses the official Body Mass Index formula:

$$\text{BMI} = \frac{\text{weight (kg)}}{\text{height (m)}^2}$$

### Health Category Classification

| Category | BMI Range | Visual Badge Color |
| :--- | :--- | :--- |
| **Underweight** | $\text{BMI} < 18.5$ | 🔵 Soft Blue (`#1d6f8a`) |
| **Normal Weight** | $18.5 \le \text{BMI} < 25.0$ | 🟢 Soft Green (`#15803d`) |
| **Overweight** | $25.0 \le \text{BMI} < 30.0$ | 🟠 Soft Orange (`#c2410c`) |
| **Obese** | $\text{BMI} \ge 30.0$ | 🔴 Soft Red (`#b91c1c`) |

---

## 🗄️ Database Schema

SQLite table schema (`bmi_records.db`):

```sql
CREATE TABLE IF NOT EXISTS bmi_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    weight REAL NOT NULL,
    height REAL NOT NULL,
    bmi REAL NOT NULL,
    category TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
```

---

## 📥 Installation & Requirements

### Prerequisites
- Python 3.8 or higher.

### Step 1: Navigate to Project Directory
Open **Windows PowerShell** or Command Prompt:
```powershell
cd c:\Users\i7\Desktop\task2\Python-Task2-BMICalculator
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## ▶️ How to Run the Application

Execute the main python script:

```powershell
python bmi_calculator.py
```

---

## 📁 Project Structure

```
Python-Task2-BMICalculator/
│
├── bmi_calculator.py    # Main dashboard application code (Tkinter, SQLite, Matplotlib)
├── requirements.txt      # Dependency manifest (matplotlib)
├── README.md             # Detailed documentation & project manual
├── bmi_records.db        # SQLite database (auto-generated)
└── screenshots/          # Directory for UI screenshots (.gitkeep)
```

---

## 🖼️ Screenshots & Demo Sections

Place application screenshots inside `screenshots/`:
- `screenshots/dashboard_analytics.png` - Analytics dashboard with 3 embedded charts.
- `screenshots/history_table.png` - History records Treeview tab.
- `screenshots/csv_export_demo.png` - CSV file export feature.

---

## 🎓 OASIS INFOBYTE Internship Information

- **Internship**: OASIS INFOBYTE Python Programming Internship
- **Task Number**: Task 2 (Advanced Tier)
- **Project Name**: Advanced BMI Calculator & Analytics Dashboard
