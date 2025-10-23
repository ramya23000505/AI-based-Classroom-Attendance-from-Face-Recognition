### Name: RAMYA R
### Reg No: 212223230169

# AI-Based Classroom Attendance System

A complete web application that uses facial recognition to automate classroom attendance. Built with Python, Flask, and the `face_recognition` library.

![Project Demo](demo/demo.gif)
*(You should replace this with a link to your own demo video or a GIF you create)*

---

## Table of Contents

- [Objective](#objective)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
- [How to Use](#how-to-use)
- [License](#license)

---

## Objective

To build a system that automatically marks classroom attendance using AI-based face recognition. This project aims to reduce the manual time spent on roll calls and improve the accuracy of attendance records.

---

## Features

* **Student Enrollment:** Easily enroll students by adding their photos to a dataset.
* **AI-Powered Recognition:** Uses a pre-trained face recognition model to identify multiple students from a single classroom photo.
* **Web Dashboard:** A simple web interface for teachers to:
    * Upload a class photo to take attendance.
    * View daily attendance reports.
    * Manually correct any misidentified or missed students.
    * View reports from previous days.
* **Database Storage:** All attendance records are stored in a persistent SQLite database.
* **Report Export:** Export daily attendance reports to a `.csv` file.

---

## Tech Stack

* **Backend:** Python, Flask
* **AI/Face Recognition:** `face_recognition`, `opencv-python`, `numpy`
* **Database:** SQLite
* **Frontend:** HTML, CSS, JavaScript (vanilla)
* **Data Handling:** `pandas` (for CSV export)

---

## System Architecture

The system works in two main phases:

1.  **Enrollment (One-time setup):**
    * Teacher adds student photos (e.g., `John_Smith_101.jpg`) to the `dataset/` folder.
    * The `encode_faces.py` script is run once.
    * It finds the face in each photo, creates a 128-point facial encoding, and saves all encodings to an `encodings.pickle` file.

2.  **Recognition (Daily use):**
    * Teacher uploads a classroom photo via the web dashboard.
    * The Flask server receives the image.
    * It finds all faces in the uploaded photo and generates encodings for them.
    * It compares these "unknown" encodings against the list of "known" encodings from the pickle file.
    * It identifies the students and marks them "Present." All other students are marked "Absent."
    * The results are saved to the `attendance.db` database and displayed on the dashboard.



---

## Project Structure

Here is the file structure for the project:

```
ai-face-recognition-attendance/
│
├── .gitignore          # Tells Git which files to ignore
├── LICENSE             # Your open-source license
├── README.md           # This file
├── requirements.txt    # List of all Python dependencies
│
├── app.py              # The main Flask web server
├── attendance.db       # The SQLite database (created on first run)
├── encodings.pickle    # The generated face encodings (created by utility script)
│
├── dataset/            # Folder to store all known student images
│   ├── Lisa_Ray_102.jpg
│   └── John_Smith_101.jpg
│
├── templates/          # Folder for Flask's HTML files
│   └── index.html
│
└── utils/              # Utility scripts
    └── encode_faces.py
```

---

## Setup and Installation

Follow these steps to get the project running on your local machine.

**1. Clone the Repository:**
```bash
git clone [https://github.com/YourUsername/ai-face-recognition-attendance.git](https://github.com/YourUsername/ai-face-recognition-attendance.git)
cd ai-face-recognition-attendance
```

**2. Create a Python Virtual Environment:**
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

**3. Install Dependencies:**
```bash
pip install -r requirements.txt
```
*(Note: `dlib`, a dependency of `face_recognition`, may require `cmake` to be installed on your system. If you run into issues, install `cmake` first.)*

---

## How to Use

**Step 1: Enroll Students**
* Add 1-5 clear photos of each student to the `dataset/` folder.
* **IMPORTANT:** Name the files in the format: `StudentName_StudentID.jpg` (e.g., `Elon_Musk_999.jpg`).

**Step 2: Generate Face Encodings**
* Run the encoding utility script from your terminal. This only needs to be done once, or anytime you add new students.
```bash
python utils/encode_faces.py
```
* This will create (or overwrite) the `encodings.pickle` file.

**Step 3: Run the Web Application**
* Start the Flask server.
```bash
python app.py
```

**Step 4: Use the Dashboard**
* Open your web browser and go to `http://127.0.0.1:5000`.
* You can now upload a classroom photo to mark attendance, view the report, and export it to CSV.

---

