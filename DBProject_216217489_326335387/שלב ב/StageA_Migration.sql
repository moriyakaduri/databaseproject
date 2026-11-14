-- להרצה חד־פעמית על עותק קיים של שלב א׳; בבסיס ריק משתמשים ב-createTables.sql המעודכן.
-- אלה נתוני הדגמה סינתטיים בלבד; במערכת אמיתית טוענים תאריכים ממקור מוסמך.
BEGIN;
ALTER TABLE labtechnician ADD COLUMN certificationexpireson DATE;
UPDATE labtechnician
SET certificationexpireson = DATE '2026-01-01' + (365 + technicianid % 730);
ALTER TABLE labtechnician ALTER COLUMN certificationexpireson SET NOT NULL;
COMMIT;
