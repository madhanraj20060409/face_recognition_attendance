"""
AI Face Recognition Attendance System
Backend: Python Flask + OpenCV
Author: Hackathon Project
"""

from flask import Flask, render_template, request, jsonify, send_file
import cv2
import numpy as np
import os
import csv
import base64
from datetime import datetime, date
import io
from scipy.spatial import distance

# ─────────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────────
app = Flask(__name__)

IMAGES_FOLDER = "images"          # Where student photos are stored
ATTENDANCE_FILE = "attendance.csv" # CSV attendance log

os.makedirs(IMAGES_FOLDER, exist_ok=True)

# ─────────────────────────────────────────────
# MediaPipe Face Detection Setup
# ─────────────────────────────────────────────
try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    
    # Load the face detector model
    base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
    options = vision.FaceLandmarkerOptions(base_options=base_options, output_face_blendshapes=True)
    detector = vision.FaceLandmarker.create_from_options(options)
except:
    # Fallback to simpler face detection using OpenCV
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ─────────────────────────────────────────────
# Helper: Extract face detection from image
# ─────────────────────────────────────────────
def get_face_embedding(image_rgb):
    """
    Detect face using OpenCV cascade classifier.
    Returns: (x, y, w, h) if face found, None otherwise
    """
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(50, 50))
    
    if len(faces) > 0:
        x, y, w, h = faces[0]  # Return first detected face
        return (x, y, w, h)
    return None

# ─────────────────────────────────────────────
# Helper: Get histogram of face region for comparison
# ─────────────────────────────────────────────
def get_face_histogram(image, face_box):
    """Extract histogram features from face region for matching."""
    if face_box is None:
        return None
    x, y, w, h = face_box
    x = max(0, x)
    y = max(0, y)
    face_roi = image[y:y+h, x:x+w]
    if face_roi.size == 0:
        return None
    # Convert to grayscale and compute histogram
    gray = cv2.cvtColor(face_roi, cv2.COLOR_RGB2GRAY)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    return hist

# ─────────────────────────────────────────────
# Helper: Load all known faces from images folder
# ─────────────────────────────────────────────
def load_known_faces():
    """
    Reads all images in the images/ folder,
    extracts face histograms, and returns two lists:
      - known_histograms: list of face histograms
      - known_names:      matching student names
    """
    known_histograms = []
    known_names = []

    for filename in os.listdir(IMAGES_FOLDER):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            filepath = os.path.join(IMAGES_FOLDER, filename)
            try:
                img = cv2.imread(filepath)
                if img is None:
                    continue
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                face_box = get_face_embedding(rgb_img)
                if face_box:
                    hist = get_face_histogram(rgb_img, face_box)
                    if hist is not None:
                        known_histograms.append(hist)
                        name = os.path.splitext(filename)[0].replace("_", " ")
                        known_names.append(name)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue

    return known_histograms, known_names


# ─────────────────────────────────────────────
# Helper: Ensure attendance CSV has header
# ─────────────────────────────────────────────
def init_attendance_csv():
    """Create CSV with header if it doesn't exist or is empty."""
    if not os.path.exists(ATTENDANCE_FILE) or os.path.getsize(ATTENDANCE_FILE) == 0:
        with open(ATTENDANCE_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Date", "Time", "Status"])

init_attendance_csv()


# ─────────────────────────────────────────────
# Helper: Check if student already marked today
# ─────────────────────────────────────────────
def already_marked_today(name):
    """Returns True if student was already marked present today."""
    today = str(date.today())
    if not os.path.exists(ATTENDANCE_FILE):
        return False
    with open(ATTENDANCE_FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2 and row[0] == name and row[1] == today:
                return True
    return False


# ─────────────────────────────────────────────
# Helper: Mark attendance in CSV
# ─────────────────────────────────────────────
def mark_attendance(name):
    """Appends a new attendance row for the student."""
    now = datetime.now()
    with open(ATTENDANCE_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, str(now.date()), now.strftime("%H:%M:%S"), "Present"])


# ─────────────────────────────────────────────
# ROUTES – Pages
# ─────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/attendance")
def attendance():
    return render_template("attendance.html")

@app.route("/report")
def report():
    return render_template("report.html")


# ─────────────────────────────────────────────
# API: Register a new student
# ─────────────────────────────────────────────
@app.route("/api/register", methods=["POST"])
def api_register():
    """
    Receives: { name: "John Doe", image: "<base64 jpg>" }
    Saves image to images/ folder.
    Returns: success/error message
    """
    data = request.get_json()
    name = data.get("name", "").strip()
    image_data = data.get("image", "")

    if not name:
        return jsonify({"success": False, "message": "Name is required."})
    if not image_data:
        return jsonify({"success": False, "message": "Image is required."})

    try:
        # Decode base64 image
        if "," in image_data:
            image_data = image_data.split(",")[1]  # Remove "data:image/jpeg;base64,"
        img_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Convert BGR (OpenCV) → RGB (MediaPipe)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Check that a face exists in the photo
        face_box = get_face_embedding(rgb_img)
        if face_box is None:
            return jsonify({"success": False, "message": "No face detected. Please try again with a clearer photo."})

        # Save image as Name.jpg (spaces replaced with underscores)
        filename = name.replace(" ", "_") + ".jpg"
        filepath = os.path.join(IMAGES_FOLDER, filename)
        cv2.imwrite(filepath, img)

        return jsonify({"success": True, "message": f"Student '{name}' registered successfully!"})

    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"})


# ─────────────────────────────────────────────
# API: Recognize face and mark attendance
# ─────────────────────────────────────────────
@app.route("/api/recognize", methods=["POST"])
def api_recognize():
    """
    Receives: { image: "<base64 jpg>" }
    Detects faces, matches against known students,
    marks attendance if matched.
    Returns: list of recognized students
    """
    data = request.get_json()
    image_data = data.get("image", "")

    if not image_data:
        return jsonify({"success": False, "message": "No image provided."})

    try:
        # Decode base64 image
        if "," in image_data:
            image_data = image_data.split(",")[1]
        img_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Load known faces
        known_histograms, known_names = load_known_faces()
        if not known_histograms:
            return jsonify({"success": False, "message": "No students registered yet."})

        # Detect face in the frame
        face_box = get_face_embedding(rgb_img)
        if face_box is None:
            return jsonify({"success": True, "results": [], "message": "No faces detected in frame."})

        # Get histogram of detected face
        test_hist = get_face_histogram(rgb_img, face_box)
        if test_hist is None:
            return jsonify({"success": True, "results": [], "message": "Could not extract face features."})

        # Compare with all known faces using histogram distance
        results = []
        min_distance = float('inf')
        best_match_index = -1
        
        for idx, known_hist in enumerate(known_histograms):
            # Calculate histogram distance (lower is better)
            dist = distance.euclidean(test_hist, known_hist)
            if dist < min_distance:
                min_distance = dist
                best_match_index = idx

        # Threshold for matching (adjust based on testing)
        if best_match_index >= 0 and min_distance < 50:
            name = known_names[best_match_index]
            
            if already_marked_today(name):
                status = "Already Marked"
            else:
                mark_attendance(name)
                status = "Marked Present"
            
            results.append({"name": name, "status": status})
        else:
            results.append({"name": "Unknown", "status": "Not Recognized"})

        return jsonify({"success": True, "results": results})

    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"})


# ─────────────────────────────────────────────
# API: Get attendance report
# ─────────────────────────────────────────────
@app.route("/api/report", methods=["GET"])
def api_report():
    """
    Returns all attendance records as JSON.
    Optional query param: ?date=YYYY-MM-DD to filter by date.
    """
    filter_date = request.args.get("date", "")
    records = []

    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if filter_date and row.get("Date") != filter_date:
                    continue
                records.append(row)

    return jsonify({"success": True, "records": records})


# ─────────────────────────────────────────────
# API: Get list of registered students
# ─────────────────────────────────────────────
@app.route("/api/students", methods=["GET"])
def api_students():
    """Returns a list of all registered student names."""
    students = []
    for filename in os.listdir(IMAGES_FOLDER):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            name = os.path.splitext(filename)[0].replace("_", " ")
            students.append(name)
    return jsonify({"success": True, "students": students})


# ─────────────────────────────────────────────
# API: Download attendance as CSV
# ─────────────────────────────────────────────
@app.route("/api/download", methods=["GET"])
def api_download():
    """Sends the attendance.csv file for download."""
    if os.path.exists(ATTENDANCE_FILE):
        return send_file(ATTENDANCE_FILE, as_attachment=True, download_name="attendance.csv")
    return jsonify({"success": False, "message": "No attendance file found."})


# ─────────────────────────────────────────────
# Run the app
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  AI Face Attendance System Starting...")
    print("  Open: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)
