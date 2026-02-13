
from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Any, Union
from app.services.rag_service import kb_engine
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, model_validator
from app.core.database import get_db
from app.models.models import Doctor, Patient, Appointment, Branch, DiagnosticTest, TestAppointment
from app.services import notification
import logging
import re
from thefuzz import process

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# ==========================================
# 1. HELPERS
# ==========================================

def clean_doctor_name(name_input: str) -> str:
    if not name_input: return ""
    name_input = name_input.lower().strip()
    # Remove titles and filler words
    name_input = re.sub(r'\b(dr\.?|doctor|mr\.?|mrs\.?|please|book|appointment|with|for|i want|check)\b', '', name_input, flags=re.IGNORECASE)
    name_input = re.sub(r'\s+', ' ', name_input).strip()
    return name_input.title()

def parse_datetime(date_str: str, time_str: str) -> datetime:
    full_str = f"{date_str} {time_str}".strip()
    try:
        return datetime.strptime(full_str, "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            return datetime.strptime(full_str, "%Y-%m-%d %I:%M %p")
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid time format: {time_str}")

def generate_slots(date_str: str) -> List[str]:
    slots = []
    current = datetime.strptime(f"{date_str} 09:00", "%Y-%m-%d %H:%M")
    end_time = datetime.strptime(f"{date_str} 17:00", "%Y-%m-%d %H:%M")
    while current < end_time:
        slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=30)
    return slots

# ==========================================
# 2. PYDANTIC MODELS (Strict Input Schema)
# ==========================================

# --- THIS WAS MISSING ---
class VerifyRequest(BaseModel):
    patient_id: int

    @model_validator(mode='before')
    @classmethod
    def fix_keys(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Auto-fix if AI sends "patientId" instead of "patient_id"
            if 'patient_id' not in data:
                data['patient_id'] = data.get('patientId') or data.get('id')
        return data

# --- UPDATED REQUEST MODEL ---
class GetDoctorsRequest(BaseModel):
    branch_id: Optional[int] = None
    speciality: Optional[str] = None  # <--- ADDED THIS

    @model_validator(mode='before')
    @classmethod
    def fix_keys(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # 1. Fix Branch ID
            if 'branch_id' not in data:
                data['branch_id'] = data.get('branchId') or data.get('branch') or data.get('id')
            
            # 2. Fix Speciality (Handle AI variations)
            if 'speciality' not in data:
                data['speciality'] = (
                    data.get('specialization') or 
                    data.get('category') or 
                    data.get('type')
                )
        return data

class AvailabilityRequest(BaseModel):
    doctor_name: str
    date: str
    branch_id: Optional[int] = None

    @model_validator(mode='before')
    @classmethod
    def fix_keys(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # 1. CLEAN KEYS: Remove \r, \n, and spaces from all keys
            clean_data = {}
            for k, v in data.items():
                # This line fixes the "doctor_name\r\n" error
                clean_key = k.strip().replace('\r', '').replace('\n', '')
                clean_data[clean_key] = v
            data = clean_data

            # 2. Map Aliases (Handle AI mistakes)
            if 'doctor_name' not in data:
                data['doctor_name'] = data.get('doctor') or data.get('doctorName')
            if 'branch_id' not in data:
                data['branch_id'] = data.get('branchId') or data.get('branch')
            
            # 3. Handle Empty Strings
            if data.get('branch_id') == "":
                data['branch_id'] = None
                
        return data

class PatientBase(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    gender_id: int = 1

# --- PASTE THIS IN THE PYDANTIC MODELS SECTION ---

class BookRequest(BaseModel):
    # We use Strict types here because the validator below fixes everything first
    patient_id: int
    doctor_name: str
    date: str
    time: str

    @model_validator(mode='before')
    @classmethod
    def bulletproof_inputs(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # 1. GHOST BUSTER: Strip \r\n and spaces from ALL keys
            clean_data = {}
            for k, v in data.items():
                clean_key = k.strip().replace('\r', '').replace('\n', '')
                clean_data[clean_key] = v
            data = clean_data

            # 2. Map Aliases (Fix Vapi's naming mistakes)
            if 'patient_id' not in data:
                data['patient_id'] = data.get('patientId') or data.get('id')
            if 'doctor_name' not in data:
                data['doctor_name'] = data.get('doctor') or data.get('doctorName')

            # 3. FIX PATIENT ID: Convert string "210001" -> int 210001
            pid = data.get('patient_id')
            if isinstance(pid, str):
                # Remove anything that isn't a number (e.g. "ID: 210001" -> "210001")
                numeric_id = "".join(filter(str.isdigit, pid))
                if numeric_id:
                    data['patient_id'] = int(numeric_id)
                else:
                    data['patient_id'] = None # Let validation fail if no ID

        return data
# Paste this in your Pydantic Models section
class RescheduleRequest(BaseModel):
    # Relaxed types to prevent 422 crashes
    patient_id: Optional[Union[int, str]] = None
    new_date: Optional[str] = None
    new_time: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def bulletproof_inputs(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # 1. GHOST BUSTER: Strip \r\n and spaces from ALL keys
            clean_data = {}
            for k, v in data.items():
                clean_key = k.strip().replace('\r', '').replace('\n', '')
                clean_data[clean_key] = v
            data = clean_data

            # 2. Map Aliases (Fix AI naming mistakes)
            if 'patient_id' not in data:
                data['patient_id'] = data.get('patientId') or data.get('id')
            if 'new_date' not in data:
                data['new_date'] = data.get('date') or data.get('newDate')
            if 'new_time' not in data:
                data['new_time'] = data.get('time') or data.get('newTime')

            # 3. FIX PATIENT ID: Convert string "210001" -> int 210001
            pid = data.get('patient_id')
            if pid:
                # Turn "210001" or "ID: 210001" into integer 210001
                numeric_id = "".join(filter(str.isdigit, str(pid)))
                if numeric_id:
                    data['patient_id'] = int(numeric_id)
                else:
                    data['patient_id'] = None
            
        return data
class CancelRequest(BaseModel):
    patient_id: Optional[Union[int, str]] = None

    @model_validator(mode='before')
    @classmethod
    def fix_keys(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Clean keys deeply (remove newlines/whitespace)
            data = {k.strip().replace('\n', ''): v for k, v in data.items()}
            
            if 'patient_id' not in data:
                data['patient_id'] = data.get('patientId') or data.get('id')
        return data
    
class TestRequest(BaseModel):
    test_name: str
    department: str  # "cardiology" or "neurology"

    @model_validator(mode='before')
    @classmethod
    def fix_keys(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Clean keys (remove \r\n, spaces)
            clean_data = {}
            for k, v in data.items():
                clean_key = k.strip().replace('\r', '').replace('\n', '')
                clean_data[clean_key] = v
            data = clean_data
            
            # Map Aliases
            if 'test_name' not in data:
                data['test_name'] = data.get('test') or data.get('name')
            if 'department' not in data:
                data['department'] = data.get('dept')
        return data
    
class BookTestRequest(BaseModel):
    patient_id: int
    test_name: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM

    @model_validator(mode='before')
    @classmethod
    def bulletproof_inputs(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # 1. GHOST BUSTER: Strip \r\n and spaces from ALL keys
            clean_data = {}
            for k, v in data.items():
                clean_key = k.strip().replace('\r', '').replace('\n', '')
                clean_data[clean_key] = v
            data = clean_data

            # 2. Map Aliases (Fix Vapi's naming mistakes)
            if 'patient_id' not in data:
                data['patient_id'] = data.get('patientId') or data.get('id')
            if 'test_name' not in data:
                data['test_name'] = data.get('test') or data.get('name')

            # 3. FIX PATIENT ID: Convert string "210001" -> int 210001
            pid = data.get('patient_id')
            if isinstance(pid, str):
                numeric_id = "".join(filter(str.isdigit, pid))
                if numeric_id:
                    data['patient_id'] = int(numeric_id)
                else:
                    data['patient_id'] = None 
        return data

# --- HELPER Safe Int Parser ---
def get_safe_int(val: Any) -> Optional[int]:
    if not val: return None
    try: return int(str(val).strip())
    except ValueError: return None

# ==========================================
# 3. ENDPOINTS (ALL POST)
# ==========================================

@router.post("/branches")
def get_branches(db: Session = Depends(get_db)):
    branches = db.query(Branch).all()
    return [{"id": b.Branch_Id, "name": b.Branch_Name, "location": b.Location} for b in branches]

@router.post("/doctors")
def get_doctors(req: GetDoctorsRequest, db: Session = Depends(get_db)):
    """
    Fetch doctors, optionally filtered by Branch and Speciality.
    """
    query = db.query(Doctor)
    
    # Filter by Branch (if provided)
    if req.branch_id:
        query = query.filter(Doctor.Branch_Id == req.branch_id)
        
    # Filter by Speciality (if provided)
    if req.speciality:
        # Case-insensitive search (e.g., "cardio" matches "Cardiologist")
        query = query.filter(Doctor.Specialization.ilike(f"%{req.speciality}%"))
        
    doctors = query.all()
    
    if not doctors:
        return []

    return [
        {
            "id": d.Doctor_Id, 
            "name": d.Doctor_Name, 
            "specialization": d.Specialization, 
            "branch_id": d.Branch_Id
        } 
        for d in doctors
    ]

# --- THIS WAS MISSING ---
@router.post("/patient/verify")
def verify_patient(req: VerifyRequest, db: Session = Depends(get_db)):
    """Verify if a patient exists by ID."""
    logger.info(f"Verifying Patient ID: {req.patient_id}")
    patient = db.query(Patient).filter(Patient.Patient_Id == req.patient_id).first()
    if not patient: raise HTTPException(status_code=404, detail="Patient ID invalid.")
    return {"status": "verified", "patient_id": patient.Patient_Id, "name": patient.Patient_Name}

@router.post("/availability")
def check_availability(req: AvailabilityRequest, db: Session = Depends(get_db)):
    # Handled missing params gracefully to prevent Vapi 422 loops
    if not req.doctor_name:
        return {"status": "error", "message": "Please provide a doctor name."}
    
    clean_doctor = clean_doctor_name(req.doctor_name)
    
    # Use today's date if not provided (or handle error)
    if not req.date:
         return {"status": "error", "message": "Please provide a date (YYYY-MM-DD)."}

    logger.info(f"Checking Availability: Doc='{clean_doctor}', Date={req.date}")

    query = db.query(Doctor).filter(Doctor.Doctor_Name.ilike(f"%{clean_doctor}%"))
    if req.branch_id: query = query.filter(Doctor.Branch_Id == req.branch_id)
    doctor_obj = query.first()

    if not doctor_obj:
        # Fallback: Fuzzy Search
        all_docs_query = db.query(Doctor)
        if req.branch_id: all_docs_query = all_docs_query.filter(Doctor.Branch_Id == req.branch_id)
        all_docs = all_docs_query.all()
        doc_names = [d.Doctor_Name for d in all_docs]
        
        if doc_names:
            match = process.extractOne(clean_doctor, doc_names)
            if match and match[1] > 70: 
                doctor_obj = next(d for d in all_docs if d.Doctor_Name == match[0])

    if not doctor_obj: 
        return {"status": "error", "message": f"Doctor '{clean_doctor}' not found."}

    try: target_date = datetime.strptime(req.date, "%Y-%m-%d")
    except ValueError: return {"status": "error", "message": "Invalid date format. Use YYYY-MM-DD."}
    
    if target_date.weekday() == 6: return {"doctor": doctor_obj.Doctor_Name, "available_slots": [], "message": "Closed on Sundays."}

    booked = db.query(Appointment).filter(Appointment.Doctor_Id == doctor_obj.Doctor_Id, Appointment.Appointment_Date >= target_date, Appointment.Appointment_Date < target_date + timedelta(days=1), Appointment.Appointment_Status.in_(["SCHEDULED", "RESCHEDULED"])).all()
    booked_times = {appt.Appointment_Date.strftime("%H:%M") for appt in booked}
    all_slots = generate_slots(req.date)
    available = [slot for slot in all_slots if slot not in booked_times]
    
    return {"doctor": doctor_obj.Doctor_Name, "branch": doctor_obj.branch.Branch_Name, "available_slots": available,"system_instruction": "STOP. Read these slots to the user and wait for them to pick one. DO NOT call book_appointment yet."}

@router.post("/patient/register", status_code=status.HTTP_201_CREATED)
def register_patient(patient_data: PatientBase, request: Request, db: Session = Depends(get_db)):
    existing = db.query(Patient).filter(Patient.Phone_Number == patient_data.phone).first()
    if existing: return {"status": "exists", "patient_id": existing.Patient_Id}
    new_patient = Patient(Patient_Name=patient_data.name, Phone_Number=patient_data.phone, Email_Id=patient_data.email, Gender_Id=patient_data.gender_id, CreatedBy=1, CreatedIpAddress=request.client.host, CreatedAt=datetime.now())
    db.add(new_patient); db.commit(); db.refresh(new_patient)
    if patient_data.email: notification.send_welcome_email(patient_data.name, patient_data.email, new_patient.Patient_Id)
    return {"status": "created", "patient_id": new_patient.Patient_Id}

# --- PASTE THIS IN THE ENDPOINTS SECTION ---

@router.post("/book")
def book_appointment(booking: BookRequest, request: Request, db: Session = Depends(get_db)):
    """
    Definition: Used to book an appointment.
    Input Parameters:
      - booking (BookRequest): JSON body containing patient_id, doctor_name, date, time.
    Response Format: JSON with status ("confirmed" or "error") and message.
    """
    # 1. DEBUG LOG: See EXACTLY what Vapi sent
    logger.info(f"BOOKING REQUEST DATA: {booking.dict()}")

    # 2. FAIL FAST: Validate date
    if not booking.date or not str(booking.date).strip():
        logger.warning("Booking failed: Missing 'date' parameter.")
        return {
            "status": "error",
            "message": "I need the appointment date. Please ask the user which date they want."
        }

    # 3. FAIL FAST: Validate time
    if not booking.time or not str(booking.time).strip():
        logger.warning("Booking failed: Missing 'time' parameter.")
        return {
            "status": "error",
            "message": "I need the appointment time. Please ask the user: 'What time would you like to book?' and then call this tool again with the time filled in."
        }

    # Normalize time safely (for voice / AI messy input)
    time_clean = str(booking.time).strip()

    # 4. Logic & Parse Date/Time
    pid = booking.patient_id
    try:
        appt_dt = parse_datetime(booking.date, time_clean)
        # --- NEW: Format time perfectly (e.g. "09:00") ---
        formatted_time = appt_dt.strftime("%H:%M")
    except Exception as e:
        logger.error(f"Date Parse Error: {e}")
        return {"status": "error", "message": "I didn't understand that date or time. Please say it again clearly."}
        
    if appt_dt.weekday() == 6: 
        return {"status": "error", "message": "The clinic is closed on Sundays."}

    # 5. Find Doctor (with Fuzzy Fallback)
    clean_doc = clean_doctor_name(booking.doctor_name)
    doctor = db.query(Doctor).filter(Doctor.Doctor_Name.ilike(f"%{clean_doc}%")).first()
    
    if not doctor:
        all_docs = db.query(Doctor).all()
        names = [d.Doctor_Name for d in all_docs]
        match = process.extractOne(clean_doc, names) if names else None
        if match and match[1] > 70: 
            doctor = next(d for d in all_docs if d.Doctor_Name == match[0])

    if not doctor: 
        return {"status": "error", "message": f"I couldn't find a doctor named '{clean_doc}'."}

    # 6. Find Patient
    patient = db.query(Patient).filter(Patient.Patient_Id == pid).first()
    if not patient: 
        return {"status": "error", "message": "I can't find your Patient ID. Please register first."}

    # 7. Check for Conflicts
    conflict = db.query(Appointment).filter(
        Appointment.Doctor_Id == doctor.Doctor_Id, 
        Appointment.Appointment_Date == appt_dt, 
        Appointment.Appointment_Status.in_(["SCHEDULED", "RESCHEDULED"])
    ).first()
    
    if conflict: 
        return {"status": "error", "message": "That time slot is already taken. Please pick another time."}

    # 8. Create Appointment
    new_appt = Appointment(
        Patient_Id=patient.Patient_Id, 
        Doctor_Id=doctor.Doctor_Id, 
        Appointment_Date=appt_dt, 
        Appointment_Status="SCHEDULED", 
        CreatedBy=1, 
        CreatedIpAddress=request.client.host, 
        CreatedAt=datetime.now()
    )
    db.add(new_appt)
    db.commit()
    
    # 9. Send Notification (Using formatted_time)
    if patient.Email_Id: 
        notification.send_booking_confirmation(
            patient.Email_Id, 
            doctor.Doctor_Name, 
            f"{booking.date} {formatted_time}", 
            patient.Patient_Id,
            new_appt.Appointment_Id
        )
        
    # 10. Return Success (Using formatted_time)
    return {
        "status": "confirmed", 
        "appointment_id": new_appt.Appointment_Id, 
        "message": f"Appointment confirmed with Dr. {doctor.Doctor_Name} on {booking.date} at {formatted_time}."
    }

# Paste this in your Endpoints section
@router.post("/appointment/reschedule")
def reschedule_appointment(req: RescheduleRequest, request: Request, db: Session = Depends(get_db)):
    """
    Definition: Reschedule an existing appointment.
    """
    # 1. DEBUG LOG: See EXACTLY what Vapi sent
    logger.info(f"RESCHEDULE REQUEST DATA: {req.dict()}")

    # 2. FAIL FAST: Check for missing inputs
    if not req.patient_id:
        return {
            "status": "error", 
            "message": "I lost the Patient ID. Please ask the user for their ID again."
        }

    if not req.new_date or not str(req.new_date).strip():
        return {
            "status": "error", 
            "message": "I need the new date. Please ask the user: 'What date would you like to move your appointment to?'"
        }
    
    if not req.new_time or not str(req.new_time).strip():
        return {
            "status": "error", 
            "message": "I need the new time. Please ask the user: 'What time works for you?'"
        }

    # Normalize inputs
    time_clean = str(req.new_time).strip()
    
    # 3. Parse New Date/Time
    try:
        new_dt = parse_datetime(req.new_date, time_clean)
        formatted_time = new_dt.strftime("%H:%M")
    except Exception as e:
        logger.error(f"Date Parse Error: {e}")
        return {"status": "error", "message": "I didn't understand that date or time. Please say it again clearly."}

    if new_dt.weekday() == 6: 
        return {"status": "error", "message": "The clinic is closed on Sundays."}

    # 4. Find the Existing Appointment
    appt = db.query(Appointment).filter(
        Appointment.Patient_Id == req.patient_id, 
        Appointment.Appointment_Status.in_(["SCHEDULED", "RESCHEDULED"]), 
        Appointment.Appointment_Date >= datetime.now()
    ).order_by(Appointment.Appointment_Date.asc()).first()

    if not appt: 
        return {"status": "error", "message": "I couldn't find any upcoming appointments for your ID."}
    
    old_time_str = appt.Appointment_Date.strftime("%Y-%m-%d %H:%M")

    # 5. Check for Conflicts
    conflict = db.query(Appointment).filter(
        Appointment.Doctor_Id == appt.Doctor_Id,
        Appointment.Appointment_Date == new_dt,
        Appointment.Appointment_Status.in_(["SCHEDULED", "RESCHEDULED"])
    ).first()

    if conflict:
        return {"status": "error", "message": "That new time slot is already taken. Please pick another time."}
    # 6. Get Doctor Name (Needed for Email)
    doctor = db.query(Doctor).filter(Doctor.Doctor_Id == appt.Doctor_Id).first()
    doctor_name = doctor.Doctor_Name if doctor else "Unknown Doctor"
    
    # 6. Update Appointment
    appt.Appointment_Date = new_dt
    appt.Appointment_Status = "RESCHEDULED"
    appt.ModifiedAt = datetime.now()
    db.commit()
    
    # 7. Notify Patient
    patient = db.query(Patient).filter(Patient.Patient_Id == appt.Patient_Id).first()
    if patient and patient.Email_Id: 
        notification.send_reschedule_notification(
            patient.Email_Id, 
            doctor_name,
            old_time_str, 
            f"{req.new_date} {formatted_time}", 
            patient.Patient_Id,
            appt.Appointment_Id
            
        )

    return {
        "status": "rescheduled", 
        "message": f"Appointment successfully moved to {req.new_date} at {formatted_time}.",
        "new_time": f"{req.new_date} {formatted_time}"
    }
@router.post("/appointment/cancel")
def cancel_appointment(req: CancelRequest, request: Request, db: Session = Depends(get_db)):
    # --- SAFETY CHECK ---
    # If Vapi sends 0 or None, reject it immediately.
    if not req.patient_id or req.patient_id == 0:
        logger.error("Vapi sent an empty Patient ID for cancellation.")
        return {
            "status": "error", 
            "message": "I lost the patient ID. Please ask the user for their ID again or use the one from the verification step."
        }
    # --------------------
    # 1. Logging
    logger.info(f"Received Cancel Request for Patient ID: {req.patient_id}")

    # 2. Logic: Find the appointment
    # We use 'desc()' to find the LATEST appointment. 
    appt = db.query(Appointment).filter(
        Appointment.Patient_Id == req.patient_id,
        Appointment.Appointment_Status.in_(["SCHEDULED", "RESCHEDULED"])
    ).order_by(Appointment.Appointment_Date.desc()).first()
    
    # 3. Handle "Not Found"
    if not appt: 
        return {"status": "error", "message": "I couldn't find any active appointments for that ID."}
    
    # 4. Execute Cancel
    appt_time = appt.Appointment_Date.strftime("%Y-%m-%d %H:%M")
    appt_id = appt.Appointment_Id  # <--- CAPTURE ID HERE
    
    appt.Appointment_Status = "CANCELLED"
    appt.ModifiedBy = 1
    appt.ModifiedAt = datetime.now()
    db.commit()
    
    # 5. Notify (Now Passing Appointment ID)
    patient = db.query(Patient).filter(Patient.Patient_Id == appt.Patient_Id).first()
    if patient and patient.Email_Id: 
        notification.send_cancellation_notification(
            patient.Email_Id, 
            appt_time, 
            patient.Patient_Id,
            appt_id  # <--- ADDED THIS ARGUMENT
        )
    
    return {"status": "cancelled", "message": f"Appointment on {appt_time} has been cancelled."}

# --- Add this endpoint at the bottom of the file ---
# --- RAG / KNOWLEDGE BASE TOOL ---

# 1. The Input Model
class HospitalInfoRequest(BaseModel):
    query: str

    @model_validator(mode='before')
    @classmethod
    def clean_query(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Clean Keys
            clean_data = {}
            for k, v in data.items():
                clean_key = k.strip().replace('\r', '').replace('\n', '')
                clean_data[clean_key] = v
            data = clean_data
            
            # Map Aliases
            if 'query' not in data:
                data['query'] = data.get('question') or data.get('q') or data.get('text')
        return data

# 2. The Endpoint
@router.post("/hospital_info")
def get_hospital_info(req: HospitalInfoRequest):
    """
    Tool: Searches the hospital's knowledge base for general information.
    """
    # Import inside function to avoid circular dependency issues if any
    from app.services.rag_service import kb_engine
    
    logger.info(f"Searching Knowledge Base for: {req.query}")

    # Search
    context = kb_engine.search(req.query)

    # Return
    return {
        "results": context,
        "instruction": "Use the information above to answer the user's question. If the answer is not in the text, say you don't have that specific information."
    }
# ==========================================
# DIAGNOSTIC TEST ENDPOINTS
# ==========================================

@router.post("/check_test")
def check_test_availability(req: TestRequest, db: Session = Depends(get_db)):
    """
    Tool: Checks DB for test availability.
    Input: test_name (e.g., "ECG"), department ("cardiology")
    """
    logger.info(f"Checking Test: {req.test_name} in {req.department}")
    
    dept = req.department.lower()
    test_query = req.test_name.lower().strip()

    # 1. Search Database using SQL LIKE for fuzzy match
    # We use ilike for case-insensitive search
    test_obj = db.query(DiagnosticTest).filter(
        DiagnosticTest.Department.ilike(dept),
        DiagnosticTest.Test_Name.ilike(f"%{test_query}%")
    ).first()
    
    # 2. Handle Not Found
    if not test_obj:
        # Try finding without department filter as fallback
        test_obj = db.query(DiagnosticTest).filter(
            DiagnosticTest.Test_Name.ilike(f"%{test_query}%")
        ).first()

    if not test_obj:
        return {"status": "error", "message": f"I couldn't find a test named '{req.test_name}'."}

    # 3. Formulate Response based on DB Data
    if test_obj.Is_Available:
        return {
            "status": "available",
            "test": test_obj.Test_Name,
            "cost": f"₹{int(test_obj.Price) if test_obj.Price else 0}",
            "schedule": test_obj.Schedule,
            "message": f"Yes, the {test_obj.Test_Name} is available. It costs ₹{int(test_obj.Price)} and the schedule is: {test_obj.Schedule}."
        }
    else:
        return {
            "status": "unavailable",
            "test": test_obj.Test_Name,
            "referral": test_obj.Referral_Name,
            "contact": test_obj.Referral_Contact,
            "message": f"We do not conduct {test_obj.Test_Name} here. We recommend contacting {test_obj.Referral_Name} at {test_obj.Referral_Contact}."
        }

@router.post("/book_test")
def book_test_appointment(req: BookTestRequest, request: Request, db: Session = Depends(get_db)):
    """
    Tool: Books a diagnostic test for a patient.
    Input: patient_id, test_name, date, time
    """
    logger.info(f"BOOKING TEST REQUEST: {req.dict()}")

    # 1. Fail Fast checks
    if not req.date or not req.time:
         return {"status": "error", "message": "I need both date and time to book the test."}

    # 2. Find the Test ID
    test_obj = db.query(DiagnosticTest).filter(
        DiagnosticTest.Test_Name.ilike(f"%{req.test_name}%")
    ).first()

    if not test_obj:
        return {"status": "error", "message": f"Test '{req.test_name}' not found."}

    if not test_obj.Is_Available:
        return {"status": "error", "message": f"Sorry, {test_obj.Test_Name} is not available here."}

    # 3. Check if Patient Exists
    patient = db.query(Patient).filter(Patient.Patient_Id == req.patient_id).first()
    if not patient:
        return {"status": "error", "message": "Invalid Patient ID."}

    # 4. Create the Appointment
    try:
        # Use our helper to safely parse messy AI time formats
        appt_datetime = parse_datetime(req.date, req.time)
        formatted_time = appt_datetime.strftime("%H:%M")
        
        new_booking = TestAppointment(
            Patient_Id=req.patient_id,
            Test_Id=test_obj.Test_Id,
            Appointment_Date=appt_datetime,
            Status="CONFIRMED"
        )
        # ... (inside book_test_appointment) ...
        db.add(new_booking)
        db.commit()

        # NEW / PROFESSIONAL WAY:
        if patient.Email_Id:
             notification.send_test_booking_confirmation(
                to_email=patient.Email_Id,
                patient_name=patient.Patient_Name,
                test_name=test_obj.Test_Name,
                date_time=f"{req.date} {formatted_time}",
                booking_id=new_booking.Test_Appt_Id
            )

        return {
            "status": "success",
            "message": f"Confirmed! {test_obj.Test_Name} booked for {req.date} at {formatted_time}. Your booking ID is T-{new_booking.Test_Appt_Id}."
        }
    except Exception as e:
        logger.error(f"Test Booking Error: {e}")
        return {"status": "error", "message": "Failed to book test due to a server error."}