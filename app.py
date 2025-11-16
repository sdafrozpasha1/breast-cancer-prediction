from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_session import Session
import pickle
import numpy as np
from datetime import datetime
import os
import json

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True

# CORS configuration for production
cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:8000').split(',')
CORS(app, 
     supports_credentials=True,
     origins=cors_origins,
     allow_headers=['Content-Type'],
     methods=['GET', 'POST', 'OPTIONS'])

Session(app)
bcrypt = Bcrypt(app)

# Use file-based storage for persistence
from database import Database
db = Database()

# For backward compatibility
users_db = {}
predictions_db = {}

# Load existing data on startup
def load_data():
    global users_db, predictions_db
    try:
        import json
        import os
        if os.path.exists('data/users.json'):
            with open('data/users.json', 'r') as f:
                users_db = json.load(f)
                print(f"Loaded {len(users_db)} users from file")
        if os.path.exists('data/predictions.json'):
            with open('data/predictions.json', 'r') as f:
                predictions_db = json.load(f)
                print(f"Loaded predictions from file")
    except Exception as e:
        print(f"Error loading data: {e}")
        pass

def save_data():
    try:
        import json
        import os
        os.makedirs('data', exist_ok=True)
        with open('data/users.json', 'w') as f:
            json.dump(users_db, f)
        with open('data/predictions.json', 'w') as f:
            json.dump(predictions_db, f)
    except:
        pass

load_data()

# Load ML model (you'll need to train and save this)
try:
    with open('breast_cancer_model.pkl', 'rb') as f:
        model = pickle.load(f)
except:
    model = None
    print("Warning: Model not loaded. Train the model first.")

# User Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    if not email or not password or not name:
        return jsonify({'error': 'All fields required'}), 400
    
    if email in users_db:
        return jsonify({'error': 'User already exists'}), 400
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    users_db[email] = {
        'name': name,
        'email': email,
        'password': hashed_password,
        'created_at': datetime.now().isoformat()
    }
    save_data()
    
    return jsonify({'message': 'Registration successful'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = users_db.get(email)
    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    session['user_email'] = email
    return jsonify({
        'message': 'Login successful',
        'user': {'name': user['name'], 'email': user['email']}
    }), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_email', None)
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    if 'user_email' in session:
        user = users_db.get(session['user_email'])
        return jsonify({
            'authenticated': True,
            'user': {'name': user['name'], 'email': user['email']}
        }), 200
    return jsonify({'authenticated': False}), 401

# Symptom-Based Prediction
@app.route('/api/predict/symptom-based', methods=['POST'])
def predict_symptom_based():
    # Allow predictions without authentication for easier access
    data = request.json
    
    # Extract symptom-based features
    age = int(data.get('age', 0))
    family_history = 1 if data.get('familyHistory') == 'yes' else 0
    previous_conditions = 1 if data.get('previousConditions') == 'yes' else 0
    lump_present = 1 if data.get('lumpPresent') == 'yes' else 0
    nipple_discharge = 1 if data.get('nippleDischarge') == 'yes' else 0
    skin_changes = 1 if data.get('skinChanges') == 'yes' else 0
    breast_pain = 1 if data.get('breastPain') == 'yes' else 0
    armpit_swelling = 1 if data.get('armpitSwelling') == 'yes' else 0
    asymmetry = 1 if data.get('asymmetry') == 'yes' else 0
    
    # Risk calculation algorithm
    risk_score = 0
    risk_score += age * 0.5 if age > 50 else age * 0.2
    risk_score += family_history * 20
    risk_score += previous_conditions * 15
    risk_score += lump_present * 25
    risk_score += nipple_discharge * 15
    risk_score += skin_changes * 20
    risk_score += breast_pain * 10
    risk_score += armpit_swelling * 22  # High risk indicator
    risk_score += asymmetry * 18  # Significant warning sign
    
    risk_percentage = min(risk_score, 100)
    
    # Generate personalized prevention recommendations
    preventions = []
    
    # Age-based recommendations
    if age > 40:
        preventions.append({
            'category': 'Screening',
            'recommendation': 'Schedule annual mammograms',
            'priority': 'High',
            'details': 'Women over 40 should have yearly mammograms for early detection.'
        })
    
    # Family history recommendations
    if family_history:
        preventions.extend([
            {
                'category': 'Genetic Testing',
                'recommendation': 'Consider BRCA1/BRCA2 genetic testing',
                'priority': 'High',
                'details': 'Family history increases risk. Genetic counseling can help assess inherited risk.'
            },
            {
                'category': 'Screening',
                'recommendation': 'Start screening earlier (age 30-35)',
                'priority': 'High',
                'details': 'With family history, earlier and more frequent screening is recommended.'
            }
        ])
    
    # Symptom-based recommendations
    if lump_present:
        preventions.append({
            'category': 'Immediate Action',
            'recommendation': 'Schedule clinical breast exam immediately',
            'priority': 'Urgent',
            'details': 'Any new lump should be evaluated by a healthcare provider as soon as possible.'
        })
    
    if nipple_discharge:
        preventions.append({
            'category': 'Medical Evaluation',
            'recommendation': 'Consult doctor about nipple discharge',
            'priority': 'High',
            'details': 'Nipple discharge can indicate various conditions and should be evaluated.'
        })
    
    if skin_changes:
        preventions.append({
            'category': 'Medical Evaluation',
            'recommendation': 'Get skin changes examined',
            'priority': 'High',
            'details': 'Skin dimpling, redness, or texture changes should be evaluated promptly.'
        })
    
    if armpit_swelling:
        preventions.append({
            'category': 'Immediate Action',
            'recommendation': 'Evaluate lymph node swelling immediately',
            'priority': 'Urgent',
            'details': 'Swelling in armpit or near collarbone may indicate lymph node involvement and requires urgent medical attention.'
        })
    
    if asymmetry:
        preventions.append({
            'category': 'Medical Evaluation',
            'recommendation': 'Assess sudden breast asymmetry',
            'priority': 'High',
            'details': 'Sudden changes in breast size or shape should be evaluated by a healthcare provider.'
        })
    
    # General prevention recommendations
    preventions.extend([
        {
            'category': 'Lifestyle',
            'recommendation': 'Maintain healthy weight',
            'priority': 'Medium',
            'details': 'Being overweight increases breast cancer risk, especially after menopause.'
        },
        {
            'category': 'Lifestyle',
            'recommendation': 'Exercise regularly (150 min/week)',
            'priority': 'Medium',
            'details': 'Regular physical activity can reduce breast cancer risk by 10-20%.'
        },
        {
            'category': 'Lifestyle',
            'recommendation': 'Limit alcohol consumption',
            'priority': 'Medium',
            'details': 'Even small amounts of alcohol can increase risk. Limit to 1 drink per day or less.'
        },
        {
            'category': 'Diet',
            'recommendation': 'Eat a healthy diet rich in fruits and vegetables',
            'priority': 'Medium',
            'details': 'A diet high in vegetables, fruits, and whole grains may help reduce risk.'
        },
        {
            'category': 'Self-Care',
            'recommendation': 'Perform monthly breast self-exams',
            'priority': 'Medium',
            'details': 'Know what\'s normal for you and report any changes to your doctor.'
        }
    ])
    
    # Risk-specific recommendations
    if risk_percentage > 60:
        preventions.insert(0, {
            'category': 'Urgent',
            'recommendation': 'Schedule comprehensive medical evaluation',
            'priority': 'Urgent',
            'details': 'High risk requires immediate medical attention and comprehensive screening.'
        })
    elif risk_percentage > 30:
        preventions.insert(0, {
            'category': 'Follow-up',
            'recommendation': 'Consult healthcare provider within 2 weeks',
            'priority': 'High',
            'details': 'Moderate risk warrants professional evaluation and personalized screening plan.'
        })
    
    prediction = {
        'type': 'symptom-based',
        'risk_percentage': round(risk_percentage, 2),
        'outcome': 'High Risk' if risk_percentage > 60 else 'Moderate Risk' if risk_percentage > 30 else 'Low Risk',
        'preventions': preventions,
        'timestamp': datetime.now().isoformat(),
        'user_email': session.get('user_email', 'anonymous'),
        'input_data': data
    }
    
    # Save prediction if user is logged in
    if 'user_email' in session:
        if session['user_email'] not in predictions_db:
            predictions_db[session['user_email']] = []
        predictions_db[session['user_email']].append(prediction)
        save_data()
    
    return jsonify(prediction), 200

# Technical/Medical Prediction
@app.route('/api/predict/technical', methods=['POST'])
def predict_technical():
    # Allow predictions without authentication for easier access
    data = request.json
    
    # Extract technical features
    features = [
        float(data.get('radiusMean', 0)),
        float(data.get('textureMean', 0)),
        float(data.get('perimeterMean', 0)),
        float(data.get('areaMean', 0)),
        float(data.get('smoothnessMean', 0)),
        float(data.get('compactnessMean', 0))
    ]
    
    # Use ML model if available
    if model:
        try:
            # Pad features if model expects more
            while len(features) < 30:
                features.append(0)
            
            prediction_result = model.predict([features])[0]
            probability = model.predict_proba([features])[0]
            
            malignant_prob = probability[1] * 100 if len(probability) > 1 else 50
        except Exception as e:
            print(f"Model prediction error: {e}")
            malignant_prob = 50
    else:
        # Fallback calculation
        malignant_prob = min((sum(features) / len(features)) * 5, 100)
    
    # Generate prevention recommendations based on result
    preventions = []
    
    if malignant_prob > 50:
        preventions.extend([
            {
                'category': 'Urgent',
                'recommendation': 'Consult oncologist immediately',
                'priority': 'Urgent',
                'details': 'High malignancy probability requires immediate specialist consultation.'
            },
            {
                'category': 'Diagnostic',
                'recommendation': 'Schedule biopsy and additional imaging',
                'priority': 'Urgent',
                'details': 'Confirmatory tests are essential for accurate diagnosis and treatment planning.'
            },
            {
                'category': 'Support',
                'recommendation': 'Consider genetic counseling',
                'priority': 'High',
                'details': 'Understanding genetic factors can guide treatment and family screening.'
            }
        ])
    else:
        preventions.extend([
            {
                'category': 'Follow-up',
                'recommendation': 'Schedule follow-up in 6 months',
                'priority': 'Medium',
                'details': 'Even benign findings should be monitored regularly.'
            },
            {
                'category': 'Screening',
                'recommendation': 'Continue regular mammograms',
                'priority': 'Medium',
                'details': 'Maintain routine screening schedule as recommended by your doctor.'
            }
        ])
    
    # General prevention recommendations
    preventions.extend([
        {
            'category': 'Lifestyle',
            'recommendation': 'Maintain healthy lifestyle',
            'priority': 'Medium',
            'details': 'Regular exercise, healthy diet, and limited alcohol reduce cancer risk.'
        },
        {
            'category': 'Monitoring',
            'recommendation': 'Track any changes in breast tissue',
            'priority': 'Medium',
            'details': 'Report any new lumps, pain, or changes to your healthcare provider.'
        },
        {
            'category': 'Education',
            'recommendation': 'Learn about breast health',
            'priority': 'Low',
            'details': 'Understanding risk factors and symptoms empowers early detection.'
        }
    ])
    
    prediction = {
        'type': 'technical',
        'malignant_probability': round(malignant_prob, 2),
        'benign_probability': round(100 - malignant_prob, 2),
        'outcome': 'Malignant' if malignant_prob > 50 else 'Benign',
        'preventions': preventions,
        'timestamp': datetime.now().isoformat(),
        'user_email': session.get('user_email', 'anonymous'),
        'input_data': data
    }
    
    # Save prediction if user is logged in
    if 'user_email' in session:
        if session['user_email'] not in predictions_db:
            predictions_db[session['user_email']] = []
        predictions_db[session['user_email']].append(prediction)
        save_data()
    
    return jsonify(prediction), 200

# Prediction History
@app.route('/api/prediction-history', methods=['GET'])
def get_prediction_history():
    if 'user_email' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    history = predictions_db.get(session['user_email'], [])
    return jsonify(history), 200

# AI Assistance
@app.route('/api/ai-assistance', methods=['POST'])
def ai_assistance():
    if 'user_email' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    question = data.get('question', '')
    
    # Simple keyword-based responses (replace with actual AI)
    responses = {
        'symptoms': 'Common breast cancer symptoms include lumps, nipple discharge, skin changes, and breast pain. Consult a doctor if you notice any changes.',
        'prevention': 'Prevention includes regular screenings, healthy lifestyle, limiting alcohol, maintaining healthy weight, and being physically active.',
        'screening': 'Mammograms are recommended annually for women over 40. Self-exams and clinical exams are also important.',
        'treatment': 'Treatment options include surgery, radiation, chemotherapy, hormone therapy, and targeted therapy. Treatment depends on cancer stage and type.',
        'risk': 'Risk factors include age, family history, genetic mutations (BRCA1/BRCA2), previous breast conditions, and lifestyle factors.'
    }
    
    response = 'I can help with questions about breast cancer symptoms, prevention, screening, treatment, and risk factors. Please ask a specific question.'
    
    for key, value in responses.items():
        if key in question.lower():
            response = value
            break
    
    return jsonify({'response': response}), 200

# Educational Resources
@app.route('/api/educational-resources', methods=['GET'])
def get_educational_resources():
    resources = [
        {
            'id': 1,
            'title': 'Understanding Breast Cancer',
            'description': 'Learn about breast cancer types, stages, and how it develops.',
            'category': 'basics',
            'url': '#'
        },
        {
            'id': 2,
            'title': 'Early Detection and Screening',
            'description': 'Importance of mammograms, self-exams, and clinical examinations.',
            'category': 'screening',
            'url': '#'
        },
        {
            'id': 3,
            'title': 'Risk Factors and Prevention',
            'description': 'Understand risk factors and steps to reduce your risk.',
            'category': 'prevention',
            'url': '#'
        },
        {
            'id': 4,
            'title': 'Treatment Options',
            'description': 'Overview of surgery, chemotherapy, radiation, and other treatments.',
            'category': 'treatment',
            'url': '#'
        },
        {
            'id': 5,
            'title': 'Living with Breast Cancer',
            'description': 'Support resources, lifestyle tips, and coping strategies.',
            'category': 'support',
            'url': '#'
        }
    ]
    
    return jsonify(resources), 200

# Serve frontend
@app.route('/')
def serve_frontend():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    return app.send_static_file(path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
