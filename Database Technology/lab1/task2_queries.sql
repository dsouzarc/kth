/* Lab 1, Task 2 SQL Solutions
 * DD 1334 Database Technologies - Fall 2017
 * Written by Sabrina Backstrom, Ryan D'souza
*/



/* Question 1: Create a view that contains isbn and title of all the books in the database. 
 *    Then query it to list all the titles and isbns. 
 *    Then delete (drop) the new view. Why might this view be nice to have?
*/
\echo 'Question 1'

CREATE VIEW Library AS (SELECT title, isbn 
                            FROM books, editions
                          WHERE books.book_id = editions.book_id);

SELECT title, isbn
    FROM Library;

DROP VIEW Library;

\echo 'This view would be nice to have as a quick way of getting: '
\echo 'a book title based on its ISBN, or an ISBN based on its title'



/* Question 2: Try to insert into editions a new tuple ('5555', 12345, 1, 59, '2012-12-02'). 
 *    Explain what happened
*/
\echo '\n\n Question 2'

INSERT INTO editions 
    VALUES ('5555', 12345, 1, 59, '2012-12-02');

\echo 'The INSERT fails because the `editions` table has a FOREIGN KEY requirement '
\echo 'based on `book_id` in the `books` table that stops us from inserting a book '
\echo 'into `editions` if that `book_id` is not already present in the `books` table'


/* Question 3: Try to insert into editions a new tuple only setting its isbn='5555'. 
 *    Explain what happened.
*/
\echo '\n\n Question 3'

INSERT INTO editions(isbn)
    VALUES ('5555');

\echo 'The INSERT fails because the `editions` table has constraints that prohibit '
\echo 'certain attributes from being null, and that insert results in everything except for '
\echo 'isbn being null'



/* Question 4: Try to first insert a book with (book_id, title) of (12345, 'How I Insert') then
 *    One into editions as in 2. 
 *    Show that this worked by making an appropriate query of the database. 
 *    Why do we not need an author or subject?
*/
\echo '\n\n Question 4'

INSERT INTO books(book_id, title)
    VALUES (12345, 'How I Insert');

INSERT INTO editions
    VALUES ('5555', 12345, 1, 59, '2012-12-02');

SELECT books.book_id, books.title, editions.isbn, editions.book_id, 
          editions.edition, editions.publisher_id, editions.publication_date
    FROM books, editions
  WHERE books.book_id = 12345 AND editions.book_id = 12345;

\echo 'We do not need an author or a subject during our insert because there is no CONSTRAINT'



/* Question 5: Update the new book by setting the subject to 'Mystery' */
\echo '\n\n Question 5'

UPDATE books
    SET subject_id = (SELECT subjects.subject_id
                          FROM subjects
                        WHERE subjects.subject = 'Mystery')
  WHERE books.book_id = 12345;


SELECT books.book_id, books.title, subjects.subject 
    FROM books, subjects
  WHERE books.book_id = 12345
          AND subjects.subject_id = books.subject_id;



/* Question 6: Try to delete the new tuple from books. Explain what happens. */
\echo '\n\n Question 6'

DELETE FROM books
  WHERE books.book_id = 12345;

\echo 'A FOREIGN CONSTRAINT in the `editions` table prevents this DELETE from executing '
\echo 'as the `book_id` in `books` must not be null while `editions` as the `book_id` '
\echo 'according to the constraint'



/* Question 7: Delete both new tuples from step 4 and query the database to confirm. */
\echo '\n\n Question 7'

DELETE FROM editions
  WHERE editions.book_id = 12345;

DELETE FROM books
  WHERE books.book_id = 12345;

SELECT *
    FROM books, editions
  WHERE books.book_id = 12345
          AND editions.book_id = 12345;


/* Question 8: Now insert a book with 
 *    (book_id, title, subject_id ) of (12345, 'How I Insert', 3443). 
 *    Explain what happened.
*/
\echo '\n\n Question 8'

INSERT INTO books(book_id, title, subject_id)
    VALUES (12345, 'How I Insert', 3443);

\echo 'This INSERT fails because of the `books` table FOREIGN KEY CONSTRAINT that checks '
\echo 'the `subjects` table to ensure that the subject_id exists in the `subjects` table'



/* Question 9: Create a constraint, called ‘hasSubject’ that forces the 
 *    subject_id to not be NULL and to match one in the subjects table.
 *    Show that you can still insert an book with no author_id but not without a subject_id
 *    Now remove the new constraint and any added books
*/
\echo '\n\n Question 9'


-- Adds the constraint that subject_id can not be NULL and must be in subjects table --
ALTER TABLE books 
  ADD CONSTRAINT hasSubject 
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id), 
  ALTER COLUMN subject_id 
    SET NOT NULL;


-- Inserts a book with no author_id, but with a subject_id --
WITH insert_information AS (SELECT subject_id, 12345 AS book_id, 'My book' AS title
                                FROM subjects
                              WHERE subjects.subject = 'Computers')

INSERT INTO books(subject_id, book_id, title)
  SELECT insert_information.subject_id, insert_information.book_id, insert_information.title
      FROM insert_information;
    
-- Shows results of successful insert -- 
SELECT * 
    FROM books
  WHERE books.book_id = 12345;


-- Attempts to insert book with no subject_id --
WITH insert_information AS (SELECT 123456 AS book_id, 'My book' AS title)

INSERT INTO books(book_id, title)
  SELECT insert_information.book_id, insert_information.book_id
      FROM insert_information;

\echo 'Insert is unsuccessful because subject_id is NULL or not found'

-- Failsafe to delete our inserted books -- 
DELETE FROM books
  WHERE books.book_id = 12345 
          OR books.book_id = 123456;


-- Remove the constraints that we added --
ALTER TABLE books 
  DROP CONSTRAINT hasSubject, 
  ALTER COLUMN subject_id 
    DROP NOT NULL;
