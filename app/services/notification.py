# import smtplib
# import os
# from dotenv import load_dotenv
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# # Load variables from .env.local file
# load_dotenv(".env.local")

# # --- CONFIGURATION ---
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
# SENDER_EMAIL = os.getenv("MAIL_USERNAME")
# SENDER_PASSWORD = os.getenv("MAIL_PASSWORD")

# # --- THE NEW PROFESSIONAL SIGNATURE ---
# SIGNATURE = """
# Best Regards,

# Medicare Hospital Administration
# Patient Care Services Team
# ------------------------------------------------------
# Helpline: +91-999-888-7777
# Email:    support@medicarehospital.com
# ------------------------------------------------------
# """

# def send_email(to_email: str, subject: str, body: str):
#     if not to_email:
#         print("⚠️ No email address provided, skipping email.")
#         return
    
#     if not SENDER_EMAIL or not SENDER_PASSWORD:
#         print("❌ Error: Email credentials missing in .env.local")
#         return

#     try:
#         msg = MIMEMultipart()
#         msg['From'] = f"Medicare Hospital <{SENDER_EMAIL}>"
#         msg['To'] = to_email
#         msg['Subject'] = subject
#         msg.attach(MIMEText(body, 'plain'))

#         server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
#         server.starttls()
#         server.login(SENDER_EMAIL, SENDER_PASSWORD)
#         server.send_message(msg)
#         server.quit()
#         print(f"✅ Email sent successfully to {to_email}")
#     except Exception as e:
#         print(f"❌ Failed to send email: {e}")

# # ==========================================
# # EMAIL TEMPLATES
# # ==========================================

# def send_welcome_email(name: str, email: str, patient_id: int):
#     subject = "Welcome to Medicare Hospital - Registration Complete"
#     body = f"""Dear {name},

# We are pleased to welcome you to the Medicare Hospital network. 

# Your Registration is Complete.
# --------------------------------
# Your Patient ID: {patient_id}
# --------------------------------
# (Please save this ID. You will need it to book or manage appointments.)

# You can now visit any of our branches (Delhi or Bangalore). We look forward to serving you.

# {SIGNATURE}"""
#     send_email(email, subject, body)

# def send_booking_confirmation(email: str, doctor_name: str, time: str, patient_id: int):
#     subject = "Appointment Confirmed - Medicare Hospital"
#     body = f"""Dear Patient,

# Your appointment has been successfully booked.

# Appointment Details:
# --------------------------------
# Patient ID: {patient_id}
# Doctor:     {doctor_name}
# Time:       {time}
# Location:   Medicare Hospital Group
# --------------------------------

# Please arrive 15 minutes early.

# {SIGNATURE}"""
#     send_email(email, subject, body)

# # --- UPDATED: NOW ACCEPTS DOCTOR NAME ---
# def send_reschedule_notification(email: str, doctor_name: str, old_time: str, new_time: str, patient_id: int):
#     subject = "Appointment Rescheduled - Medicare Hospital"
#     body = f"""Dear Patient,

# As per your request, your appointment has been rescheduled.

# Updated Slot:
# --------------------------------
# Patient ID: {patient_id}
# Doctor:     {doctor_name}
# Old Time:   {old_time}
# New Time:   {new_time}
# --------------------------------

# We apologize for any inconvenience.

# {SIGNATURE}"""
#     send_email(email, subject, body)

# def send_cancellation_notification(email: str, time: str, patient_id: int):
#     subject = "Appointment Cancellation - Medicare Hospital"
#     body = f"""Dear Patient,

# This is to confirm that your appointment has been cancelled.

# Details:
# --------------------------------
# Patient ID: {patient_id}
# Cancelled Time: {time}
# --------------------------------

# If you need to book a new slot, please contact our Voice Assistant.

# {SIGNATURE}"""
#     send_email(email, subject, body)

# import smtplib
# import os
# from dotenv import load_dotenv
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# # Load variables from .env.local file
# load_dotenv(".env.local")

# # --- CONFIGURATION ---
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
# SENDER_EMAIL = os.getenv("MAIL_USERNAME")
# SENDER_PASSWORD = os.getenv("MAIL_PASSWORD")

# # --- HTML STYLES (Professional Teal Theme) ---
# # This CSS makes the email look like a real app interface.
# HTML_HEAD = """
# <html>
# <head>
# <style>
#     body { font-family: 'Arial', sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }
#     .container { max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
#     .header { background-color: #0F766E; color: white; padding: 20px; text-align: center; }
#     .header h1 { margin: 0; font-size: 24px; }
#     .content { padding: 30px; color: #333333; line-height: 1.6; }
#     .card { background: #F0FDFA; border-left: 5px solid #0F766E; padding: 15px; margin: 20px 0; border-radius: 4px; }
#     .field { margin-bottom: 10px; }
#     .label { font-weight: bold; color: #555; display: inline-block; width: 120px; }
#     .value { font-weight: 500; color: #000; }
#     .footer { background-color: #333; color: #aaa; text-align: center; padding: 15px; font-size: 12px; }
#     .btn { display: inline-block; background: #0F766E; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px; }
# </style>
# </head>
# <body>
# <div class="container">
#     <div class="header">
#         <h1>🏥 Medicare Hospital</h1>
#     </div>
# """

# HTML_FOOTER = """
#     <div class="footer">
#         <p>Medicare Hospital Administration | Patient Care Team</p>
#         <p>Helpline: +91-999-888-7777 | Email: support@medicarehospital.com</p>
#         <p>&copy; 2026 Medicare Hospital. All rights reserved.</p>
#     </div>
# </div>
# </body>
# </html>
# """

# def send_email(to_email: str, subject: str, html_body: str):
#     if not to_email:
#         print("⚠️ No email address provided, skipping email.")
#         return
    
#     if not SENDER_EMAIL or not SENDER_PASSWORD:
#         print("❌ Error: Email credentials missing in .env.local")
#         return

#     try:
#         msg = MIMEMultipart()
#         msg['From'] = f"Medicare Hospital <{SENDER_EMAIL}>"
#         msg['To'] = to_email
#         msg['Subject'] = subject
#         # IMPORTANT: We use 'html' here instead of 'plain'
#         msg.attach(MIMEText(html_body, 'html'))

#         server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
#         server.starttls()
#         server.login(SENDER_EMAIL, SENDER_PASSWORD)
#         server.send_message(msg)
#         server.quit()
#         print(f"✅ HTML Email sent successfully to {to_email}")
#     except Exception as e:
#         print(f"❌ Failed to send email: {e}")

# # ==========================================
# # PROFESSIONAL EMAIL TEMPLATES
# # ==========================================

# def send_welcome_email(name: str, email: str, patient_id: int):
#     subject = "Welcome to Medicare Hospital - Registration Complete"
#     body = f"""
#     <div class="content">
#         <h2>Welcome, {name}!</h2>
#         <p>We are pleased to welcome you to the Medicare Hospital network. Your digital profile has been successfully created.</p>
        
#         <div class="card">
#             <div class="field"><span class="label">Patient Name:</span> <span class="value">{name}</span></div>
#             <div class="field"><span class="label">Patient ID:</span> <span class="value" style="font-size: 18px; color: #0F766E;">{patient_id}</span></div>
#             <div class="field"><span class="label">Status:</span> <span class="value">Active & Verified</span></div>
#         </div>

#         <p><strong>Please save your Patient ID.</strong> You will need it to book appointments via our Voice AI Assistant.</p>
#     </div>
#     """
#     send_email(email, subject, HTML_HEAD + body + HTML_FOOTER)

# def send_booking_confirmation(email: str, doctor_name: str, time: str, patient_id: int):
#     # Generates a random-looking Appt ID for display if you don't pass the real one, 
#     # but ideally, you should pass the real DB ID if you have it. 
#     # For now, we keep the function signature simple as requested.
    
#     subject = "Appointment Confirmed - Medicare Hospital"
#     body = f"""
#     <div class="content">
#         <h2>✅ Appointment Confirmed</h2>
#         <p>Dear Patient, your appointment has been successfully scheduled with our specialist.</p>
        
#         <div class="card">
#             <div class="field"><span class="label">Patient ID:</span> <span class="value">{patient_id}</span></div>
#             <div class="field"><span class="label">Doctor:</span> <span class="value">{doctor_name}</span></div>
#             <div class="field"><span class="label">Date & Time:</span> <span class="value">{time}</span></div>
#             <div class="field"><span class="label">Location:</span> <span class="value">Medicare Hospital Group</span></div>
#         </div>

#         <p>Please arrive <strong>15 minutes early</strong> for pre-check procedures.</p>
#     </div>
#     """
#     send_email(email, subject, HTML_HEAD + body + HTML_FOOTER)

# def send_reschedule_notification(email: str, doctor_name: str, old_time: str, new_time: str, patient_id: int):
#     subject = "Appointment Rescheduled - Medicare Hospital"
#     body = f"""
#     <div class="content">
#         <h2>🗓️ Appointment Updated</h2>
#         <p>As per your request, your upcoming appointment has been rescheduled.</p>
        
#         <div class="card">
#             <div class="field"><span class="label">Patient ID:</span> <span class="value">{patient_id}</span></div>
#             <div class="field"><span class="label">Doctor:</span> <span class="value">{doctor_name}</span></div>
#             <div class="field"><span class="label" style="color:red;">Old Time:</span> <span class="value" style="text-decoration: line-through;">{old_time}</span></div>
#             <div class="field"><span class="label" style="color:green;">New Time:</span> <span class="value">{new_time}</span></div>
#         </div>

#         <p>We apologize for any inconvenience. See you soon!</p>
#     </div>
#     """
#     send_email(email, subject, HTML_HEAD + body + HTML_FOOTER)

# def send_cancellation_notification(email: str, time: str, patient_id: int):
#     subject = "Appointment Cancellation - Medicare Hospital"
#     body = f"""
#     <div class="content">
#         <h2 style="color: #DC2626;">🚫 Appointment Cancelled</h2>
#         <p>This email confirms that your scheduled appointment has been cancelled.</p>
        
#         <div class="card" style="border-left-color: #DC2626; background: #FEF2F2;">
#             <div class="field"><span class="label">Patient ID:</span> <span class="value">{patient_id}</span></div>
#             <div class="field"><span class="label">Cancelled Slot:</span> <span class="value">{time}</span></div>
#             <div class="field"><span class="label">Status:</span> <span class="value" style="color: #DC2626;">Cancelled</span></div>
#         </div>

#         <p>If you would like to book a new appointment, please call our AI Assistant again.</p>
#     </div>
#     """
#     send_email(email, subject, HTML_HEAD + body + HTML_FOOTER)

import smtplib
import logging
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set up the logger
logging.basicConfig(level=logging.INFO) # <--- Add this
logger = logging.getLogger(__name__)    # <--- Add this
# Load variables from .env.local file
load_dotenv(".env.local")

# --- CONFIGURATION ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("MAIL_USERNAME")
SENDER_PASSWORD = os.getenv("MAIL_PASSWORD")

# --- HTML STYLES (Professional Teal Theme) ---
HTML_HEAD = """
<html>
<head>
<style>
    body { font-family: 'Arial', sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }
    .container { max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .header { background-color: #0F766E; color: white; padding: 20px; text-align: center; }
    .header h1 { margin: 0; font-size: 24px; }
    .content { padding: 30px; color: #333333; line-height: 1.6; }
    .card { background: #F0FDFA; border-left: 5px solid #0F766E; padding: 15px; margin: 20px 0; border-radius: 4px; }
    .field { margin-bottom: 10px; }
    .label { font-weight: bold; color: #555; display: inline-block; width: 140px; }
    .value { font-weight: 500; color: #000; }
    .footer { background-color: #333; color: #aaa; text-align: center; padding: 15px; font-size: 12px; }
    .highlight-id { color: #0F766E; font-weight: bold; font-family: monospace; font-size: 16px; }
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🏥 Medicare Hospital</h1>
    </div>
"""

HTML_FOOTER = """
    <div class="footer">
        <p>Medicare Hospital Administration | Patient Care Team</p>
        <p>Helpline: +91-999-888-7777 | Email: support@medicarehospital.com</p>
        <p>&copy; 2026 Medicare Hospital. All rights reserved.</p>
    </div>
</div>
</body>
</html>
"""

def send_email(to_email: str, subject: str, html_body: str):
    if not to_email:
        print("⚠️ No email address provided, skipping email.")
        return
    
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("❌ Error: Email credentials missing in .env.local")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = f"Medicare Hospital <{SENDER_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ HTML Email sent successfully to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# ==========================================
# PROFESSIONAL EMAIL TEMPLATES
# ==========================================

def send_welcome_email(name: str, email: str, patient_id: int):
    subject = "Welcome to Medicare Hospital - Registration Complete"
    body = f"""
    <div class="content">
        <h2>Welcome, {name}!</h2>
        <p>We are pleased to welcome you to the Medicare Hospital network.</p>
        
        <div class="card">
            <div class="field"><span class="label">Patient Name:</span> <span class="value">{name}</span></div>
            <div class="field"><span class="label">Your Patient ID:</span> <span class="highlight-id">{patient_id}</span></div>
            <div class="field"><span class="label">Status:</span> <span class="value">Active & Verified</span></div>
        </div>

        <p><strong>Please save your Patient ID.</strong> You will need it to book appointments.</p>
    </div>
    """
    send_email(email, subject, HTML_HEAD + body + HTML_FOOTER)

def send_booking_confirmation(email: str, doctor_name: str, time: str, patient_id: int, appointment_id: int):
    subject = f"Appointment Confirmed (ID: {appointment_id})"
    body = f"""
    <div class="content">
        <h2>✅ Appointment Confirmed</h2>
        <p>Dear Patient, your appointment has been successfully scheduled.</p>
        
        <div class="card">
            <div class="field"><span class="label">Appointment ID:</span> <span class="highlight-id">#{appointment_id}</span></div>
            <div class="field"><span class="label">Patient ID:</span> <span class="value">{patient_id}</span></div>
            <div class="field"><span class="label">Doctor:</span> <span class="value">{doctor_name}</span></div>
            <div class="field"><span class="label">Date & Time:</span> <span class="value">{time}</span></div>
        </div>

        <p>Please arrive <strong>15 minutes early</strong> with your Appointment ID.</p>
    </div>
    """
    send_email(email, subject, HTML_HEAD + body + HTML_FOOTER)

def send_reschedule_notification(email: str, doctor_name: str, old_time: str, new_time: str, patient_id: int, appointment_id: int):
    subject = f"Appointment Rescheduled (ID: {appointment_id})"
    body = f"""
    <div class="content">
        <h2>🗓️ Appointment Updated</h2>
        <p>As per your request, your upcoming appointment has been moved.</p>
        
        <div class="card">
            <div class="field"><span class="label">Appointment ID:</span> <span class="highlight-id">#{appointment_id}</span></div>
            <div class="field"><span class="label">Doctor:</span> <span class="value">{doctor_name}</span></div>
            <div class="field"><span class="label" style="color:red;">Old Time:</span> <span class="value" style="text-decoration: line-through;">{old_time}</span></div>
            <div class="field"><span class="label" style="color:green;">New Time:</span> <span class="value">{new_time}</span></div>
        </div>

        <p>Your previous slot has been released.</p>
    </div>
    """
    send_email(email, subject, HTML_HEAD + body + HTML_FOOTER)

def send_cancellation_notification(email: str, time: str, patient_id: int, appointment_id: int):
    subject = f"Appointment Cancellation (ID: {appointment_id})"
    body = f"""
    <div class="content">
        <h2 style="color: #DC2626;">🚫 Appointment Cancelled</h2>
        <p>This email confirms that your scheduled appointment has been cancelled.</p>
        
        <div class="card" style="border-left-color: #DC2626; background: #FEF2F2;">
            <div class="field"><span class="label">Appointment ID:</span> <span class="highlight-id" style="color:#DC2626;">#{appointment_id}</span></div>
            <div class="field"><span class="label">Cancelled Slot:</span> <span class="value">{time}</span></div>
            <div class="field"><span class="label">Status:</span> <span class="value" style="color: #DC2626;">Cancelled</span></div>
        </div>
    </div>
    """
    send_email(email, subject, HTML_HEAD + body + HTML_FOOTER)

# --- ADD THIS TO THE BOTTOM OF app/services/notification.py ---

def send_test_booking_confirmation(to_email: str, patient_name: str, test_name: str, date_time: str, booking_id: int):
    """
    Sends a professional confirmation email specifically for Diagnostic Tests.
    """
    subject = f"✅ Booking Confirmed: {test_name}"
    
    # Professional HTML Template
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
                <h2 style="color: #2c3e50; text-align: center;">Medicare Hospital</h2>
                <h3 style="color: #27ae60; text-align: center;">Diagnostic Test Confirmed</h3>
                
                <p>Dear <b>{patient_name}</b>,</p>
                <p>Your booking for a <b>{test_name}</b> has been successfully confirmed.</p>
                
                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><b>📅 Date & Time:</b> {date_time}</p>
                    <p><b>🔬 Test Name:</b> {test_name}</p>
                    <p><b>🆔 Booking Reference:</b> T-{booking_id}</p>
                </div>

                <p><b>Instructions:</b></p>
                <ul>
                    <li>Please arrive 15 minutes before your scheduled time.</li>
                    <li>Carry a valid ID proof.</li>
                    <li>If this is a blood test, please check if fasting is required.</li>
                </ul>

                <hr style="border: 0; border-top: 1px solid #eee;">
                <p style="font-size: 12px; color: #777; text-align: center;">
                    Medicare Hospital • 123 Health Street, Delhi<br>
                    Need help? Call us at 999-888-777
                </p>
            </div>
        </body>
    </html>
    """

    try:
        # We reuse your existing 'send_email' function that you already have in this file
        send_email(to_email, subject, body)
        logger.info(f"Test confirmation email sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send test email: {e}")