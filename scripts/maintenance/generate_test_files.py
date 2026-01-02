"""
Generate 100 diverse test files for comprehensive system testing
Covers all domains with realistic content
"""
import os
from pathlib import Path
import random

# Create incoming directory if it doesn't exist
incoming_dir = Path("data/incoming")
incoming_dir.mkdir(parents=True, exist_ok=True)

# Test file templates for different domains
test_files = {
    # Technology Domain (15 files)
    "drone_flight_controller_v2.txt": """
UAV Flight Controller System
Version 2.0 Technical Specification

Flight Control Algorithm:
- PID controller for stabilization
- GPS waypoint navigation
- Altitude hold using barometric sensor
- Return-to-home safety feature

Hardware:
- STM32F4 microcontroller
- MPU6050 IMU sensor
- GPS module NEO-6M
- ESC control for 4 motors
""",
    "web_api_documentation.md": """
# REST API Documentation

## Authentication Endpoints

### POST /api/auth/login
Request body:
```json
{
  "username": "string",
  "password": "string"
}
```

### GET /api/users
Returns list of all users (Admin only)

### POST /api/files/upload
Upload file with multipart/form-data
""",
    "cloud_deployment_guide.txt": """
AWS Deployment Guide

1. Setup EC2 Instance
   - t2.medium instance
   - Ubuntu 22.04 LTS
   - Security group ports: 80, 443, 22

2. Install Docker
   docker-compose up -d

3. Configure nginx reverse proxy
   SSL certificate with Let's Encrypt
""",
    "database_schema_design.sql": """
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
""",
    "kubernetes_deployment.yaml": """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: documind-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: documind
""",
    
    # Code Domain (15 files)
    "react_dashboard_component.jsx": """
import React, { useState, useEffect } from 'react';

function Dashboard() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    fetch('/api/analytics')
      .then(res => res.json())
      .then(setData);
  }, []);
  
  return (
    <div className="dashboard">
      <h1>Analytics Dashboard</h1>
      {data.map(item => <Card key={item.id} data={item} />)}
    </div>
  );
}

export default Dashboard;
""",
    "python_ml_algorithm.py": """
import numpy as np
from sklearn.ensemble import RandomForestClassifier

def train_model(X_train, y_train):
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    return model

def predict(model, X_test):
    return model.predict(X_test)
""",
    "backend_api_service.py": """
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class UserCreate(BaseModel):
    username: str
    email: str

@app.post("/users")
async def create_user(user: UserCreate):
    # Save to database
    return {"id": 1, "username": user.username}
""",
    "sorting_algorithm_analysis.txt": """
Sorting Algorithm Complexity Analysis

Quick Sort:
- Best Case: O(n log n)
- Average Case: O(n log n)
- Worst Case: O(n²)
- Space: O(log n)

Merge Sort:
- All Cases: O(n log n)
- Space: O(n)
""",
    "unit_tests_suite.py": """
import pytest

def test_user_creation():
    user = User(name="John", email="john@example.com")
    assert user.name == "John"
    assert user.email == "john@example.com"

def test_authentication():
    result = authenticate("admin", "password123")
    assert result.is_authenticated == True
""",
    
    # Education Domain (15 files)
    "machine_learning_lecture_notes.txt": """
Machine Learning - Lecture 5: Neural Networks

Topics Covered:
1. Perceptron Model
   - Linear classifier
   - Activation function
   
2. Backpropagation Algorithm
   - Forward pass
   - Compute loss
   - Backward pass
   - Update weights

Assignment: Implement a 2-layer neural network for MNIST classification
""",
    "python_programming_tutorial.md": """
# Python Programming Course - Week 3

## Topics:
- Lists and Tuples
- Dictionaries
- List Comprehensions

## Exercise:
```python
# Create a list of squares
squares = [x**2 for x in range(10)]
print(squares)
```

Assignment: Build a student grade management system
""",
    "calculus_problem_set.txt": """
Calculus Assignment - Chapter 5

1. Find the derivative of f(x) = 3x² + 2x - 5

2. Evaluate the integral: ∫(2x + 1)dx

3. Application Problem:
   A ball is thrown upward with velocity v(t) = -9.8t + 20
   Find the maximum height reached.
""",
    "data_science_project_report.txt": """
Data Science Project Report

Title: Predicting House Prices using Linear Regression

Dataset: Boston Housing Dataset
- 506 samples
- 13 features (crime rate, rooms, age, etc.)

Model Performance:
- R² Score: 0.85
- RMSE: $4,200

Conclusions: Number of rooms and location are strongest predictors
""",
    "physics_lab_experiment.txt": """
Physics Lab Report - Simple Pendulum

Objective: Determine acceleration due to gravity

Procedure:
1. Measure pendulum length (L = 1.0m)
2. Release from 15° angle
3. Record 10 oscillations time

Results:
Period T = 2.01 seconds
Calculated g = 9.78 m/s²

Error analysis: 0.2% experimental error
""",
    
    # Healthcare Domain (10 files)
    "patient_medical_record.txt": """
Patient Medical Record

Patient ID: MR-2024-001
Name: [REDACTED]
Age: 45 years
Gender: Male

Chief Complaint: Chest pain

Diagnosis: Mild angina
Prescription:
- Aspirin 75mg daily
- Atorvastatin 20mg at night

Follow-up: 2 weeks
""",
    "lab_blood_test_report.txt": """
Pathology Lab Report

Test: Complete Blood Count (CBC)
Date: 30/12/2024

Results:
- Hemoglobin: 14.2 g/dL (Normal: 13-17)
- WBC Count: 7,500/μL (Normal: 4,000-11,000)
- Platelet Count: 250,000/μL (Normal: 150,000-400,000)

Interpretation: All parameters within normal limits
""",
    "discharge_summary_hospital.txt": """
Hospital Discharge Summary

Admission Date: 25/12/2024
Discharge Date: 28/12/2024

Diagnosis: Acute appendicitis
Procedure: Laparoscopic appendectomy

Post-operative Course:
- No complications
- Pain managed with oral analgesics
- Wound healing well

Discharge Medications:
- Paracetamol 500mg as needed
- Antibiotic course 5 days
""",
    "medical_imaging_xray_report.txt": """
X-Ray Imaging Report

Study: Chest X-Ray PA View
Date: 30/12/2024

Findings:
- Both lung fields are clear
- No pleural effusion
- Cardiac silhouette normal size
- No bony abnormality detected

Impression: Normal chest X-ray
""",
    "prescription_medication_list.txt": """
Prescription

Patient: [Name]
Date: 30/12/2024

Medications:
1. Metformin 500mg - 1 tablet twice daily (Diabetes)
2. Amlodipine 5mg - 1 tablet once daily (Hypertension)
3. Vitamin D3 60,000 IU - Weekly once

Duration: 1 month
Next Visit: 30/01/2025
""",
    
    # Finance Domain (10 files)
    "expense_report_december.txt": """
Monthly Expense Report - December 2024

Category Breakdown:
- Salaries: $45,000
- Office Rent: $5,000
- Utilities: $800
- Software Licenses: $2,500
- Marketing: $3,200

Total Expenses: $56,500
Budget: $60,000
Variance: +$3,500 (Under budget)
""",
    "tax_calculation_summary.txt": """
Income Tax Calculation FY 2024-25

Gross Salary: $80,000
Standard Deduction: $12,000
Taxable Income: $68,000

Tax Brackets:
- 10% on first $10,000 = $1,000
- 12% on next $30,000 = $3,600
- 22% on remaining $28,000 = $6,160

Total Tax: $10,760
Effective Rate: 13.45%
""",
    "invoice_client_payment.txt": """
INVOICE

Invoice #: INV-2024-156
Date: 30/12/2024

Client: Acme Corporation

Services:
- Web Development: $5,000
- API Integration: $2,500
- Testing & Deployment: $1,500

Subtotal: $9,000
Tax (18%): $1,620
Total Amount: $10,620

Payment Terms: Net 30 days
""",
    "quarterly_financial_statement.txt": """
Quarterly Financial Statement - Q4 2024

Revenue:
- Product Sales: $250,000
- Services: $80,000
Total Revenue: $330,000

Expenses:
- COGS: $120,000
- Operating Expenses: $95,000
Total Expenses: $215,000

Net Profit: $115,000
Profit Margin: 34.8%
""",
    "budget_allocation_2025.txt": """
Annual Budget Allocation 2025

Total Budget: $500,000

Department Allocation:
- Engineering: $200,000 (40%)
- Sales & Marketing: $150,000 (30%)
- Operations: $100,000 (20%)
- Admin: $50,000 (10%)

Capital Expenditure: $75,000
Contingency Fund: $25,000
""",
    
    # College/School Domain (10 files)
    "student_transcript_official.txt": """
Official Academic Transcript

Student Name: John Doe
Student ID: 2021CS001
Program: B.Tech Computer Science

Semester 1 (Fall 2021):
- Programming in C: A (4.0)
- Mathematics I: A- (3.7)
- Physics: B+ (3.3)
- English: A (4.0)

Semester GPA: 3.75
Cumulative GPA: 3.75
""",
    "bonafide_certificate_college.txt": """
BONAFIDE CERTIFICATE

This is to certify that Mr./Ms. [Student Name] is a bonafide student of our college, studying in Third Year B.Tech Computer Science Engineering during the academic year 2024-2025.

Date of Birth: 15/05/2003
Admission Year: 2021
Current Year: Third Year

Issued for: Internship Application

Principal Signature
Date: 30/12/2024
""",
    "placement_company_offer.txt": """
Job Offer Letter

Company: Tech Solutions Inc.
Position: Software Developer
Candidate: [Student Name]

Salary Package:
- Base Salary: $70,000/year
- Performance Bonus: Up to $5,000
- Health Insurance
- 15 days PTO

Start Date: July 1, 2025
Location: San Francisco, CA

Please respond within 15 days.
""",
    "college_fee_receipt.txt": """
Fee Receipt

Student Name: Jane Smith
Roll Number: 2022ME045
Course: M.Tech Mechanical

Payment Details:
- Tuition Fee: $3,000
- Lab Fee: $500
- Library Fee: $100

Total Paid: $3,600
Payment Mode: Online
Transaction ID: TXN20241230001

Academic Year: 2024-2025 (Semester 2)
""",
    "semester_exam_schedule.txt": """
End Semester Examination Schedule
December 2024

Date | Time | Subject | Room
-----|------|---------|-----
05/01 | 9 AM | Data Structures | Hall A
07/01 | 9 AM | DBMS | Hall B
10/01 | 2 PM | Operating Systems | Hall A
12/01 | 9 AM | Computer Networks | Hall C

Instructions:
- Bring student ID card
- Report 30 minutes early
- No electronic devices allowed
""",
    
    # Company/Business Domain (10 files)
    "employee_handbook_policy.txt": """
Employee Handbook 2025

Work Hours: 9 AM - 6 PM (Monday to Friday)

Leave Policy:
- Casual Leave: 12 days/year
- Sick Leave: 10 days/year
- Annual Leave: 15 days/year

Code of Conduct:
- Professional behavior expected
- Confidentiality agreements mandatory
- No harassment tolerated

Dress Code: Business casual
""",
    "project_proposal_client.txt": """
Project Proposal

Client: GlobalTech Industries
Project: E-commerce Platform Development

Scope:
- Custom shopping cart
- Payment gateway integration
- Admin dashboard
- Mobile responsive design

Timeline: 4 months
Budget: $50,000

Team:
- 2 Backend Developers
- 1 Frontend Developer
- 1 QA Engineer
- 1 Project Manager
""",
    "meeting_minutes_board.txt": """
Board Meeting Minutes
Date: 28/12/2024

Attendees:
- CEO, CFO, CTO, Head of Sales, Head of HR

Agenda:
1. Q4 Performance Review
   - Revenue exceeded target by 15%
   - Customer satisfaction at 92%

2. 2025 Strategy
   - Expand to 3 new markets
   - Launch 2 new products

Action Items:
- CFO to prepare detailed budget
- CTO to finalize tech roadmap
""",
    "performance_appraisal_form.txt": """
Annual Performance Appraisal

Employee: Alex Johnson
Position: Senior Developer
Period: Jan 2024 - Dec 2024

Ratings (1-5):
- Technical Skills: 4.5
- Communication: 4.0
- Leadership: 4.2
- Initiative: 4.5

Overall Rating: Exceeds Expectations

Salary Increment: 12%
Promotion: To Tech Lead

Next Review: December 2025
""",
    "statement_of_work_contract.txt": """
Statement of Work (SOW)

Project: Mobile App Development
Client: FitLife Inc.
Vendor: DevStudio

Deliverables:
1. iOS and Android native apps
2. Backend API
3. Admin panel
4. User documentation

Milestones:
- Design: Week 1-2
- Development: Week 3-10
- Testing: Week 11-12
- Deployment: Week 13

Payment Terms:
- 30% upfront
- 40% at milestone 2
- 30% on completion
""",
    
    # Government/Legal Domain (10 files)
    "rental_lease_agreement.txt": """
RENTAL LEASE AGREEMENT

Landlord: Mr. Robert Smith
Tenant: Ms. Emily Davis

Property Address:
123 Main Street, Apt 4B
Pune, Maharashtra

Terms:
- Monthly Rent: ₹25,000
- Security Deposit: ₹50,000
- Lease Duration: 11 months
- Start Date: 01/01/2025

Utilities: Tenant responsible
Maintenance: Landlord responsible for major repairs

Witnesses:
1. __________________
2. __________________
""",
    "non_disclosure_agreement.txt": """
NON-DISCLOSURE AGREEMENT (NDA)

Between:
Party A: TechCorp Solutions
Party B: InnovateLabs

Effective Date: 30/12/2024

Purpose: Discussion of potential business partnership

Confidential Information includes:
- Business plans
- Financial data
- Technical specifications
- Customer lists

Term: 2 years from signing date

Governing Law: State of California
""",
    "power_of_attorney_legal.txt": """
POWER OF ATTORNEY

I, [Principal Name], hereby appoint [Attorney Name] as my attorney-in-fact to act on my behalf in the following matters:

1. Banking transactions
2. Property management
3. Legal proceedings
4. Tax filings

This power of attorney shall remain in effect until revoked in writing.

Signed: ________________
Date: 30/12/2024

Notarized: ____________
""",
    "income_tax_return_form.txt": """
INCOME TAX RETURN
Assessment Year: 2024-25

PAN: ABCDE1234F
Name: Taxpayer Name

Income Sources:
- Salary: ₹800,000
- Interest on Savings: ₹15,000
Gross Total Income: ₹815,000

Deductions:
- Section 80C: ₹150,000
- Section 80D: ₹25,000

Taxable Income: ₹640,000
Tax Payable: ₹62,400

Tax Paid: ₹65,000
Refund Due: ₹2,600
""",
    "court_summons_notice.txt": """
COURT SUMMONS

Case No: CIV-2024-1156
Court: District Court, Mumbai

Plaintiff: ABC Corporation
Defendant: XYZ Company

Matter: Breach of Contract

Hearing Date: 15/01/2025
Time: 10:30 AM
Courtroom: 5

Defendant must appear in person or through legal counsel.

Failure to appear may result in judgment by default.

Issued By: Court Clerk
Date:30/12/2024
""",
    
    # Personal Domain (5 files)
    "personal_resume_cv.txt": """
CURRICULUM VITAE

Name: Sarah Williams
Email: sarah.w@email.com
Phone: +1-555-0123

Education:
- M.S. Computer Science, MIT (2022)
- B.Tech, IIT Delhi (2020)

Experience:
Software Engineer, Google (2022-Present)
- Developed cloud infrastructure tools
- Led team of 5 engineers

Skills:
Python, Java, Kubernetes, AWS, Machine Learning

Publications:
- "Efficient Data Processing" (ICML 2023)
""",
    "electricity_bill_statement.txt": """
Electricity Bill

Account Number: 1234567890
Billing Period: Nov 2024

Meter Reading:
Previous: 15,240 kWh
Current: 15,540 kWh
Consumption: 300 kWh

Charges:
- Energy Charges: ₹1,800
- Fixed Charges: ₹200
- Tax: ₹360

Total Amount: ₹2,360
Due Date: 10/01/2025

Payment Methods: Online, Bank, Cash
""",
    "insurance_policy_health.txt": """
Health Insurance Policy

Policy Number: HI-2024-9876
Policyholder: John Anderson

Coverage:
- Sum Insured: $100,000
- Hospitalization: Covered
- Pre-existing: Covered after 2 years
- Maternity: Covered

Premium: $1,200/year
Policy Period: 01/01/2024 - 31/12/2024

Cashless Hospitals: 5,000+ network hospitals
Claim Process: Online portal or toll-free number
""",
    "bank_statement_savings.txt": """
Bank Statement
Account: Savings Account

Account Holder: Emily Johnson
Account Number: 001234567890
Period: December 2024

Opening Balance: $5,240.00

Transactions:
05/12 - Salary Credit: +$4,500.00
10/12 - Rent Payment: -$1,200.00
15/12 - Grocery: -$250.00
20/12 - Online Shopping: -$180.00

Closing Balance: $8,110.00

Interest Earned: $12.50
""",
    "credit_card_statement.txt": """
Credit Card Statement

Cardholder: Michael Brown
Card Number: **** **** **** 1234
Statement Date: 30/12/2024

Transactions:
15/12 - Amazon: $85.00
18/12 - Gas Station: $45.00
22/12 - Restaurant: $62.00
27/12 - Supermarket: $120.00

Total Amount Due: $312.00
Minimum Payment: $31.20
Due Date: 15/01/2025

Credit Limit: $5,000
Available Credit: $4,688
""",
}

# Generate 100 files (use templates multiple times with variations)
file_count = 0
for i in range(100):
    # Cycle through templates
    template_names = list(test_files.keys())
    template_name = template_names[i % len(template_names)]
    content = test_files[template_name]
    
    # Create unique filename
    base_name = template_name.rsplit('.', 1)[0]
    ext = template_name.rsplit('.', 1)[1] if '.' in template_name else 'txt'
    filename = f"{base_name}_{i+1:03d}.{ext}"
    
    # Write file
    filepath = incoming_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    file_count += 1
    if file_count % 20 == 0:
        print(f"Created {file_count}/100 files...")

print(f"\n[SUCCESS] Created {file_count} test files in {incoming_dir}")
print("Files cover domains: Technology, Code, Education, Healthcare, Finance, College, Company, Government, Personal")
