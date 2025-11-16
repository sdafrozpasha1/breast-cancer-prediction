"""
Utility functions for the breast cancer prediction system
"""

import numpy as np
from datetime import datetime
import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    Validate password strength
    Requirements: At least 8 characters
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    return True, "Password is valid"

def calculate_symptom_risk(data):
    """
    Calculate risk score based on symptoms
    Returns risk percentage (0-100)
    """
    age = int(data.get('age', 0))
    family_history = 1 if data.get('familyHistory') == 'yes' else 0
    previous_conditions = 1 if data.get('previousConditions') == 'yes' else 0
    lump_present = 1 if data.get('lumpPresent') == 'yes' else 0
    nipple_discharge = 1 if data.get('nippleDischarge') == 'yes' else 0
    skin_changes = 1 if data.get('skinChanges') == 'yes' else 0
    breast_pain = 1 if data.get('breastPain') == 'yes' else 0
    
    # Risk calculation algorithm
    risk_score = 0
    
    # Age factor (increases with age, especially after 50)
    if age < 30:
        risk_score += 5
    elif age < 40:
        risk_score += 10
    elif age < 50:
        risk_score += 15
    elif age < 60:
        risk_score += 20
    else:
        risk_score += 25
    
    # Family history is a strong indicator
    risk_score += family_history * 20
    
    # Previous conditions
    risk_score += previous_conditions * 15
    
    # Physical symptoms
    risk_score += lump_present * 25
    risk_score += nipple_discharge * 15
    risk_score += skin_changes * 20
    risk_score += breast_pain * 10
    
    # Cap at 100
    risk_percentage = min(risk_score, 100)
    
    return risk_percentage

def get_risk_category(risk_percentage):
    """Categorize risk level"""
    if risk_percentage < 30:
        return "Low Risk"
    elif risk_percentage < 60:
        return "Moderate Risk"
    else:
        return "High Risk"

def get_risk_recommendations(risk_percentage):
    """Get recommendations based on risk level"""
    if risk_percentage < 30:
        return [
            "Continue regular self-examinations",
            "Maintain a healthy lifestyle",
            "Schedule routine check-ups as recommended by your doctor"
        ]
    elif risk_percentage < 60:
        return [
            "Consult with your healthcare provider soon",
            "Consider more frequent screenings",
            "Discuss family history with your doctor",
            "Maintain awareness of any changes"
        ]
    else:
        return [
            "Seek immediate medical consultation",
            "Schedule a comprehensive examination",
            "Discuss diagnostic imaging options",
            "Consider genetic counseling if family history is present"
        ]

def format_prediction_result(prediction_type, data, result):
    """Format prediction result for display"""
    formatted = {
        'type': prediction_type,
        'timestamp': datetime.now().isoformat(),
        'result': result
    }
    
    if prediction_type == 'symptom-based':
        formatted['risk_percentage'] = result.get('risk_percentage')
        formatted['category'] = get_risk_category(result.get('risk_percentage'))
        formatted['recommendations'] = get_risk_recommendations(result.get('risk_percentage'))
    else:
        formatted['malignant_probability'] = result.get('malignant_probability')
        formatted['benign_probability'] = result.get('benign_probability')
        formatted['outcome'] = result.get('outcome')
    
    return formatted

def sanitize_input(data):
    """Sanitize user input data"""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Remove potentially harmful characters
            sanitized[key] = value.strip()
        else:
            sanitized[key] = value
    return sanitized

def validate_technical_input(data):
    """Validate technical medical input"""
    required_fields = [
        'radiusMean', 'textureMean', 'perimeterMean',
        'areaMean', 'smoothnessMean', 'compactnessMean'
    ]
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
        
        try:
            value = float(data[field])
            if value < 0:
                return False, f"{field} must be positive"
        except ValueError:
            return False, f"{field} must be a number"
    
    return True, "Valid input"

def get_ai_response(question):
    """
    Generate AI response based on question
    This is a simple keyword-based system
    In production, integrate with actual AI/NLP service
    """
    question_lower = question.lower()
    
    responses = {
        'symptom': {
            'keywords': ['symptom', 'sign', 'lump', 'pain', 'discharge', 'change'],
            'response': 'Common breast cancer symptoms include: a lump in the breast or underarm, changes in breast size or shape, nipple discharge (especially bloody), skin changes (dimpling, redness), and persistent breast pain. However, many breast cancers have no symptoms in early stages, which is why regular screening is important.'
        },
        'prevention': {
            'keywords': ['prevent', 'avoid', 'reduce risk', 'lifestyle'],
            'response': 'While not all breast cancers can be prevented, you can reduce your risk by: maintaining a healthy weight, exercising regularly (at least 150 minutes per week), limiting alcohol consumption, avoiding smoking, breastfeeding if possible, and limiting hormone therapy. Regular screening is also crucial for early detection.'
        },
        'screening': {
            'keywords': ['screening', 'mammogram', 'test', 'check', 'exam'],
            'response': 'Screening recommendations: Women 40-44 can start annual mammograms, women 45-54 should get annual mammograms, women 55+ can switch to every 2 years or continue yearly. Monthly self-exams and clinical breast exams are also important. Talk to your doctor about your personal screening schedule based on your risk factors.'
        },
        'treatment': {
            'keywords': ['treatment', 'therapy', 'cure', 'surgery', 'chemotherapy', 'radiation'],
            'response': 'Breast cancer treatment depends on the type, stage, and individual factors. Options include: surgery (lumpectomy or mastectomy), radiation therapy, chemotherapy, hormone therapy, targeted therapy, and immunotherapy. Most patients receive a combination of treatments. Your oncologist will create a personalized treatment plan.'
        },
        'risk': {
            'keywords': ['risk', 'chance', 'likely', 'factor', 'cause'],
            'response': 'Risk factors include: age (risk increases with age), family history, genetic mutations (BRCA1/BRCA2), personal history of breast cancer, dense breast tissue, early menstruation or late menopause, never having children or having first child after 30, obesity, and alcohol consumption. Having risk factors doesn\'t mean you\'ll get cancer, and many people with cancer have no known risk factors.'
        },
        'diagnosis': {
            'keywords': ['diagnose', 'detect', 'find', 'biopsy'],
            'response': 'Breast cancer is diagnosed through: mammography, ultrasound, MRI, and biopsy (the definitive test). If an abnormality is found, a biopsy will be performed to examine tissue under a microscope. Additional tests may include blood tests and imaging to determine if cancer has spread.'
        }
    }
    
    # Find matching response
    for category, info in responses.items():
        for keyword in info['keywords']:
            if keyword in question_lower:
                return info['response']
    
    # Default response
    return "I can help answer questions about breast cancer symptoms, prevention, screening, treatment, risk factors, and diagnosis. Please ask a specific question about any of these topics, and I'll provide detailed information. Remember, for personalized medical advice, always consult with a healthcare professional."

def log_prediction(user_email, prediction_data):
    """Log prediction for analytics"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'user': user_email,
        'type': prediction_data.get('type'),
        'result': prediction_data.get('outcome')
    }
    # In production, save to database or logging service
    print(f"Prediction logged: {log_entry}")
