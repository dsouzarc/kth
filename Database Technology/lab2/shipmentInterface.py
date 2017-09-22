#!/usr/bin/python

import pgdb

from sys import argv

class DBContext:
    """
        DBContext is a small interface to a database that simplifies SQL.
        Each function gathers the minimal amount of information required and executes the query
    """

    def __init__(self): 

        print("AUTHORS NOTE: If you submit faulty information here, I am not responsible for the consequences.")
        print "The idea is that you, the authorized database user, log in."
        print "Then the interface is available to employees whos should only be able to enter shipments as they are made."

        params = {
                    'host' : 'nestor2.csc.kth.se', 
                    'user' : raw_input("Username: "), 
                    'database' : '', 
                    'password' : raw_input("Password: ")
        }

        self.conn = pgdb.connect(**params)
        self.menu = ["Record a shipment","Show stock", "Show shipments", "Exit"]
        self.cur = self.conn.cursor()


    def print_menu(self):
        """
            Prints a menu of all functions this program offers
            Returns the numerical correspondant of the choice made

            :return int: numerical choice
        """

        for i,x in enumerate(self.menu):
            print("%i. %s"%(i+1,x))
        return self.get_int()


    def get_int(self):
        """
            Retrieves an integer from the user.
            If the user fails to submit an integer, it will reprompt until an integer is submitted

            :return int: valid numerical choice
        """

        while True:
            try:
                choice = int(input("Choose: "))
                if 1 <= choice <= len(self.menu):
                    return choice
                print("Invalid choice.")
            except (NameError,ValueError, TypeError,SyntaxError):
                print("That was not a number, genious.... :(")

 
    def makeShipments(self):
        """
            Given shipment information, checks to make sure we have the book in stock
            If we do, decrements the stock and creates a new shipment order
            If anything happens, rollsback the shipment transaction
        """

        CID = raw_input("cutomerID: ")
        try:
            int(CID)
        except Exception:
            raise ValueError("Invalid customerID: '%s'" % CID)

        SID = input("shipment ID: ")
        try:
            int(SID)
        except Exception:
            raise ValueError("Invalid shipmentID: '%s'" % SID)

        Sisbn= raw_input("isbn: ").strip()
        Sdate= raw_input("Ship date: ").strip()

        # Check to see how many books with this ISBN are left
        stock_query = "SELECT stock.stock FROM stock WHERE stock.isbn = %s"
        stock_left = None
        try:
            self.cur.execute(stock_query, (Sisbn,))
            stock_left = self.cur.fetchone()
        except pgdb.DatabaseError as query_error:
            raise ValueError("Invalid query or connecting to database: %s" % query_error)
        except Error as general_error:
            raise Exception("Error connecting to database: %s" % general_error)


        #Handle no book with that ISBN or no books in general
        if not stock_left:
            raise ValueError("No book in stock with isbn '%s' found" % Sisbn)

        if stock_left <= 0:
            print("No more books in stock :(")
            return
        else:
            print "WE have the book in stock"


        update_stock_query = "UPDATE stock SET stock = stock-1 WHERE isbn=%s;"
        try:
            self.cur.execute(update_stock_query, (Sisbn,))
        except pgdb.DatabaseError as update_error:
            self.conn.rollback()
            raise ValueError("Unable to update stock count: %s" % update_error)

        print "stock decremented" 
   
        insert_query = ("INSERT INTO shipments(shipment_id, customer_id, isbn, ship_date) "
                            "VALUES (%s, %s, %s, %s);")
        try:
            self.cur.execute(insert_query, (int(SID), int(CID), Sisbn, Sdate))
        except pgdb.DatabaseError as insert_error:
            self.conn.rollback()
            raise ValueError("Unable to insert book - reverting shipment: %s" % insert_error)

        #End the transaction, save everything 
        print "shipment created" 
        self.conn.commit()        


    def showStock(self):
        query = """SELECT * FROM stock;"""
        print query
        try:
            self.cur.execute(query)
        except (pgdb.DatabaseError, pgdb.OperationalError):
            print "  Exception encountered while modifying table data." 
            self.conn.rollback ()
            return   
        self.print_answer()


    def showShipments(self):
        query = """SELECT * FROM shipments;"""
        print query
        try:
            self.cur.execute(query)
        except (pgdb.DatabaseError, pgdb.OperationalError):
            print "  Exception encountered while modifying table data." 
            self.conn.rollback ()
            return   
        self.print_answer()


    def exit(self):    
        self.cur.close()
        self.conn.close()
        exit()


    def print_answer(self):
        print("\n".join([", ".join([str(a) for a in x]) for x in self.cur.fetchall()]))


    def run(self):
        """
            Main loop.
            Will divert control through the DBContext as dictated by the user
        """

        actions = [self.makeShipments, self.showStock, self.showShipments, self.exit]
        while True:
            try:
                actions[self.print_menu()-1]()
            except IndexError:
                print("Bad choice")
                continue


if __name__ == "__main__":
    db = DBContext()
    db.run()
