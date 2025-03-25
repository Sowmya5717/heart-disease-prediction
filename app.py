#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 15 14:29:54 2025

@author: rgukt
"""

import numpy as np
import pickle
import streamlit as st
from gtts import gTTS
from reportlab.pdfgen import canvas
from datetime import datetime
import os
import base64

st.set_page_config(page_title="Heart Disease Prediction App", layout="centered")



# Load and encode your background image
with open("/home/rgukt/Downloads/Heart-Disease-Prediction/heart.jpeg", "rb") as img_file:
    encoded_img = base64.b64encode(img_file.read()).decode()

# Streamlit CSS - Balanced background and visible text
st.markdown(f"""
    <style>
    html, body, .stApp {{
        height: 100%;
        margin: 0;
        padding: 0;
        background: none;
        color: #ffffff;
    }}

    /* Blurred background */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: url("data:image/jpeg;base64,{encoded_img}") no-repeat center center fixed;
        background-size: cover;
        filter: blur(5px) brightness(0.6);  /* Slight blur + better brightness */
        z-index: -2;
    }}

    /* Slightly lighter overlay for better background visibility */
    .stApp::after {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.3);  /* 30% black overlay */
        z-index: -1;
    }}

    .main, .block-container {{
        background-color: transparent !important;
    }}

    h1, h2, h3, h4, h5, h6, p, label {{
        color: #ffffff !important;
        text-shadow: 2px 2px 4px #000000;  /* Makes text pop */
        font-weight: 700;
    }}

    /* Input box style */
    input[type="text"], input[type="number"], textarea {{
        background-color: rgba(255, 255, 255, 0.85) !important;
        color: #000000 !important;
        border-radius: 8px !important;
        padding: 12px;
        border: none;
    }}

    /* Netflix-style Button */
    .stButton button {{
        background-color: #e50914 !important;
        color: #ffffff !important;
        padding: 14px 28px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
    }}

    .stButton button:hover {{
        background-color: #f6121d !important;
    }}

    header, footer, .css-18ni7ap.e8zbici2 {{
        background-color: transparent !important;
    }}
    </style>
""", unsafe_allow_html=True)



loaded_file=pickle.load(open('/home/rgukt/Downloads/Heart-Disease-Prediction/heart_disease_model.sav','rb'))



st.title("    Heart Disease Prediction App    ")

# Inputs
name=st.text_input("Enter your name:",key="name")
age = st.text_input("Age (1-100)", help="Normal: 20-50 | Low Risk: 51-60 | High Risk: >60 /n/n Risk of heart disease increases with age, especially after 50.",key="age")
sex = st.selectbox("Sex (0 = Female, 1 = Male)", ["Select", 0, 1],help="Males are generally at higher risk for heart disease at a younger age.", key="sex")
cp = st.selectbox("Chest Pain Type (0-3)", ["Select", 0, 1, 2, 3],help=(
        "Possible Values:\n"
        "0 → Typical Angina (chest pain from reduced blood flow to the heart)\n"
        "1 → Atypical Angina (unusual chest pain not related to exertion)\n"
        "2 → Non-Anginal Pain (pain not related to heart)\n"
        "3 → Asymptomatic (no chest pain but possible heart issue)\n\n"
        "Helps the model understand the severity and type of chest pain, which strongly signals heart disease."
    ), key="cp")
trestbps = st.text_input("Resting Blood Pressure (50-200 mmHg)",help="Normal Range: 90-120 mm Hg.\n\n High BP puts extra strain on the heart and arteries, increasing heart disease risk.", key="trestbps")
chol = st.text_input("Cholesterol Level (100-600 mg/dL)",help="Normal: 125-200 mg/dl.\n\n High cholesterol can cause artery blockages, increasing heart disease risk." ,key="chol")
fbs = st.selectbox("Fasting Blood Sugar > 120 mg/dL", ["Select", 0, 1],help="0 → False\n1 → True\n\nWhy: High fasting blood sugar indicates diabetes risk, a major heart disease factor.", key="fbs")
restecg = st.selectbox("Resting ECG (0-2)", ["Select", 0, 1, 2],help=(
        "0 → Normal\n"
        "1 → ST-T wave abnormality (possible ischemia)\n"
        "2 → Left Ventricular Hypertrophy (heart enlargement)\n\n"
        "Why: Helps detect heart muscle strain or damage."
    ), key="restecg")
thalach = st.text_input("Max Heart Rate Achieved (60-250)",help=" Low max heart rate may signal poor heart function or blockages." ,key="thalach")
exang = st.selectbox("Exercise-Induced Angina", ["Select", 0, 1],help="0 → No\n1 → Yes\n\n Angina triggered by exercise signals reduced blood flow to the heart.", key="exang")
oldpeak = st.text_input("ST Depression (0.0 - 6.0)",help="ST depression induced by exercise relative to rest.\n\n Higher values indicate reduced blood flow (ischemia)." ,key="oldpeak")
slope = st.selectbox("Slope of ST Segment (0-2)", ["Select", 0, 1, 2],help=(
        "0 → Upsloping (normal)\n"
        "1 → Flat (may indicate heart problems)\n"
        "2 → Downsloping (high chance of heart disease)\n\n"
        "Why: Represents changes in the heart's electrical pattern during exercise."
    ), key="slope")
ca = st.selectbox("Number of Major Vessels (0-4)", ["Select", 0, 1, 2, 3, 4],help="Number of major blood vessels (0-3) showing blockages.\n\n Higher count of blocked vessels increases heart disease risk." ,key="ca")
thal = st.selectbox("Thalassemia (0-3)", ["Select", 0, 1, 2, 3], help=(
        "0 → Normal\n"
        "1 → Fixed Defect (permanent damage to heart muscle)\n"
        "2 → Reversible Defect (temporary blood flow issue)\n\n"
        "Why: Indicates how well the heart is supplied with blood and oxygen."
    ),key="thal")
lang = st.selectbox("Select Language for Audio", ["English", "Hindi", "Telugu"])   


if st.button("Predict"):
    errors = []

    # Validation for numeric inputs
    if name.strip() == "":
        errors.append("Please enter the patient's name.")
    if not age.strip():
        errors.append(" Age is required.")
    elif not age.isdigit() or int(age) <= 0 or int(age) > 100:
        errors.append(" Age must be a number between 1 and 100.")

    if not trestbps.strip():
        errors.append(" Resting Blood Pressure is required.")
    elif not trestbps.isdigit() or int(trestbps) <= 0:
        errors.append(" Resting Blood Pressure must be positive.")

    if not chol.strip():
        errors.append(" Cholesterol is required.")
    elif not chol.isdigit() or int(chol) <= 0:
        errors.append(" Cholesterol must be positive.")

    if not thalach.strip():
        errors.append(" Max Heart Rate is required.")
    elif not thalach.isdigit() or int(thalach) < 60 or int(thalach) > 250:
        errors.append(" Max Heart Rate must be between 60 and 250.")

    if not oldpeak.strip():
        errors.append(" ST Depression (Oldpeak) is required.")
    elif not oldpeak.replace('.', '', 1).isdigit() or float(oldpeak) < 0 or float(oldpeak) > 6:
        errors.append(" ST Depression must be a number between 0.0 and 6.0.")

    # Select box validations
    if sex == "Select":
        errors.append(" Please select Sex.")
    if cp == "Select":
        errors.append(" Please select Chest Pain Type.")
    if fbs == "Select":
        errors.append(" Please select Fasting Blood Sugar status.")
    if restecg == "Select":
        errors.append(" Please select Resting ECG result.")
    if exang == "Select":
        errors.append(" Please select Exercise-Induced Angina.")
    if slope == "Select":
        errors.append(" Please select Slope of ST Segment.")
    if ca == "Select":
        errors.append(" Please select Number of Major Vessels.")
    if thal == "Select":
        errors.append(" Please select Thalassemia value.")

    # Show all errors at once and STOP prediction if errors exist
    if errors:
        for err in errors:
            st.toast(err, icon="⚠️")
        st.stop()
    else:
        # Proceed to prediction ONLY IF no errors
        input_data = [
            int(age), int(sex), int(cp), int(trestbps), int(chol),
            int(fbs), int(restecg), int(thalach), int(exang),
            float(oldpeak), int(slope), int(ca), int(thal)
        ]
        lang_code = {'English': 'en', 'Hindi': 'hi', 'Telugu': 'te'}
        prediction = loaded_file.predict(np.array(input_data).reshape(1, -1))[0]
        if prediction ==1 :
            result = "Heart Disease Detected " 
            if lang == "Hindi":
                message = f"प्रिय {name}, आपके परिणाम के अनुसार, हृदय रोग का खतरा है। कृपया तुरंत डॉक्टर से सलाह लें।"
            elif lang == "Telugu":
                message = f"ప్రియమైన {name}, మీ ఫలితాల ప్రకారం హృదయ వ్యాధి ప్రమాదం ఉంది. దయచేసి వెంటనే డాక్టర్‌ని సంప్రదించండి."
            else:
                message = f"Dear {name}, based on the prediction, there is a risk of heart disease. Please consult a doctor immediately."
        else:
            result = "No Heart Disease Detected"
            if lang == "Hindi":
                message = f"प्रिय {name}, आपके परिणाम के अनुसार, हृदय रोग का कोई संकेत नहीं है। स्वस्थ रहें और अपना ख्याल रखें।"
            elif lang == "Telugu":
                message = f"ప్రియమైన {name}, మీ ఫలితాల ప్రకారం హృదయ వ్యాధి యొక్క ఎలాంటి లక్షణాలు లేవు. ఆరోగ్యంగా ఉండండి."
            else:
                message = f"Dear {name}, based on the prediction, there is no sign of heart disease. Stay healthy and take care."
        st.success(f"Prediction: {result}")
        # Multi-Language Audio Output
        tts = gTTS(text=message, lang=lang_code[lang])
        tts.save("result.mp3")
        st.audio("result.mp3", format="audio/mp3")
    
        # Generate PDF with ALL DETAILS
        pdf_file = f"{name}_Heart_Report.pdf"
        c = canvas.Canvas(pdf_file)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(150, 800, "Heart Disease Prediction Report")
        c.setFont("Helvetica", 14)
        y = 750
        details = [
            f"Name              : {name}",
            f"Age               : {age}",
            f"Sex               : {'Male' if int(sex) == 1 else 'Female'}",
            f"Chest Pain Type   : {cp}",
            f"Rest BP           : {trestbps} mmHg",
            f"Cholesterol       : {chol} mg/dL",
            f"Fasting Sugar     : {fbs}",
            f"Rest ECG          : {restecg}",
            f"Max Heart Rate    : {thalach}",
            f"Exercise Angina   : {exang}",
            f"ST Depression     : {oldpeak}",
            f"Slope             : {slope}",
            f"Major Vessels     : {ca}",
            f"Thalassemia       : {thal}",
            f"Prediction        : {result}",
            f"Date & Time       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        for detail in details:
            c.drawString(100, y, detail)
            y -= 25
        c.save()
    
        # PDF Download
        with open(pdf_file, "rb") as pdf:
            st.download_button("Download Report PDF", data=pdf, file_name=pdf_file, mime='application/pdf')
        if prediction == 1:
            st.markdown("""
                        <div style='font-size:30px; font-weight:bold '>
                        Healthy Food Suggestions
                        </div>
                """, unsafe_allow_html=True)
            with st.expander(" List of food items are "):
                st.markdown("### 🍞 Whole Grains")
                st.write("""
                - Oats, brown rice, quinoa, whole wheat
                - Improves cholesterol levels
                - Helps maintain blood pressure
                """)
        
                st.markdown("### 🥬 Leafy Greens")
                st.write("""
                - Spinach, kale, broccoli, arugula
                - Rich in vitamins, minerals, and antioxidants
                - Lowers blood pressure and supports heart health
                """)
            
                st.markdown("### 🍎 Fruits")
                st.write("""
                - Berries, apples, oranges, pomegranates
                - High in fiber, vitamins, and antioxidants
                - Reduces inflammation and cholesterol
                """)
            
                st.markdown("### 🐟 Lean Proteins")
                st.write("""
                - Fish (salmon, mackerel - rich in Omega-3)
                - Skinless chicken, tofu, legumes
                - Supports muscle health without adding unhealthy fat
                """)
            
                st.markdown("### 🥑 Healthy Fats")
                st.write("""
                - Avocados, olive oil, nuts (almonds, walnuts), seeds (chia, flaxseed)
                - Helps reduce bad cholesterol (LDL) and increase good cholesterol (HDL)
                """)
            
                st.markdown("### 🚫 Foods to Avoid")
                st.write("""
                - Processed meats, fried foods, excessive salt
                - Sugary drinks, pastries, red meat
                - Avoid trans fats, limit saturated fats
                """)
        if prediction == 0:
            st.markdown(" Keep healthy . Take care of yourself ")
       


