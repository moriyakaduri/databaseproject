
Hospital Laboratory Information System - Database Design


1. Project Overview

This project focuses on the database design for a Hospital Laboratory Management System. The system is responsible for tracking the entire lifecycle of a lab test within a hospital setting—from the moment a doctor orders a test for a patient, through the lab technician's analysis, to the final result and automated critical alerts.
The primary goals of this system are to maintain accurate medical records, ensure secure and normalized data storage (minimizing redundancy), and provide real-time updates for critical medical events to ensure patient safety.

2. Entity-Relationship Diagram (ERD)

The database structure is visualized in the ERD diagram. The schema is fully normalized (3NF), ensuring data integrity and consisting of 7 primary entities connected to eliminate redundant data.
<img width="847" height="600" alt="צילום מסך 2026-10-20 212110" src="https://github.com/user-attachments/assets/b7e4a881-88c0-460e-83bc-d25c6ff2fb83" />

3. Entities and Attributes Description

The database is structured around two hospital-wide entities (Patient, Doctor) and five laboratory-specific entities:
• Patient: Represents individuals receiving medical care at the hospital.
	• Attributes: PatientID (Primary Key), IDNumber (ID Number - Unique), FirstName (First Name), LastName (Last Name), DateOfBirth (Date of Birth), Gender (Gender), Phone (Phone), Address (Address).
• Doctor: Represents the hospital's medical staff who order the laboratory tests.
	• Attributes: DoctorID (Primary Key), LicenseNumber (License Number - Unique), FirstName (First Name), LastName (Last Name), Specialty (Specialty), Phone (Phone), Email (Email).
• LabTest (Lab Test): The catalog of all standard tests the laboratory is authorized to perform (e.g., Complete Blood Count, Glucose).
	• Attributes: TestID (Primary Key), TestName (Test Name), TestCategory (Test Category), Description (Description), MeasurementUnit (Measurement Unit), ReferenceRange (Reference Range), EstimatedDuration (Estimated Duration).
• TestOrder (Test Order): A specific request made by a doctor for a patient to undergo a particular lab test.
	• Attributes: OrderID (Primary Key), PatientID (Foreign Key), DoctorID (Foreign Key), TestID (Foreign Key), OrderDate (Order Date), Priority (Priority), Status (Status), OrderNotes (Order Notes).
• TestResult (Test Result): The clinical findings entered by the laboratory staff after analyzing the sample.
	• Attributes: ResultID (Primary Key), OrderID (Foreign Key - Unique), TechnicianID (Foreign Key), ResultValue (Result Value), ResultDate (Result Date), Interpretation (Interpretation), Comments (Comments).
• LabTechnician (Lab Technician): The certified laboratory personnel authorized to perform tests and log results.
	• Attributes: TechnicianID (Primary Key), FirstName (First Name), LastName (Last Name), CertificationNumber (Certification Number - Unique), Phone (Phone), Email (Email), HireDate (Hire Date).
• LabAlert (Lab Alert): An automated notification generated strictly for test results deemed critical.
	• Attributes: AlertID (Primary Key), ResultID (Foreign Key - Unique), AlertDate (Alert Date), AlertStatus (Alert Status).

4. Relationships and Business Logic

The connections between the entities dictate the system's core business logic:
• Patient (1) ────< (N) TestOrder: A single patient can have multiple test orders recorded over time, but every test order must belong to one specific patient.
• Doctor (1) ────< (N) TestOrder: A doctor can issue multiple test orders for various patients, but each specific order is linked to exactly one prescribing doctor.
• LabTest (1) ────< (N) TestOrder: A single type of test from the catalog can be ordered many times, but each test order refers to only one specific test type.
• TestOrder (1) ──── (0..1) TestResult: A test order can have a maximum of one resulting record (ensured by a UNIQUE constraint on the OrderID field).
• LabTechnician (1) ────< (N) TestResult: A lab technician can process and record many test results, but each specific result is signed off by only one technician.
• TestResult (1) ──── (0..1) LabAlert: A test result triggers an alert only if the clinical interpretation is 'Critical'. Normal or non-critical abnormal results do not generate an alert.

5. Relational Navigation and Data Integrity

By adhering to 3NF, the system avoids storing repetitive data. For instance, when displaying a "Medical Alert," the system does not store the patient's name or the doctor's phone number directly within the LabAlert table. Instead, the application navigates through the foreign keys (LabAlert → TestResult → TestOrder → Patient/Doctor) to retrieve accurate, up-to-date information, ensuring absolute data integrity.

User Interface (UI) - Screens Specification

As part of the Top-Down design phase, the main screens of the system were defined and designed using Google AI Studio. These screens reflect the data flow and the required functionality for managing the hospital laboratory.

🔗 View the Interactive Prototype (Google AI Studio)
https://ai.studio/apps/df3f878f-ea06-4229-aff1-0bdbfb6184f0

1. Main Dashboard

The lab manager's home screen, centralizing all key data at a glance.
• What you see: Current status of all lab tests (pending, in progress, completed), breakdown by test categories, active critical alerts tracking, and charts showing testing loads.

2. Reports & Analytics

A management screen designed to analyze laboratory efficiency.
• What you see: Distribution of tests by status and priority (Urgent/Normal), most frequently requested test types, individual performance metrics for lab technicians, and alert resolution tracking.

3. Critical Medical Alerts

A dedicated screen that aggregates all test results significantly deviating from the normal reference range.
• What you see: A dynamic list of alerts. Each entry displays the patient's name, ordering doctor, test type, and the critical measured value.

4. Patients Management

The interface for managing patient records within the laboratory context.
• What you see: A patient registry including ID Number (Unique), full name, age, gender, and contact details.

5. Doctors Management

A registry of the medical staff authorized to order laboratory tests.
• What you see: Doctor details including License Number (Unique), full name, medical specialty, and contact information.

6. Lab Tests Catalog

The laboratory's operational catalog, defining all available diagnostic tests.
• What you see: Test names, associated categories, required measurement units, and standard reference ranges.

7. Test Orders Management

The primary workspace for tracking incoming test requisitions from doctors.
• What you see: Complete documentation of every request, including Order ID, order date, patient info, and status.

8. Test Results Management

The data entry interface designated for certified lab technicians.
• What you see: The interface for entering actual quantitative result values and automated clinical interpretations.



<img width="1578" height="718" alt="WhatsApp Image 2026-10-19 at 17 10 59" src="https://github.com/user-attachments/assets/5f1c4f2b-43d1-4498-aaf4-a54caeb25f7d" />
<img width="1543" height="716" alt="WhatsApp Image 2026-10-19 at 17 10 21" src="https://github.com/user-attachments/assets/b10ee0ef-b85a-4a76-beb5-18b12fa48901" />
<img width="1579" height="719" alt="WhatsApp Image 2026-10-19 at 17 09 44" src="https://github.com/user-attachments/assets/ad962298-7600-45de-b31c-e50fb699db55" />
<img width="1557" height="726" alt="WhatsApp Image 2026-10-19 at 17 09 15" src="https://github.com/user-attachments/assets/61de110f-bb7d-44bb-a535-61dacb0c9802" />
<img width="1558" height="743" alt="WhatsApp Image 2026-10-19 at 17 08 46" src="https://github.com/user-attachments/assets/52148a86-5331-4c2e-a33c-21ef9177800c" />
<img width="1432" height="649" alt="WhatsApp Image 2026-10-19 at 17 07 07" src="https://github.com/user-attachments/assets/eedea562-362f-4e70-80ed-6b5907600ed2" />
<img width="1600" height="650" alt="WhatsApp Image 2026-10-19 at 17 05 19" src="https://github.com/user-attachments/assets/80ae227b-8eb0-4964-a3fc-7db86342eb16" />

<img width="1600" height="656" alt="WhatsApp Image 2026-10-19 at 17 12 18" src="https://github.com/user-attachments/assets/ba6c2ff9-5ce0-483c-abf5-323d16749168" />
<img width="1580" height="740" alt="WhatsApp Image 2026-10-19 at 17 11 35" src="https://github.com/user-attachments/assets/772a8b34-198c-4699-af36-06a91a6a58ae" />