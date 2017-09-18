/* Lab 1, Task 3 SQL Solutions
 * DD 1334 Database Technologies - Fall 2017
 * Written by Sabrina Backstrom, Ryan D'souza
*/


-- Get rid of old triggers/functions
DROP TRIGGER IF EXISTS OrderValidatorTrigger ON shipments;
DROP FUNCTION IF EXISTS OrderValidatorFunction();

/* Throws exception if there is no stock to ship
 * If there is stock, reduces the stock by 1
*/
CREATE FUNCTION OrderValidatorFunction()
  RETURNS TRIGGER AS $OrderValidatorFunction$

  DECLARE 
    stock_count integer;

  BEGIN

    stock_count = (SELECT stock.stock 
                      FROM stock 
                    WHERE stock.isbn = NEW.isbn);

    IF stock_count IS NULL THEN
      RAISE EXCEPTION 'There is no stock to ship';
    END IF;

    IF stock_count <= 0 THEN
      RAISE EXCEPTION 'There is no stock to ship';

    ELSE
      UPDATE stock
          SET stock = stock_count - 1
        WHERE stock.isbn = NEW.isbn;

    END IF;

    RETURN NEW;

  END;
$OrderValidatorFunction$ LANGUAGE plpgsql;

/* Before an order is inserted, validates the order.
 * Raises an exception if there is no stock */
CREATE TRIGGER OrderValidatorTrigger 
  BEFORE INSERT
  ON shipments

  FOR EACH ROW
    EXECUTE PROCEDURE OrderValidatorFunction();


/* For testing and demonstration purposes */

\echo 'Original database'
SELECT *
  FROM stock;


\echo '\n\nShould be error INSERTing as there is no stock with this ISBN'
INSERT INTO shipments
  VALUES(2000, 860, '0394900014', '2012-12-07');


\echo '\n\nShould have inserted'
INSERT INTO shipments
  VALUES(2001, 860, '044100590X', '2012-12-07');


\echo '\n\n Show that only the second row was inserted'
SELECT * FROM shipments WHERE shipment_id > 1999;


\echo '\n\nShould 044100590X decremented'
SELECT * FROM stock;


\echo '\n\nRestoring database'
DELETE FROM shipments WHERE shipment_id > 1999;

UPDATE stock SET stock = 89 WHERE isbn = '044100590X';

DROP TRIGGER IF EXISTS OrderValidatorTrigger ON shipments;
DROP FUNCTION IF EXISTS OrderValidatorFunction();
