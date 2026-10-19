-- ישות משותפת 1: מטופל (Patient)
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

-- ישות משותפת 2: רופא (Doctor)
CREATE TABLE IF NOT EXISTS Doctor (
    DoctorID SERIAL PRIMARY KEY,
    LicenseNumber VARCHAR(20) NOT NULL UNIQUE,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Specialty VARCHAR(60) NOT NULL,
    Phone VARCHAR(15),
    Email VARCHAR(100)
);

-- ישות משותפת 3: מחלקה (Ward)
CREATE TABLE IF NOT EXISTS Ward (
    WardID SERIAL PRIMARY KEY,
    WardName VARCHAR(80) NOT NULL,
    WardType VARCHAR(50) NOT NULL,
    Floor SMALLINT NOT NULL,
    Capacity SMALLINT NOT NULL,
    Phone VARCHAR(15)
);

-- טבלת בדיקות מעבדה (LabTest)
CREATE TABLE IF NOT EXISTS LabTest (
    TestID SERIAL PRIMARY KEY,
    TestName VARCHAR(100) NOT NULL,
    Category VARCHAR(50) NOT NULL,
    NormalRange VARCHAR(50)
);

-- טבלת הזמנות בדיקה (TestOrder) - מחברת בין המטופל, הרופא, המחלקה והבדיקה
CREATE TABLE IF NOT EXISTS TestOrder (
    OrderID SERIAL PRIMARY KEY,
    PatientID INT REFERENCES Patient(PatientID) ON DELETE CASCADE,
    DoctorID INT REFERENCES Doctor(DoctorID) ON DELETE CASCADE,
    WardID INT REFERENCES Ward(WardID) ON DELETE CASCADE,
    TestID INT REFERENCES LabTest(TestID) ON DELETE CASCADE,
    OrderDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);