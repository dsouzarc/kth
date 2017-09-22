#!/usr/bin/python

import pgdb

import re
from sys import argv

#  The code should not allow the customer to find out other customers or other booktown data.
#  Security is taken as the customer knows his own customer_id, first and last names.  
#  So not really so great but it illustrates how one would check a password if there were the addition of encription.

#  Most of the code is here except those little pieces needed to avoid injection attacks.  
#  You might want to read up on pgdb, postgresql, and this useful function: pgdb.escape_string(some text)

#  You should also add exception handling.  Search WWW for 'python try' or 'exception' for things like:
#         try: 
#             ...
#         except (errorcode1, errorcode2,...):
#             ....
# A good tip is the error message you get when exceptions are not caught such as:
#  Traceback (most recent call last):
#  File "./customerInterface.py", line 105, in <module>
#    db.run()
#  File "./customerInterface.py", line 98, in run
#    actions[self.print_menu()-1]()
#  File "./customerInterface.py", line 68, in shipments
#    self.cur.execute(query)
#  File "/usr/lib/python2.6/dist-packages/pgdb.py", line 259, in execute
#    self.executemany(operation, (params,))
#  File "/usr/lib/python2.6/dist-packages/pgdb.py", line 289, in executemany
#    raise DatabaseError("error '%s' in '%s'" % (msg, sql))
# pg.DatabaseError: error 'ERROR:  syntax error at or near "*"
# LINE 1: SELECT * FROM * WHERE *
#
#  You should think "Hey this pg.DatabaseError (an error code) mentioned above could be caught at 
#  File "./customerInterface.py", line 68, in shipments  self.cur.execute(query) also mentioned above."
#  The only problem is the codes need to be pgdb. instead of the pg. shown in my output 
#  (I am not sure why they are different) so the code to catch is pgdb.DatabaseError.
#
#

class DBContext:
    """
        DBContext is a small interface to a database that simplifies SQL.
        Each function gathers the minimal amount of information required and executes the query
    """

    def __init__(self): 
        print("AUTHORS NOTE: If you submit faulty information here, I am not responsible for the consequences.")

        print "The idea is that you, the authorized database user, log in."
        print "Then the interface is available to customers whos should only be able to see their own shipments."

        params = {
            'host': 'nestor2.csc.kth.se', 
            'user': raw_input("Username: "), 
            'database': '', 
            'password': raw_input("Password: ")
        }

        self.conn = pgdb.connect(**params)
        self.menu = ["Shipments Status", "Exit"]
        self.cur = self.conn.cursor()


    def print_menu(self):
        """
            Prints a menu of all functions this program offers

            :return int: the numerical correspondant of the choice made
        """

        for i,x in enumerate(self.menu):
            print("%i. %s"%(i+1,x))

        return self.get_int()


    def get_int(self):
        """
            Retrieves an integer from the user.
            If the user fails to submit an integer, it will reprompt until an integer is submitted

            :return int: selected choice
        """

        while True:
            try:
                choice = int(input("Choose: "))
                if 1 <= choice <= len(self.menu):
                    return choice
                print("Invalid choice.")

            except (NameError,ValueError, TypeError,SyntaxError):
                print("That was not a number, genious.... :(")

 
    def shipments(self):
        """
            Prompts user for a customer_id, validates with user supplied first and last name
            Prints out all shipments for that customer
        """
 
        # ID should be hard typed to an integer - they can enter: 1 OR 1=1  
        customer_id = raw_input("customerID: ")
        try:
            int(customer_id)
        except Exception as parsing_exception:
            raise ValueError("Invalid input for customerID: %s" % customer_id)


        # These names inputs allow injection attacks - they can enter: Hilbert' OR 'a'='a  
        first_name = raw_input("First Name: ").strip()
        last_name = raw_input("Last Name: ").strip()


        #Validate that the input they gave us is correct - avoid injection by using this format
        validate_query = "SELECT first_name, last_name FROM customers WHERE customer_id = %s;"
        try:
            self.cur.execute(validate_query, (customer_id,))
        except pgdb.DatabaseError as query_error:
            raise ValueError("Invalid query or connecting to database: %s" % query_error)
        except Error as general_error:
            raise Exception("Error connecting to database: %s" % general_error)

        #Because of unique key, we only need to look at one response
        validate_response = self.cur.fetchone()

        #No customer with that ID found
        if not validate_response:
            raise ValueError("No customer with customer_id = '%s' found" % customer_id)

        #Validate the first and last name
        if not (first_name == validate_response[0] and last_name == validate_response[1]):
            raise ValueError("Incorrect customer name for customer_id")
        else:
            print("good name")


        # Print out a listing of shipment_id,ship_date,isbn,title for this customer
        shipment_query = ("SELECT shipment_id, ship_date, shipment.isbn, book.title "
                            "FROM shipments AS shipment "
                            "INNER JOIN editions AS edition "
                                "ON edition.isbn = shipment.isbn "
                            "INNER JOIN books AS book "
                                "ON book.book_id = edition.book_id "
                                    "WHERE shipment.customer_id = %s; ")

        
        try:
            self.cur.execute(shipment_query, (customer_id,))
        except pgdb.DatabaseError as query_error:
            raise ValueError("Error with executing query: %s" % query_error)
        except Error as general_error:
            raise Exception("Error connecting to database: %s" % general_error)

       
        # Here the list should print for example:  
        #    Customer 860 Tim Owens:
        #    shipment_id,ship_date,isbn,title
        #    510, 2001-08-14 16:33:47+02, 0823015505, Dynamic Anatomy

        print("Customer %s %s %s" % (customer_id, first_name, last_name))
        print("shipment_id,ship_date,isbn,title")
        self.print_answer()


    def exit(self):    
        """ Close the database connections """

        self.cur.close()
        self.conn.close()
        exit()


    def print_answer(self):
        """ Print the most recent database results """

        print("\n".join([", ".join([str(a) for a in x]) for x in self.cur.fetchall()]))


    def run(self):
        """
            Main loop - divert control through the DBContext as dictated by the user
        """

        actions = [self.shipments, self.exit]
        while True:
            try:
                actions[self.print_menu()-1]()
            except IndexError:
                print("Bad choice")
                continue


if __name__ == "__main__":
    db = DBContext()
    db.run()
