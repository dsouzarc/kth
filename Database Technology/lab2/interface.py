#!/usr/bin/python

import pgdb
from sys import argv


class DBContext:

    """ DBContext is a small interface to a database that simplifies SQL.
        Each function gathers the minimal amount of information required and executes the query
    """


    def __init__(self): #PG-connection setup
        print("AUTHORS NOTE: If you submit faulty information here, I am not responsible for the consequences.")

        #TODO: Remove hardcoding
        params = {
                'host':'nestor2.csc.kth.se', 
                'user': '', #raw_input("Username: "), 
                'database': '', #raw_input("Database: "), 
                'password': '' #raw_input("Password: ")
        }

        self.menu = ["Select.", "Insert.", "Remove.", "Exit"]

        self.conn = pgdb.connect(**params)
        self.cur = self.conn.cursor()


    def print_menu(self):
        """ Prints a menu of all functions this program offers.  
                Returns the numerical correspondant of the choice made
        """

        for i,x in enumerate(self.menu):
            print("%i. %s"%(i+1,x))

        return self.get_int()


    def get_int(self):
        """ Retrieves an integer from the user.
            If the user fails to submit an integer, it will reprompt until an integer is submitted
        """

        while True:

            try:
                choice = int(input("Choose: "))
                if 1 <= choice <= len(self.menu):
                    return choice
                print("Invalid choice.")

            except (NameError,ValueError, TypeError, SyntaxError):
                print("That was not a number, genious.... :(")


    def select(self):
        """ Finds and prints tuples.
            Will query the user for the information required to identify a tuple.
            If the filter field is left blank, no filter will be used
            Written by the Professor
        """
        # split(",") method then creates a list of the relations
        # (tables) that you have separated by commas.  The strip
        # method just remove the white space.  So this line is read
        # from right to left, that is first the user input is parsed
        # into a list of names, then the x is set to the list contents
        # incremented thru the list then the current x is striped and
        # the words " natural join " are added to the long string
        # being defined and stored in the variable tables.

        tables = [x.strip() + " natural join " for x in raw_input("Choose table(s): ").split(",")]

        # Here we do some char pointer tricks to remove the extra " natural
        # join " (14 characters
        tables[len(tables)-1] = tables[len(tables)-1][0:len(tables[len(tables)-1])-14]

        # print the result to the screen
        print tables
        # here columns becomes the string that you type at prompt for Choose columns.

        columns = raw_input("Choose column(s): ")
        print columns

        #list comprehension building a list ready to be reduced into a string.
        filters = raw_input("Apply filters: ")


        # This will set query to the long string "SELECT columns FROM
        # tables WHERE filters;" The %s indicate that a string from a
        # variable will be inserted here, Those string variables
        # (actually expressions here) are then listed at the end
        # separated by commas.

        # lambda is a python keyword for defining a function (here with a+b)
        # reduce is a python built in way to call a function on a list 
        #   (iterable) (here each element of columns is taken as b in turn 
        # join is the python way to concatenate a list of strings
        try:
            query = """SELECT %s FROM %s%s;"""%(reduce(lambda a,b:a+b,columns), "".join(tables), "" if filters == "" else " WHERE %s"%filters)
        except (NameError,ValueError, TypeError,SyntaxError):
            print "  Bad input."
            return

        print(query)

        # Execute the query, print results- No error catching so crashes on malformed queries
        self.cur.execute(query)       
        self.print_answer()


    def get_tables_and_columns(self):
        """
            Returns a dictionary with key: table_name, value: set of columns in that table
            Created by Ryan D'souza

            :returns dict: all column names (values) mapped to their table names (key)
        """

        table_columns = {}

        query = ("SELECT table_name, column_name "
                    "FROM INFORMATION_SCHEMA.COLUMNS "
                    "WHERE table_schema='public'; ")
        self.cur.execute(query)

        result_table_values = self.cur.fetchall()

        for result_table_value in result_table_values:
            table_name = result_table_value[0]
            column_name = result_table_value[1]

            if not table_name in table_columns:
                table_columns[table_name] = set()

            table_columns[table_name].add(column_name)

        return table_columns


    def remove(self):
        """
            Removes tuples.
            Will query the user for the information required to identify a tuple.
            If the filter field is left blank, no filters will be used
        """

        table_columns = self.get_tables_and_columns()

        #Prompt user for table name - check for validity
        delete_table_name = raw_input("Choose table to delete from: ")
        if delete_table_name not in table_columns:
            raise pgdb.DatabaseError("'%s' not in database" % delete_table_name)

        
        delete_conditions = raw_input("Specify DELETE conditions: ")

        delete_command = ""

        #Delete all rows from this table
        if delete_conditions is None or len(delete_conditions) == 0 or delete_conditions == "*":
                delete_command = "DELETE * FROM {table_name}".format(table_name=delete_table_name)

        #We only delete specific rows based on a condition
        else:
            delete_command = ("DELETE FROM {table_name} WHERE {conditions}"
                                .format(table_name=delete_table_name,
                                            conditions=delete_conditions))

        print(delete_command)

        #Execute and save
        self.cur.execute(delete_command)
        self.conn.commit()


    def insert(self):
        """
            Inserts tuples.
            Will query the user for the information required to create tuples
        """

        table_columns = self.get_tables_and_columns()

        #Prompt user for the table name. Check to see if it is a valid table name
        insert_table_name = raw_input("Choose table to insert into: ")
        if insert_table_name not in table_columns:
            raise pgdb.DatabaseError("'%s' not in database" % insert_table_name)

        
        insert_column_names = raw_input("Choose column name(s): ").replace(" ", "").split(",")
        column_names_string = ""

        #Formatting for if we're specifying the column names 
        if len(insert_column_names) > 0 and len(insert_column_names[0]) > 0:
            column_names_string = " ("

            #Append every valid column name to our string
            for insert_column_name in insert_column_names:
                if insert_column_name in table_columns[insert_table_name]:
                    column_names_string += insert_column_name + ", "
                else:
                    raise pgdb.DatabaseError("'%s' not found in table '%s'" % (insert_column_name,
                                                insert_table_name))
                                                
                    
            #Get rid of the trailing comma and space, finish insert formatting
            column_names_string = column_names_string[:-2] + ")"


        #Start formatting the actual values themselves
        insert_values = raw_input("Insert value(s): ").replace(" ", "").split(",")
        insert_values_string = "("

        for insert_value in insert_values:
            insert_values_string += insert_value + ", "

        #Get rid of the trailing comma and space if we had values
        if len(insert_values) > 0:
            insert_values_string = insert_values_string[:-2]

        insert_values_string += ")"

        #Full INSERT command
        insert_command = ("INSERT INTO {table_name} {column_names} VALUES {values}"
                            .format(table_name=insert_table_name,
                                        column_names=column_names_string,
                                        values=insert_values_string))

        print(insert_command)

        #Execute and save
        self.cur.execute(insert_command)       
        self.conn.commit()


    def exit(self):    
        """ Close our database """

        self.cur.close()
        self.conn.close()
        exit()
    

    def print_answer(self):
        """ We print all the stuff that was just fetched. """

        print("\n".join([", ".join([str(a) for a in x]) for x in self.cur.fetchall()]))


    def run(self):
        """Main loop. Will divert control through the DBContext as dictated by the user."""

        actions = [self.select, self.insert, self.remove, self.exit]
        while True:
            try:
                actions[self.print_menu()-1]()
                print
            except IndexError:
                # if somehow the index into actions is wrong we just loop back
                print("Bad choice")


if __name__ == "__main__":
    db = DBContext()
    db.run()
