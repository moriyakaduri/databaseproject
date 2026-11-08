-- Method 3: actual CSV import using psql. Run with this folder as working directory.
BEGIN;
\copy labtechnician(technicianid,firstname,lastname,certificationnumber,phone) FROM 'technicians.csv' WITH (FORMAT csv, HEADER true)
SELECT setval(pg_get_serial_sequence('labtechnician','technicianid'),(SELECT max(technicianid) FROM labtechnician));
COMMIT;
