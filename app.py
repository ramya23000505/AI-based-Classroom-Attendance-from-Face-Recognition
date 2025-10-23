# app.py
from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import os
import cv2
import numpy as np
import face_recognition
import pickle
from datetime import datetime
import pandas as pd
import io

app = Flask(__name__)

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    # Student table
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    # Attendance log table
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            name TEXT,
            date TEXT,
            status TEXT,
            FOREIGN KEY (student_id) REFERENCES students (student_id)
        )
    ''')
    conn.commit()
    conn.close()

# --- Load Known Faces ---
data = pickle.loads(open('encodings.pickle', "rb").read())
known_encodings = data['encodings']
known_names = data['names']

# --- Helper Function to Add Students to DB (from dataset) ---
def sync_students_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    for name_id in known_names:
        try:
            name, student_id = name_id.rsplit('_', 1)
            # Add student if not already exists
            c.execute("INSERT OR IGNORE INTO students (student_id, name) VALUES (?, ?)", (student_id, name))
        except ValueError:
            print(f"Skipping {name_id}, not in 'Name_ID' format.")
    conn.commit()
    conn.close()

# --- Web Page Routes ---
@app.route('/')
def index():
    # Renders the main dashboard page
    return render_template('index.html')

# --- API Endpoints ---

@app.route('/api/mark_attendance', methods=['POST'])
def mark_attendance():
    if 'file' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['file']
    
    # Read the image file in memory
    filestr = file.read()
    npimg = np.frombuffer(filestr, np.uint8)
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Find all faces and their encodings in the new image
    face_locations = face_recognition.face_locations(rgb_image)
    unknown_encodings = face_recognition.face_encodings(rgb_image, face_locations)

    today = datetime.now().strftime('%Y-%m-%d')
    present_students = set() # Use a set to avoid duplicates

    for encoding in unknown_encodings:
        # See if the face is a match for the known faces
        matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.5)
        name_id = "Unknown"

        face_distances = face_recognition.face_distance(known_encodings, encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name_id = known_names[best_match_index]
            present_students.add(name_id)

    # --- Log to Database ---
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    # Get full student list
    c.execute("SELECT student_id, name FROM students")
    all_students = c.fetchall()
    
    attendance_report = []

    for student_id, name in all_students:
        full_name_id = f"{name}_{student_id}"
        
        status = "Absent"
        if full_name_id in present_students:
            status = "Present"
        
        # Check if record for today already exists
        c.execute("SELECT * FROM attendance_logs WHERE student_id = ? AND date = ?", (student_id, today))
        if c.fetchone() is None:
            # If not, insert new record
            c.execute("INSERT INTO attendance_logs (student_id, name, date, status) VALUES (?, ?, ?, ?)",
                      (student_id, name, today, status))
        
        attendance_report.append({"id": student_id, "name": name, "status": status})

    conn.commit()
    conn.close()

    return jsonify({"report": attendance_report})

@app.route('/api/get_report', methods=['GET'])
def get_report():
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row # To get results as dictionaries
    c = conn.cursor()
    
    c.execute("SELECT * FROM attendance_logs WHERE date = ?", (date,))
    report = [dict(row) for row in c.fetchall()]
    
    conn.close()
    return jsonify(report)

@app.route('/api/update_attendance', methods=['POST'])
def update_attendance():
    data = request.json
    log_id = data.get('log_id')
    new_status = data.get('status')
    
    if not log_id or not new_status:
        return jsonify({"error": "Missing data"}), 400

    try:
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute("UPDATE attendance_logs SET status = ? WHERE log_id = ?", (new_status, log_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Record updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/export_csv', methods=['GET'])
def export_csv():
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    conn = sqlite3.connect('attendance.db')
    # Use pandas to easily create a CSV
    df = pd.read_sql_query(f"SELECT name, student_id, status, date FROM attendance_logs WHERE date = '{date}'", conn)
    conn.close()
    
    output = io.BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return send_file(output, mimetype='text/csv',
                     download_name=f'attendance_{date}.csv', as_attachment=True)

if __name__ == '__main__':
    init_db()
    sync_students_db() # Sync dataset names with DB on startup
    app.run(debug=True)