-- psql master script. EMPTY database only. Run from the Stage A directory.
-- All three methods were actually executed separately on the main DB.
\set ON_ERROR_STOP on
\ir SQLInsert/baseSeed.sql
\ir SQLInsert/extendCatalog.sql
\cd DataImportFiles
\ir import.sql
\cd ..
\ir Programing/generated.sql
\ir audit/validate.sql
