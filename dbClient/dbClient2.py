#!/usr/bin/env python
from cffi import FFI
from tabulate import tabulate
import sys
import mysql.connector

ffi = FFI()
cryptoLib = ffi.dlopen('cryptoLib.o')
ff

USER = 'root'
PASSWORD = ''
HOST = '127.0.0.1'
PORT = 3306
DB = 'project'
prompt = """\
################################################################################
##
##              Final Project!
##
##          Options:
##          1. Insert emp_id emp_age emp_salary
##          2. Select emp_id
##          3. Select *
##          4. Select SUM
##          5. Exit
##
################################################################################"""
def main(argv=None):
    connection = mysql.connector.connect(user=USER, password=PASSWORD, host=HOST, port=PORT, database=DB)
    cursor = connection.cursor()
    print(prompt)
    response = getNum("Please enter an option\n")
    while (response != 5):
        queryDict = {}
        if (response == 1):
            queryDict['empID'] = getNum("Please enter the employee ID\n")
            queryDict['empAge'] = getNum("Please enter the employee's age\n")
            queryDict['empSalary'] = getNum("Please enter the employee's salary\n")
            try:
                cursor.execute("INSERT INTO Employees VALUES"\
                           "(%(empID)i, %(empAge)i, %(empSalary)i)" % queryDict)
                connection.commit()
                print("User added.")
            except:
                print ("An error occurred!")
        elif (response == 2):
            queryDict['empID'] = getNum("Please enter the employee ID\n")
            try:
                query = "SELECT * FROM Employees " \
                               "WHERE id = %(empID)i" % queryDict
                cursor.execute(query)
                print("Printing result data")
                printTableRows(cursor.fetchall(), cursor.column_names)
            except:
                print ("An error occurred!")
        elif (response == 3):
            try:
                query = "SELECT * FROM Employees "
                cursor.execute(query)
                print("Printing result data")
                printTableRows(cursor.fetchall(), cursor.column_names)
            except:
                print ("An error occurred!")
        elif (response == 4):
            pass
        response = getNum("Please enter an option\n")
    connection.close()
    return 0



def getNum(prompt):
    num = None
    while (not num):
        try:
            num = int(raw_input(prompt))
        except ValueError:
            print ("Please enter a number.")
    return num
def printTableRows(tuples, columns):
    rows = []
    for row in tuples:
        rows.append(list(row))
    print(tabulate(rows, headers = columns))










if __name__ == "__main__":
    sys.exit(main())
