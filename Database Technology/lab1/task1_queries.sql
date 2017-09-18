/* Lab 1, Task 1 SQL Solutions
 * DD 1334 Database Technologies - Fall 2017
 * Written by Sabrina Backstrom, Ryan D'souza
*/



/* Question 1: Who wrote "The Shining"? */
\echo 'Question 1'

SELECT author.last_name, author.first_name 
    FROM authors AS author
  WHERE author.author_id = (SELECT book.author_id 
                                FROM books AS book 
                              WHERE book.title = 'The Shining');



/* Question 2: Which titles are written by Paulette Bourgeois? */
\echo '\n\n Question 2'

SELECT book.title
	  FROM books AS book
  WHERE book.author_id IN (SELECT author.author_id
                              FROM authors AS author
                            WHERE author.first_name = 'Paulette'
                              AND author.last_name = 'Bourgeois');



/* Question 3: Who bought books about "Horror" */
\echo '\n\n Question 3'

SELECT customer.last_name, customer.first_name
    FROM customers AS customer
  INNER JOIN shipments AS shipment
    ON customer.customer_id = shipment.customer_id
  INNER JOIN editions AS edition
    ON shipment.isbn = edition.isbn
  INNER JOIN books AS book
    ON edition.book_id = book.book_id
  INNER JOIN subjects AS subject
    ON book.subject_id = subject.subject_id
      WHERE subject.subject = 'Horror';



/* Question 4: Which book has the largest stock? */
\echo '\n\n Question 4'

SELECT book.title
    FROM books AS book
  INNER JOIN editions AS edition
    ON book.book_id = edition.book_id
  INNER JOIN stock AS stock
    ON edition.isbn = stock.isbn
  INNER JOIN (SELECT MAX(stock.stock) AS stock_count 
                  FROM stock AS stock) AS largest_stock
    ON stock.stock = largest_stock.stock_count;



/* Question 5: How much money has Booktown collected for the books about Science Fiction? */
\echo '\n\n Question 5'

SELECT SUM(stock.retail_price)
    FROM stock AS stock
  INNER JOIN shipments AS shipment
    ON stock.isbn = shipment.isbn
  INNER JOIN editions AS edition
    ON stock.isbn = edition.isbn
  INNER JOIN books AS book
    ON edition.book_id = book.book_id
  INNER JOIN subjects AS subject
    ON book.subject_id = subject.subject_id
        WHERE subject.subject = 'Science Fiction';


/* Question 6: Which books have been sold to only two people? */
\echo '\n\n Question 6'

SELECT book.title 
    FROM shipments AS shipment 
  INNER JOIN editions AS edition 
    ON shipment.isbn = edition.isbn 
  INNER JOIN books AS book 
    ON edition.book_id = book.book_id 
  INNER JOIN customers AS customer 
    ON shipment.customer_id = customer.customer_id 
  GROUP BY book.book_id 
    HAVING COUNT(book.book_id) = 2;



/* Question 7: Which publisher has sold the most to Booktown? */
\echo '\n\n Question 7'

WITH 
    -- Information about the top publisher -- 
    top_publisher AS (SELECT publisher.publisher_id AS publisher_id, 
                                publisher.name AS name, 
																SUM(stock.stock * stock.cost) AS total_stock_cost 
                          FROM stock AS stock
                        INNER JOIN editions AS edition 
													ON stock.isbn = edition.isbn 
												INNER JOIN publishers AS publisher
														ON edition.publisher_id = publisher.publisher_id
													    GROUP BY publisher.publisher_id, publisher.name
															ORDER BY total_stock_cost 
															DESC LIMIT 1),

		-- The sum of all the books that have been sold at cost value per publisher_id --
    publisher_sales AS (SELECT publisher.publisher_id AS publisher_id, 
                                  SUM(stock.cost) AS sales
														FROM stock AS stock
													INNER JOIN shipments AS shipment
														ON stock.isbn = shipment.isbn
													INNER JOIN editions AS edition
														ON stock.isbn = edition.isbn
													INNER JOIN publishers AS publisher
														ON edition.publisher_id = publisher.publisher_id
													INNER JOIN books AS book
														ON edition.book_id = book.book_id
													INNER JOIN subjects AS subject
														ON book.subject_id = subject.subject_id
															GROUP BY publisher.publisher_id)

-- Returns the top publisher and their sales -- 
SELECT top_publisher.name, top_publisher.total_stock_cost + publisher_sales.sales 
		FROM top_publisher AS top_publisher, publisher_sales AS publisher_sales 
	WHERE publisher_sales.publisher_id = top_publisher.publisher_id;



/* Question 8: How much money has Booktown earned (so far)? */
\echo '\n\n Question 8'

WITH
    -- Total cost of purchases --
    purchase AS (SELECT SUM(stock.stock * stock.cost) AS purchase_price 
                      FROM stock AS stock 
                    INNER JOIN editions AS edition 
                      ON stock.isbn = edition.isbn),
                      
    -- Total profits from book sales --
    sales AS (SELECT SUM(stock.retail_price - stock.cost) AS amount_sold 
                  FROM stock AS stock 
                INNER JOIN shipments AS shipment 
                  ON stock.isbn = shipment.isbn) 
                
-- Actual query to return net earnings -- 
SELECT ((-1 * purchase.purchase_price) + sales.amount_sold) as net_earnings
    FROM purchase AS purchase, sales AS sales;



/* Question 9: Which customers have bought books about at least three different subjects? */
\echo '\n\n Question 9'

SELECT customer.last_name, customer.first_name 
    FROM customers AS customer 
  INNER JOIN shipments AS shipment 
    ON customer.customer_id = shipment.customer_id 
  INNER JOIN editions AS edition 
    ON shipment.isbn = edition.isbn 
  INNER JOIN books AS book 
    ON edition.book_id = book.book_id 
  INNER JOIN subjects AS subject 
    ON book.subject_id = subject.subject_id 
      GROUP BY customer.last_name, customer.first_name 
      HAVING COUNT(DISTINCT(subject.subject_id)) >= 3;



/* Question 10: Which subjects have not sold any books? */
\echo '\n\n Question 10'

SELECT subject.subject 
    FROM subjects AS subject 
  WHERE subject.subject_id NOT IN (SELECT subject.subject_id -- All subjects that have books sold
                                      FROM subjects AS subject 
                                    INNER JOIN books AS book 
                                      ON subject.subject_id = book.subject_id 
                                    INNER JOIN editions AS edition 
                                      ON book.book_id = edition.book_id 
                                    INNER JOIN shipments AS shipment 
                                      ON edition.isbn = shipment.isbn);

