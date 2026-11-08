
-- הכנסת רופאים
INSERT INTO Doctor (LicenseNumber, FirstName, LastName, Specialty, Phone, Email) VALUES
('LIC1001', 'דוד', 'כהן', 'המטולוגיה', '050-1234567', 'david.c@hospital.org'),
('LIC1002', 'שרה', 'לוי', 'מיקרוביולוגיה', '052-7654321', 'sara.l@hospital.org');

-- הכנסת מטופלים
INSERT INTO Patient (IDNumber, FirstName, LastName, DateOfBirth, Gender, Phone, Address) VALUES
('123456789', 'ישראל', 'ישראלי', '1985-05-12', 'M', '054-1112233', 'ירושלים'),
('987654321', 'רחל', 'אברהם', '1992-10-20', 'F', '053-4445566', 'תל אביב');

-- הכנסת בדיקות מעבדה
INSERT INTO LabTest (TestName, Category, NormalRange) VALUES
('ספירת דם מלאה (CBC)', 'המטולוגיה', '4.5 - 11.0'),
('תרבית שתן', 'מיקרוביולוגיה', 'Negative');

-- הכנסת טכנאי מעבדה
INSERT INTO LabTechnician (FirstName, LastName, CertificationNumber, Phone) VALUES
('רון', 'לוי', 'CERT801', '052-1111111'),
('מיכל', 'שפירא', 'CERT802', '052-2222222');

-- הכנסת הזמנות בדיקה
INSERT INTO TestOrder (PatientID, DoctorID, WardID, TestID, Priority, Status) VALUES
(1, 1, 1, 1, 'Normal', 'Completed'),
(2, 2, 2, 2, 'Urgent', 'Completed');

-- הכנסת תוצאות בדיקה
-- תוצאה 1: תקינה
INSERT INTO TestResult (OrderID, TechnicianID, ResultValue, Interpretation, Comments) VALUES
(1, 1, '4.8 (תקין)', 'Normal', 'בדיקה שגרתית תקינה');
-- תוצאה 2: קריטית! (תייצר התראה)
INSERT INTO TestResult (OrderID, TechnicianID, ResultValue, Interpretation, Comments) VALUES
(2, 2, 'חיובי - חיידק E.coli', 'Critical', 'דורש טיפול אנטיביוטי מיידי!');

-- הכנסת התראה רפואית אך ורק עבור התוצאה הקריטית (ResultID = 2)
INSERT INTO LabAlert (ResultID, AlertStatus) VALUES
(2, 'New');