<img width="1578" height="718" alt="WhatsApp Image 2026-10-19 at 17 10 59" src="https://github.com/user-attachments/assets/5f1c4f2b-43d1-4498-aaf4-a54caeb25f7d" />
<img width="1543" height="716" alt="WhatsApp Image 2026-10-19 at 17 10 21" src="https://github.com/user-attachments/assets/b10ee0ef-b85a-4a76-beb5-18b12fa48901" />
<img width="1579" height="719" alt="WhatsApp Image 2026-10-19 at 17 09 44" src="https://github.com/user-attachments/assets/ad962298-7600-45de-b31c-e50fb699db55" />
<img width="1557" height="726" alt="WhatsApp Image 2026-10-19 at 17 09 15" src="https://github.com/user-attachments/assets/61de110f-bb7d-44bb-a535-61dacb0c9802" />
<img width="1558" height="743" alt="WhatsApp Image 2026-10-19 at 17 08 46" src="https://github.com/user-attachments/assets/52148a86-5331-4c2e-a33c-21ef9177800c" />
<img width="1432" height="649" alt="WhatsApp Image 2026-10-19 at 17 07 07" src="https://github.com/user-attachments/assets/eedea562-362f-4e70-80ed-6b5907600ed2" />
<img width="1600" height="650" alt="WhatsApp Image 2026-10-19 at 17 05 19" src="https://github.com/user-attachments/assets/80ae227b-8eb0-4964-a3fc-7db86342eb16" />
<img width="847" height="600" alt="צילום מסך 2026-10-20 212110" src="https://github.com/user-attachments/assets/b7e4a881-88c0-460e-83bc-d25c6ff2fb83" />
<img width="1600" height="656" alt="WhatsApp Image 2026-10-19 at 17 12 18" src="https://github.com/user-attachments/assets/ba6c2ff9-5ce0-483c-abf5-323d16749168" />
<img width="1580" height="740" alt="WhatsApp Image 2026-10-19 at 17 11 35" src="https://github.com/user-attachments/assets/772a8b34-198c-4699-af36-06a91a6a58ae" />
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
