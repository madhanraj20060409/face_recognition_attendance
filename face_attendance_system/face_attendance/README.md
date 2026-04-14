# 🎓 AI Face Recognition Attendance System

A college hackathon project built with **Python Flask + OpenCV + Histogram-based Face Matching**.

---

## 📁 Project Structure

```
face_attendance/
├── static/
│     ├── style.css         ← All page styles
│     └── script.js         ← Shared JS utilities & animations
├── templates/
│     ├── index.html        ← Home page with stats
│     ├── register.html     ← Student registration with live camera
│     ├── attendance.html   ← Live attendance marking with auto-detect
│     └── report.html       ← Attendance report with filtering & download
├── images/                 ← Student face photos stored here (*.jpg)
├── attendance.csv          ← Attendance log (Name, Date, Time, Status)
├── app.py                  ← Flask backend with face detection & recognition
├── requirements.txt        ← Python dependencies
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Prerequisites
- **Python 3.7+** installed and added to PATH
- **Windows/Mac/Linux** supported

### 2. Navigate to project folder
```bash
cd face_attendance
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

**Dependencies:**
- `flask==2.3.3` - Web framework
- `opencv-python==4.8.1.78` - Face detection & image processing
- `numpy==1.24.4` - Array operations
- `scipy==1.13.1` - Histogram distance calculation

### 4. Run the application
```bash
python app.py
```

### 5. Open in browser
```
http://127.0.0.1:5000
```

---

## 🚀 How to Use

### Register a Student
1. Navigate to **`/register`**
2. Click **"Start Camera"** to activate webcam
3. **Capture a clear, front-facing photo** of the student
4. Enter the **student's name**
5. Click **"Register"**
6. Photo is saved to `images/` folder with the student's name

### Mark Attendance
1. Navigate to **`/attendance`**
2. Click **"Start Attendance"** to begin real-time face recognition
3. System **automatically detects faces** every 3 seconds
4. Recognized students are marked **"Present"** with timestamp
5. Each student is marked **only once per day** (no duplicates)
6. Unknown faces show as **"Not Recognized"**

### View & Download Reports
1. Navigate to **`/report`**
2. View all attendance records in a table
3. **(Optional)** Filter by date using the date picker
4. Click **"Download CSV"** to export attendance data

---

## 🔌 API Endpoints

| Method | Endpoint | Description | Payload |
|--------|----------|-------------|---------|
| GET | `/` | Home page | — |
| GET | `/register` | Registration page | — |
| GET | `/attendance` | Attendance page | — |
| GET | `/report` | Report page | — |
| **POST** | **/api/register** | **Register new student** | `{ name: "John Doe", image: "<base64 jpg>" }` |
| **POST** | **/api/recognize** | **Detect face & mark attendance** | `{ image: "<base64 jpg>" }` |
| **GET** | **/api/report** | **Get attendance records** | Query: `?date=YYYY-MM-DD` (optional) |
| **GET** | **/api/students** | **List all registered students** | — |
| **GET** | **/api/download** | **Download attendance.csv** | — |

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla/No Framework)
- **Backend**: Python Flask (Lightweight & Fast)
- **Face Detection**: OpenCV Haar Cascade Classifier
- **Face Recognition**: Histogram-based Matching (OpenCV)
- **Distance Metric**: Euclidean Distance (SciPy)
- **Data Storage**: CSV files (Simple & Portable)
- **Camera API**: HTML5 getUserMedia (WebRTC)

---

## 🔍 How Face Recognition Works

### Detection (OpenCV Haar Cascade)
- Detects face region in each frame
- Returns bounding box coordinates (x, y, w, h)
- Sensitivity: `minSize=(50, 50)` 

### Recognition (Histogram Matching)
1. **Registration Phase:**
   - Extract face region from photo
   - Convert to grayscale
   - Compute histogram (256 bins)
   - Store histogram alongside student name

2. **Recognition Phase:**
   - Compute histogram of detected face in camera frame
   - Compare with all stored histograms using **Euclidean Distance**
   - If distance < **50**: Match found (can be tuned)
   - Mark attendance if not already marked today

---

## 📊 Attendance CSV Format

```
Name,Date,Time,Status
John Doe,2025-04-14,09:30:45,Present
Jane Smith,2025-04-14,09:35:12,Present
John Doe,2025-04-13,09:25:33,Present
```

---

## 💡 Tips & Best Practices

✅ **For Better Recognition:**
- Use **good lighting** (avoid shadows on face)
- Register with **clear, front-facing** photos
- Keep face centered in frame during registration & attendance

✅ **Troubleshooting:**
- If face not detected: Move closer to camera, improve lighting
- If "Not Recognized": Re-register with clearer photo
- Adjust matching threshold in code: `if min_distance < 50:` (lower = stricter)

✅ **Performance:**
- System checks once per frame at ~30 FPS
- Attendance marked once per student per day (checked against CSV)
- No database needed (CSV is simple & portable)

---

## 📝 File Descriptions

- **`app.py`**: Main Flask app with routes, face detection, recognition logic
- **`script.js`**: Shared utilities (counter animations, nav highlighting, camera setup)
- **`style.css`**: Responsive design, camera preview styling
- **`*.html`**: Each page (index, register, attendance, report)
- **`attendance.csv`**: CSV log updated whenever attendance is marked

---