# from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
# from sqlalchemy.orm import relationship
# from app.core.database import Base
# from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Branch(Base):
    __tablename__ = "Branch"
    Branch_Id = Column(Integer, primary_key=True, index=True)
    Branch_Name = Column(String(100), nullable=False)
    Location = Column(String(255))
    
    # Relationship: One Branch has many Doctors
    doctors = relationship("Doctor", back_populates="branch")

class Patient(Base):
    __tablename__ = "Patient"
    Patient_Id = Column(Integer, primary_key=True, index=True)
    Patient_Name = Column(String(100), nullable=False)
    Phone_Number = Column(String(15), unique=True, index=True)
    Email_Id = Column(String(100))
    Gender_Id = Column(Integer, default=1)
    
    CreatedBy = Column(Integer)
    CreatedIpAddress = Column(String(50))
    CreatedAt = Column(DateTime, default=datetime.now)

class Doctor(Base):
    __tablename__ = "Doctor"
    Doctor_Id = Column(Integer, primary_key=True, index=True)
    Doctor_Name = Column(String(100), nullable=False)
    Specialization = Column(String(100))
    Branch_Id = Column(Integer, ForeignKey("Branch.Branch_Id"))  # <--- NEW LINK
    
    # Relationships
    branch = relationship("Branch", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")

class Appointment(Base):
    __tablename__ = "Appointment"
    Appointment_Id = Column(Integer, primary_key=True, index=True)
    Patient_Id = Column(Integer, ForeignKey("Patient.Patient_Id"))
    Doctor_Id = Column(Integer, ForeignKey("Doctor.Doctor_Id"))
    Appointment_Date = Column(DateTime, nullable=False)
    Appointment_Status = Column(String(50), default="SCHEDULED")
    
    CreatedBy = Column(Integer)
    CreatedIpAddress = Column(String(50))
    CreatedAt = Column(DateTime, default=datetime.now)
    ModifiedBy = Column(Integer, nullable=True)
    ModifiedIpAddress = Column(String(50), nullable=True)
    ModifiedAt = Column(DateTime, nullable=True)
    DeletedAt = Column(DateTime, nullable=True)

    patient = relationship("Patient")
    doctor = relationship("Doctor", back_populates="appointments")

# --- ADD THESE TO THE BOTTOM OF models.py ---

class DiagnosticTest(Base):
    __tablename__ = "Diagnostic_Tests"

    Test_Id = Column(Integer, primary_key=True, index=True)
    Test_Name = Column(String(100))
    Department = Column(String(50))
    Is_Available = Column(Boolean)
    Price = Column(Float)
    Schedule = Column(String(255))
    Referral_Name = Column(String(255))
    Referral_Contact = Column(String(50))

class TestAppointment(Base):
    __tablename__ = "Test_Appointments"

    Test_Appt_Id = Column(Integer, primary_key=True, index=True)
    
    # IMPORTANT: Use "Patient.Patient_Id" (Capital P) to match your specific table name
    Patient_Id = Column(Integer, ForeignKey("Patient.Patient_Id")) 
    
    Test_Id = Column(Integer, ForeignKey("Diagnostic_Tests.Test_Id"))
    Appointment_Date = Column(DateTime)
    Status = Column(String(20), default="CONFIRMED")