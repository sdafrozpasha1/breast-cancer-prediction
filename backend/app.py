from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import os
from datetime import datetime
import secrets

app = Flask(__name__)

# Simple CORS - allow all
CORS(app, origins=['*'])

# Simple in-memory storage
users_db = {}
sessions_db = {}
predictions_db = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    return secrets.token_hex(32)

@app.route('/')
def home():
    return jsonify({'message': 'Breast Cancer Prediction API', 'status': 'running'})

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
        
        users_db[email] = {
            'name': name,
            'email': email,
            'password': hash_password(password),
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
        if not user or user['password'] != hash_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        token = generate_token()
        sessions_db[token] = email
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {'name': user['name'], 'email': user['email']}
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def verify_token(token):
    return sessions_db.get(token)

@app.route('/api/predict/symptom-based', methods=['POST', 'OPTIONS'])
def predict_symptom_based():
    if request.method == 'OPTIONS':
        return '', 204
    
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_email = verify_token(token)
    
    if not user_email:
        return jsonify({'error': 'Unauthorized'}), 401
    
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
                'details': 'Women over 40 should have yearly mammograms.'
            })
        
        if family_history:
            preventions.extend([
                {
                    'category': 'Genetic Testing',
                    'recommendation': 'Consider BRCA1/BRCA2 genetic testing',
                    'priority': 'High',
                    'details': 'Family history increases risk.'
                },
                {
                    'category': 'Screening',
                    'recommendation': 'Start screening earlier',
                    'priority': 'High',
                    'details': 'Earlier screening recommended.'
                }
            ])
        
        if lump_present:
            preventions.append({
                'category': 'Immediate Action',
                'recommendation': 'Schedule clinical breast exam immediately',
                'priority': 'Urgent',
                'details': 'Any new lump should be evaluated.'
            })
        
        if nipple_discharge:
            preventions.append({
                'category': 'Medical Evaluation',
                'recommendation': 'Consult doctor about nipple discharge',
                'priority': 'High',
                'details': 'Should be evaluated.'
            })
        
        if skin_changes:
            preventions.append({
                'category': 'Medical Evaluation',
                'recommendation': 'Get skin changes examined',
                'priority': 'High',
                'details': 'Should be evaluated promptly.'
            })
        
        if armpit_swelling:
            preventions.append({
                'category': 'Immediate Action',
                'recommendation': 'Evaluate lymph node swelling',
                'priority': 'Urgent',
                'details': 'May indicate lymph node involvement.'
            })
        
        if asymmetry:
            preventions.append({
                'category': 'Medical Evaluation',
                'recommendation': 'Assess sudden breast asymmetry',
                'priority': 'High',
                'details': 'Sudden changes should be evaluated.'
            })
        
        preventions.extend([
            {
                'category': 'Lifestyle',
                'recommendation': 'Maintain healthy weight',
                'priority': 'Medium',
                'details': 'Reduces breast cancer risk.'
            },
            {
                'category': 'Lifestyle',
                'recommendation': 'Exercise regularly',
                'priority': 'Medium',
                'details': 'Can reduce risk by 10-20%.'
            },
            {
                'category': 'Lifestyle',
                'recommendation': 'Limit alcohol',
                'priority': 'Medium',
                'details': 'Alcohol increases risk.'
            }
        ])
        
        if risk_percentage > 60:
            preventions.insert(0, {
                'category': 'Urgent',
                'recommendation': 'Schedule comprehensive medical evaluation',
                'priority': 'Urgent',
                'details': 'High risk requires immediate attention.'
            })
        elif risk_percentage > 30:
            preventions.insert(0, {
                'category': 'Follow-up',
                'recommendation': 'Consult healthcare provider',
                'priority': 'High',
                'details': 'Moderate risk warrants evaluation.'
            })
        
        prediction = {
            'type': 'symptom-based',
            'risk_percentage': round(risk_percentage, 2),
            'outcome': 'High Risk' if risk_percentage > 60 else 'Moderate Risk' if risk_percentage > 30 else 'Low Risk',
            'preventions': preventions,
            'timestamp': datetime.now().isoformat()
        }
        
        if user_email not in predictions_db:
            predictions_db[user_email] = []
        predictions_db[user_email].append(prediction)
        
        return jsonify(prediction)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/technical', methods=['POST', 'OPTIONS'])
def predict_technical():
    if request.method == 'OPTIONS':
        return '', 204
    
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_email = verify_token(token)
    
    if not user_email:
        return jsonify({'error': 'Unauthorized'}), 401
    
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
        
        malignant_prob = min((sum(features) / len(features)) * 5, 100)
        
        preventions = []
        
        if malignant_prob > 50:
            preventions.extend([
                {
                    'category': 'Urgent',
                    'recommendation': 'Consult oncologist immediately',
                    'priority': 'Urgent',
                    'details': 'High malignancy probability.'
                },
                {
                    'category': 'Diagnostic',
                    'recommendation': 'Schedule biopsy',
                    'priority': 'Urgent',
                    'details': 'Confirmatory tests essential.'
                }
            ])
        else:
            preventions.append({
                'category': 'Follow-up',
                'recommendation': 'Schedule follow-up',
                'priority': 'Medium',
                'details': 'Regular monitoring important.'
            })
        
        prediction = {
            'type': 'technical',
            'malignant_probability': round(malignant_prob, 2),
            'benign_probability': round(100 - malignant_prob, 2),
            'outcome': 'Malignant' if malignant_prob > 50 else 'Benign',
            'preventions': preventions,
            'timestamp': datetime.now().isoformat()
        }
        
        if user_email not in predictions_db:
            predictions_db[user_email] = []
        predictions_db[user_email].append(prediction)
        
        return jsonify(prediction)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prediction-history', methods=['GET', 'OPTIONS'])
def get_prediction_history():
    if request.method == 'OPTIONS':
        return '', 204
    
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_email = verify_token(token)
    
    if not user_email:
        return jsonify({'error': 'Unauthorized'}), 401
    
    history = predictions_db.get(user_email, [])
    return jsonify(history)

@app.route('/api/ai-assistance', methods=['POST', 'OPTIONS'])
def ai_assistance():
    if request.method == 'OPTIONS':
        return '', 204
    
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_email = verify_token(token)
    
    if not user_email:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        question = data.get('question', '').lower()
        
        responses = {
            'symptom': 'Common symptoms include lumps, nipple discharge, skin changes, and breast pain.',
            'prevention': 'Prevention includes regular screenings, healthy lifestyle, and limiting alcohol.',
            'screening': 'Mammograms recommended annually for women over 40.',
            'treatment': 'Treatment options include surgery, radiation, chemotherapy, and hormone therapy.',
            'risk': 'Risk factors include age, family history, and genetic mutations.'
        }
        
        response = 'I can help with questions about symptoms, prevention, screening, treatment, and risk factors.'
        
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
            'description': 'Learn about breast cancer types and stages.',
            'category': 'basics'
        },
        {
            'id': 2,
            'title': 'Early Detection and Screening',
            'description': 'Importance of mammograms and self-exams.',
            'category': 'screening'
        },
        {
            'id': 3,
            'title': 'Risk Factors and Prevention',
            'description': 'Understand risk factors and prevention steps.',
            'category': 'prevention'
        },
        {
            'id': 4,
            'title': 'Treatment Options',
            'description': 'Overview of treatment options.',
            'category': 'treatment'
        },
        {
            'id': 5,
            'title': 'Living with Breast Cancer',
            'description': 'Support resources and coping strategies.',
            'category': 'support'
        }
    ]
    
    return jsonify(resources)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
