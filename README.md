User Interface (UI) - Screens Specification
As part of the Top-Down design phase, the main screens of the system were defined and designed using Google AI Studio. These screens reflect the data flow and the required functionality for managing the hospital laboratory, serving as the foundation for deriving the database entities and fields.

🔗 View the Interactive Prototype (Google AI Studio)
https://ai.studio/apps/df3f878f-ea06-4229-aff1-0bdbfb6184f0

Below is a detailed description of the main system screens:

1. Main Dashboard
The lab manager's home screen, centralizing all key data at a glance.

What you see: Current status of all lab tests (pending, in progress, completed), breakdown by test categories, active critical alerts tracking, and charts showing testing loads.

2. Reports & Analytics
A management screen designed to analyze laboratory efficiency.

What you see: Distribution of tests by status and priority (Urgent/Normal), most frequently requested test types, individual performance metrics for lab technicians, and alert resolution tracking.

3. Critical Medical Alerts
A dedicated screen that aggregates all test results significantly deviating from the normal reference range.

What you see: A dynamic list of alerts. Each entry displays the patient's name, ordering doctor, test type, and the critical measured value (e.g., severe hypoglycemia).

4. Patients Management
The interface for managing patient records within the laboratory context.

What you see: A patient registry including ID Number (Unique), full name, age, gender, and contact details. This screen also provides access to each patient's complete laboratory testing history.

5. Doctors Management
A registry of the medical staff authorized to order laboratory tests.

What you see: Doctor details including License Number (Unique), full name, medical specialty, and contact information. It also presents aggregated data such as total tests ordered and open alerts associated with each doctor.

6. Lab Tests Catalog
The laboratory's operational catalog, defining all available diagnostic tests.

What you see: Test names (e.g., CBC, Glucose Fasting), associated categories (Hematology, Biochemistry), required measurement units, standard reference ranges for healthy individuals, and estimated processing durations.

7. Test Orders Management
The primary workspace for tracking incoming test requisitions from doctors.

What you see: Complete documentation of every request, including Order ID, order date, patient information, ordering physician, and the requested test type. Priority levels (Normal/Urgent) and current processing statuses are managed here.

8. Test Results Management
The data entry interface designated for certified lab technicians.

What you see: The interface for entering actual quantitative result values for completed test orders. The system automatically compares the entered value against the catalog's reference range to generate a clinical interpretation (Normal, Abnormal, or Critical). The screen records the identity of the technician signing off on the result.