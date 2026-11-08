-- 1: מטופל (Patient)
CREATE TABLE IF NOT EXISTS Patient (
    PatientID SERIAL PRIMARY KEY,
    IDNumber VARCHAR(9) NOT NULL UNIQUE,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    DateOfBirth DATE NOT NULL,
    Gender VARCHAR(10) CHECK (Gender IN ('M', 'F', 'other')),
    Phone VARCHAR(15),
    Address VARCHAR(150)
);

-- 2: רופא (Doctor)
CREATE TABLE IF NOT EXISTS Doctor (
    DoctorID SERIAL PRIMARY KEY,
    LicenseNumber VARCHAR(20) NOT NULL UNIQUE,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Specialty VARCHAR(60) NOT NULL,
    Phone VARCHAR(15),
    Email VARCHAR(100)
);


-- 3: קטלוג בדיקות מעבדה (LabTest)
CREATE TABLE IF NOT EXISTS LabTest (
    TestID SERIAL PRIMARY KEY,
    TestName VARCHAR(100) NOT NULL,
    Category VARCHAR(50) NOT NULL,
    NormalRange VARCHAR(50)
);

-- 4: טכנאי מעבדה (LabTechnician)
CREATE TABLE IF NOT EXISTS LabTechnician (
    TechnicianID SERIAL PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    CertificationNumber VARCHAR(30) UNIQUE NOT NULL,
    Phone VARCHAR(15)
);

-- 5: הזמנת בדיקה (TestOrder)
CREATE TABLE IF NOT EXISTS TestOrder (
    OrderID SERIAL PRIMARY KEY,
    PatientID INT REFERENCES Patient(PatientID) ON DELETE CASCADE,
    DoctorID INT REFERENCES Doctor(DoctorID) ON DELETE CASCADE,
    WardID INT REFERENCES Ward(WardID) ON DELETE CASCADE,
    TestID INT REFERENCES LabTest(TestID) ON DELETE CASCADE,
    OrderDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Priority VARCHAR(20) DEFAULT 'Normal',
    Status VARCHAR(30) DEFAULT 'Pending'
);

-- 6: תוצאת בדיקה (TestResult)
CREATE TABLE IF NOT EXISTS TestResult (
    ResultID SERIAL PRIMARY KEY,
    OrderID INT UNIQUE REFERENCES TestOrder(OrderID) ON DELETE CASCADE,
    TechnicianID INT REFERENCES LabTechnician(TechnicianID) ON DELETE SET NULL,
    ResultValue VARCHAR(100) NOT NULL,
    ResultDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Interpretation VARCHAR(30) CHECK (Interpretation IN ('Normal', 'Abnormal', 'Critical')),
    Comments VARCHAR(250)
);

-- 7: התראה רפואית (LabAlert)
CREATE TABLE IF NOT EXISTS LabAlert (
    AlertID SERIAL PRIMARY KEY,
    ResultID INT UNIQUE REFERENCES TestResult(ResultID) ON DELETE CASCADE,
    AlertDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    AlertStatus VARCHAR(20) CHECK (AlertStatus IN ('New', 'Viewed', 'Handled')) DEFAULT 'New'
);