-- PostgreSQL / pgAdmin: הרצה על עותק ההדגמה בלבד.
-- נבחרת הזמנה קיימת; טבלה זמנית שומרת מצב קודם ומשמשת להוכחה מדויקת.
CREATE TEMP TABLE transaction_demo AS
SELECT orderid,notes AS old_notes FROM testorder ORDER BY orderid LIMIT 1;
SELECT 'before rollback' AS phase,o.orderid,o.notes FROM testorder o JOIN transaction_demo t USING(orderid);
BEGIN;
UPDATE testorder SET notes=COALESCE(notes,'')||' [ROLLBACK DEMO]'
WHERE orderid=(SELECT orderid FROM transaction_demo);
SELECT 'inside rollback' AS phase,o.orderid,o.notes FROM testorder o JOIN transaction_demo t USING(orderid);
ROLLBACK;
SELECT 'after rollback' AS phase,o.orderid,o.notes,
       o.notes IS NOT DISTINCT FROM t.old_notes AS restored
FROM testorder o JOIN transaction_demo t USING(orderid);

SELECT 'before commit' AS phase,o.orderid,o.notes FROM testorder o JOIN transaction_demo t USING(orderid);
BEGIN;
UPDATE testorder SET notes=COALESCE(notes,'')||' [COMMIT DEMO]'
WHERE orderid=(SELECT orderid FROM transaction_demo);
SELECT 'inside commit' AS phase,o.orderid,o.notes FROM testorder o JOIN transaction_demo t USING(orderid);
COMMIT;
SELECT 'after commit' AS phase,o.orderid,o.notes,
       o.notes IS NOT DISTINCT FROM COALESCE(t.old_notes,'')||' [COMMIT DEMO]' AS persisted
FROM testorder o JOIN transaction_demo t USING(orderid);
-- השינוי האחרון נשאר בכוונה לצורך הוכחת COMMIT.
DROP TABLE transaction_demo;
