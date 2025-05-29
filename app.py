from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='static')
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

def euclidean(pt1, pt2):
    # Helper function to calculate distance between two points
    from math import sqrt
    return sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)

@app.route('/upload', methods=['POST'])
def upload():
    if 'photo' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    import cv2
    import mediapipe as mp

    img = cv2.imread(filepath)
    if img is None:
        return jsonify({'error': 'Image could not be loaded.'}), 400

    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(static_image_mode=True) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if not results.multi_face_landmarks:
            return jsonify({'error': 'No face detected.'}), 400

        h, w, _ = img.shape
        lm = results.multi_face_landmarks[0].landmark

        # Landmark indices (from previous step)
        points = {
            "chin": 152,
            "forehead": 10,
            "left_cheek": 234,
            "right_cheek": 454,
            "left_eye_outer": 33,
            "left_eye_inner": 133,
            "right_eye_inner": 362,
            "right_eye_outer": 263,
            "nose_bridge": 168,
            "nose_tip": 2,
            "left_nostril": 97,
            "right_nostril": 326,
            "left_mouth": 61,
            "right_mouth": 291,
        }

        coords = {name: (int(lm[idx].x * w), int(lm[idx].y * h)) for name, idx in points.items()}

        # Distances for ratios
        face_height = euclidean(coords["chin"], coords["forehead"])
        face_width = euclidean(coords["left_cheek"], coords["right_cheek"])
        eye_width = euclidean(coords["left_eye_outer"], coords["right_eye_outer"])
        inter_eye = euclidean(coords["left_eye_inner"], coords["right_eye_inner"])
        nose_length = euclidean(coords["nose_bridge"], coords["nose_tip"])
        nose_width = euclidean(coords["left_nostril"], coords["right_nostril"])
        mouth_width = euclidean(coords["left_mouth"], coords["right_mouth"])

        # Golden Ratio
        PHI = 1.618

        def ratio_score(A, B):
            measured = A / B if A > B else B / A  # always > 1
            return round(1 - abs(measured - PHI) / PHI, 2), round(measured, 2)

        scores = []
        details = []

        # 1. Face Height / Face Width
        s, val = ratio_score(face_height, face_width)
        scores.append(s)
        details.append({"name": "Face Height / Face Width", "value": val, "score": s})

        # 2. Eye Width / Inter-Eye Distance
        s, val = ratio_score(eye_width, inter_eye)
        scores.append(s)
        details.append({"name": "Eye Width / Inter-Eye Distance", "value": val, "score": s})

        # 3. Nose Length / Nose Width
        s, val = ratio_score(nose_length, nose_width)
        scores.append(s)
        details.append({"name": "Nose Length / Nose Width", "value": val, "score": s})

        # 4. Mouth Width / Nose Width
        s, val = ratio_score(mouth_width, nose_width)
        scores.append(s)
        details.append({"name": "Mouth Width / Nose Width", "value": val, "score": s})

        harmony = round(sum(scores) / len(scores), 2)

        # Draw landmarks for feedback (optional)
        for pt in coords.values():
            cv2.circle(img, pt, 3, (0, 255, 0), -1)
        out_path = os.path.join(UPLOAD_FOLDER, "landmarked_" + file.filename)
        cv2.imwrite(out_path, img)

        return jsonify({
            "success": True,
            "harmony_score": harmony,
            "ratios": details,
            "landmarked_img": "landmarked_" + file.filename
        })
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
import os
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
if __name__ == '__main__':
    app.run(debug=True)