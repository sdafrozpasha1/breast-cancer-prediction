from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
from datetime import datetime
import os

app = Flask(__name__)

# Simple CORS - allow all origins
CORS(app, origins=['*'])

# Load ML model
try:
    with open('breast_cancer_model.pkl', 'rb') as f:
        model = pickle.load(f)
except:
    model = None
    print("Warning: Model not loaded")

@app.route('/')
def home():
    return jsonify({'message': 'Breast Cancer Prediction API', 'status': 'running'})

@app.route('/api/predict/symptom-based', methods=['POST'])
def predict_symptom_based():
    try:
        data = request.json
        
        # Extract features
        age = int(data.get('age', 0))
        family_history = 1 if data.get('familyHistory') == 'yes' else 0
        previous_conditions = 1 if data.get('previousConditions') == 'yes' else 0
        lump_present = 1 if data.get('lumpPresent') == 'yes' else 0
        nipple_discharge = 1 if data.get('nippleDischarge') == 'yes' else 0
        skin_changes = 1 if data.get('skinChanges') == 'yes' else 0
        breast_pain = 1 if data.get('breastPain') == 'yes' else 0
        armpit_swelling = 1 if data.get('armpitSwelling') == 'yes' else 0
        asymmetry = 1 if data.get('asymmetry') == 'yes' else 0
        
        # Risk calculation
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
        
        # Generate preventions
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
        
        # General preventions
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
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(prediction)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict/technical', methods=['POST'])
def predict_technical():
    try:
        data = request.json
        
        # Extract features
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
                # Pad features to match model input
                while len(features) < 30:
                    features.append(0)
                
                prediction_result = model.predict([features])[0]
                probability = model.predict_proba([features])[0]
                
                malignant_prob = probability[1] * 100 if len(probability) > 1 else 50
            except:
                malignant_prob = 50
        else:
            # Fallback calculation
            malignant_prob = min((sum(features) / len(features)) * 5, 100)
        
        # Generate preventions
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
        
        # General preventions
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
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(prediction)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-assistance', methods=['POST'])
def ai_assistance():
    try:
        data = request.json
        question = data.get('question', '').lower()
        
        responses = {
            'symptom': 'Common breast cancer symptoms include lumps, nipple discharge, skin changes, and breast pain. Consult a doctor if you notice any changes.',
            'prevention': 'Prevention includes regular screenings, healthy lifestyle, limiting alcohol, maintaining healthy weight, and being physically active.',
            'screening': 'Mammograms are recommended annually for women over 40. Self-exams and clinical exams are also important.',
            'treatment': 'Treatment options include surgery, radiation, chemotherapy, hormone therapy, and targeted therapy. Treatment depends on cancer stage and type.',
            'risk': 'Risk factors include age, family history, genetic mutations (BRCA1/BRCA2), previous breast conditions, and lifestyle factors.'
        }
        
        response = 'I can help with questions about breast cancer symptoms, prevention, screening, treatment, and risk factors. Please ask a specific question.'
        
        for key, value in responses.items():
            if key in question:
                response = value
                break
        
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/educational-resources', methods=['GET'])
def get_educational_resources():
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
