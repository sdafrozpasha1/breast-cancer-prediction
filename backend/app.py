from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import jwt
import pickle
import numpy as np
from datetime import datetime, timedelta
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'breast-cancer-jwt-secret-2024')

# CORS configuration
CORS(app, 
     origins=['https://spiffy-malabi-3967dc.netlify.app', 'http://localhost:8000'],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'OPTIONS'])

bcrypt = Bcrypt(app)

# In-memory storage (use database in production)
users_db = {}
predictions_db = {}

# Load ML model
try:
    with open('breast_cancer_model.pkl', 'rb') as f:
        model = pickle.load(f)
except:
    model = None
    print("Warning: Model not loaded")

# JWT token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_email = data['email']
            
            if current_user_email not in users_db:
                return jsonify({'error': 'User not found'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user_email, *args, **kwargs)
    
    return decorated

@app.route('/')
def home():
    return jsonify({'message': 'Breast Cancer Prediction API', 'status': 'running'})

# Authentication Routes
@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
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
        
        return jsonify({'message': 'Registration successful'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = users_db.get(email)
        if not user or not bcrypt.check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {'name': user['name'], 'email': user['email']}
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-auth', methods=['GET', 'OPTIONS'])
@token_required
def check_auth(current_user_email):
    if request.method == 'OPTIONS':
        return '', 204
    
    user = users_db.get(current_user_email)
    return jsonify({
        'authenticated': True,
        'user': {'name': user['name'], 'email': user['email']}
    }), 200

# Prediction Routes
@app.route('/api/predict/symptom-based', methods=['POST', 'OPTIONS'])
@token_required
def predict_symptom_based(current_user_email):
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json
        
        age = int(data.get('age', 0))
        family_history = 1 if data.get('familyHistory') == 'yes' else 0
        previous_conditions = 1 if data.get('previousConditions') == 'yes' else 0
        lump_present = 1 if data.get('lumpPresent') == 'yes' else 0
        nipple_discharge = 1 if data.get('nippleDischarge') == 'yes' else 0
        skin_changes = 1 if data.get('skinChanges') == 'yes' else 0
        breast_pain = 1 if data.get('breastPain') == 'yes' else 0
        armpit_swelling = 1 if data.get('armpitSwelling') == 'yes' else 0
        asymmetry = 1 if data.get('asymmetry') == 'yes' else 0
        
        risk_score = 0
        risk_score += age * 0.5 if age > 50 else age * 0.2
        risk_score += family_history * 20
        risk_score += previous_conditions * 15
        risk_score += lump_present * 25
        risk_score += nipple_discharge * 15
        risk_score += skin_changes * 20
        risk_score += breast_pain * 10
        risk_score += armpit_swelling * 22
        risk_score += asymmetry * 18
        
        risk_percentage = min(risk_score, 100)
        
        preventions = []
        
        if age > 40:
            preventions.append({
                'category': 'Screening',
                'recommendation': 'Schedule annual mammograms',
                'priority': 'High',
                'details': 'Women over 40 should have yearly mammograms for early detection.'
            })
        
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
        
        if lump_present:
            preventions.append({
                'category': 'Immediate Action',
                'recommendation': 'Schedule clinical breast exam immediately',
                'priority': 'Urgent',
                'details': 'Any new lump should be evaluated by a healthcare provider.'
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
                'details': 'Swelling in armpit or near collarbone may indicate lymph node involvement.'
            })
        
        if asymmetry:
            preventions.append({
                'category': 'Medical Evaluation',
                'recommendation': 'Assess sudden breast asymmetry',
                'priority': 'High',
                'details': 'Sudden changes in breast size or shape should be evaluated.'
            })
        
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
                'details': 'Even small amounts of alcohol can increase risk.'
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
        
        if risk_percentage > 60:
            preventions.insert(0, {
                'category': 'Urgent',
                'recommendation': 'Schedule comprehensive medical evaluation',
                'priority': 'Urgent',
                'details': 'High risk requires immediate medical attention.'
            })
        elif risk_percentage > 30:
            preventions.insert(0, {
                'category': 'Follow-up',
                'recommendation': 'Consult healthcare provider within 2 weeks',
                'priority': 'High',
                'details': 'Moderate risk warrants professional evaluation.'
            })
        
        prediction = {
            'type': 'symptom-based',
            'risk_percentage': round(risk_percentage, 2),
            'outcome': 'High Risk' if risk_percentage > 60 else 'Moderate Risk' if risk_percentage > 30 else 'Low Risk',
            'preventions': preventions,
            'timestamp': datetime.now().isoformat()
        }
        
        if current_user_email not in predictions_db:
            predictions_db[current_user_email] = []
        predictions_db[current_user_email].append(prediction)
        
        return jsonify(prediction)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/technical', methods=['POST', 'OPTIONS'])
@token_required
def predict_technical(current_user_email):
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json
        
        features = [
            float(data.get('radiusMean', 0)),
            float(data.get('textureMean', 0)),
            float(data.get('perimeterMean', 0)),
            float(data.get('areaMean', 0)),
            float(data.get('smoothnessMean', 0)),
            float(data.get('compactnessMean', 0))
        ]
        
        if model:
            try:
                while len(features) < 30:
                    features.append(0)
                
                prediction_result = model.predict([features])[0]
                probability = model.predict_proba([features])[0]
                malignant_prob = probability[1] * 100 if len(probability) > 1 else 50
            except:
                malignant_prob = 50
        else:
            malignant_prob = min((sum(features) / len(features)) * 5, 100)
        
        preventions = []
        
        if malignant_prob > 50:
            preventions.extend([
                {
                    'category': 'Urgent',
                    'recommendation': 'Consult oncologist immediately',
                    'priority': 'Urgent',
                    'details': 'High malignancy probability requires specialist consultation.'
                },
                {
                    'category': 'Diagnostic',
                    'recommendation': 'Schedule biopsy and additional imaging',
                    'priority': 'Urgent',
                    'details': 'Confirmatory tests are essential for accurate diagnosis.'
                }
            ])
        else:
            preventions.append({
                'category': 'Follow-up',
                'recommendation': 'Schedule follow-up in 6 months',
                'priority': 'Medium',
                'details': 'Regular monitoring is important even for benign findings.'
            })
        
        prediction = {
            'type': 'technical',
            'malignant_probability': round(malignant_prob, 2),
            'benign_probability': round(100 - malignant_prob, 2),
            'outcome': 'Malignant' if malignant_prob > 50 else 'Benign',
            'preventions': preventions,
            'timestamp': datetime.now().isoformat()
        }
        
        if current_user_email not in predictions_db:
            predictions_db[current_user_email] = []
        predictions_db[current_user_email].append(prediction)
        
        return jsonify(prediction)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prediction-history', methods=['GET', 'OPTIONS'])
@token_required
def get_prediction_history(current_user_email):
    if request.method == 'OPTIONS':
        return '', 204
    
    history = predictions_db.get(current_user_email, [])
    return jsonify(history)

@app.route('/api/ai-assistance', methods=['POST', 'OPTIONS'])
@token_required
def ai_assistance(current_user_email):
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json
        question = data.get('question', '').lower()
        
        responses = {
            'symptom': 'Common breast cancer symptoms include lumps, nipple discharge, skin changes, and breast pain.',
            'prevention': 'Prevention includes regular screenings, healthy lifestyle, limiting alcohol, and maintaining healthy weight.',
            'screening': 'Mammograms are recommended annually for women over 40.',
            'treatment': 'Treatment options include surgery, radiation, chemotherapy, hormone therapy, and targeted therapy.',
            'risk': 'Risk factors include age, family history, genetic mutations, and lifestyle factors.'
        }
        
        response = 'I can help with questions about breast cancer symptoms, prevention, screening, treatment, and risk factors.'
        
        for key, value in responses.items():
            if key in question:
                response = value
                break
        
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/educational-resources', methods=['GET', 'OPTIONS'])
def get_educational_resources():
    if request.method == 'OPTIONS':
        return '', 204
    
    resources = [
        {
            'id': 1,
            'title': 'Understanding Breast Cancer',
            'description': 'Learn about breast cancer types, stages, and how it develops.',
            'category': 'basics'
        },
        {
            'id': 2,
            'title': 'Early Detection and Screening',
            'description': 'Importance of mammograms, self-exams, and clinical examinations.',
            'category': 'screening'
        },
        {
            'id': 3,
            'title': 'Risk Factors and Prevention',
            'description': 'Understand risk factors and steps to reduce your risk.',
            'category': 'prevention'
        },
        {
            'id': 4,
            'title': 'Treatment Options',
            'description': 'Overview of surgery, chemotherapy, radiation, and other treatments.',
            'category': 'treatment'
        },
        {
            'id': 5,
            'title': 'Living with Breast Cancer',
            'description': 'Support resources, lifestyle tips, and coping strategies.',
            'category': 'support'
        }
    ]
    
    return jsonify(resources)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
