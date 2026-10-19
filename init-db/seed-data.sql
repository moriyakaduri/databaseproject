-- הכנסת מחלקות
INSERT INTO Ward (WardName, WardType, Floor, Capacity, Phone) VALUES
('פנימית א', 'פנימית', 2, 30, '02-5551111'),
('ילדים ב', 'ילדים', 3, 20, '02-5552222'),
('מיון כללי', 'מיון', 1, 15, '02-5553333');

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
('תפקודי כבד (ALT/AST)', 'ביוכימיה', '7 - 56'),
('תרבית שתן', 'מיקרוביולוגיה', 'Negative');

-- הכנסת הזמנת בדיקה
INSERT INTO TestOrder (PatientID, DoctorID, WardID, TestID) VALUES
(1, 1, 1, 1),
(2, 2, 2, 3);