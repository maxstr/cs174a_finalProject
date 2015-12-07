#!/usr/bin/env python


# Listen, I realize that there's no input sanitation in this application. I'm sorry.
from cffi import FFI
from tabulate import tabulate
import sys
import mysql.connector
from itertools import izip


ffi = FFI()
cdef = None
with open('WrappedCrypto.h', 'r') as f:
    cdef = f.read()
ffi.cdef(cdef)
cryptoLib = ffi.dlopen('cryptoLib.o')

global_data = []
keys = None
KEYSIZE = 128

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
##          5. Generate new keys
##          6. Print keys
##          7. Exit
##
################################################################################"""
def main(argv=None):
    global keys
    global global_data
    connection = mysql.connector.connect(user=USER, password=PASSWORD, host=HOST, port=PORT, database=DB)
    cursor = connection.cursor()
    print(prompt)
    response = getNum("Please enter an option " + ("(key generated)" if keys else "(no key generated)") + "\n")
    while 1:
        queryDict = {}
        if (response == 1):
            if not keys:
                print("Autogenerating keys.")
                keys = cryptoLib.generate_keys()
            queryDict['empID'] = getNum("Please enter the employee ID\n")
            queryDict['empAge'] = getNum("Please enter the employee's age\n")
            salaryInput = getNum("Please enter the employee's salary\n")

            ffiInt_salary = ffi.new("unsigned int *", salaryInput)
            ffiInt_ctSize = ffi.new("int *")
            ffiUC_encrypted = cryptoLib.toText(cryptoLib.encrypt_num(ffiInt_salary[0], keys.public, ffiInt_ctSize))
            encryptedString = ""
            for i in range(ffiInt_ctSize[0]):
                encryptedString += str(chr(int(ffiUC_encrypted[i])))
            print("Encrypted value: %s" % encryptedString)
            queryDict['empSalary'] = encryptedString
            queryDict['pubKey'] = ffi.string(keys.public)

            try:
                cursor.execute("INSERT INTO Employees VALUES"\
                           "(%(empID)s, %(empAge)s, %(empSalary)s, %(pubKey)s)", queryDict)
                connection.commit()
                print("User added.")
            except:
                print ("An error occurred!")
        elif (response == 2):
            if not keys:
                print("Autogenerating keys.")
                keys = cryptoLib.generate_keys()
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
            if not keys:
                print("Autogenerating keys.")
                keys = cryptoLib.generate_keys()
            try:
                query = "SELECT * FROM Employees e WHERE e.pubKey = \"%s\"" % ffi.string(keys.public)
                cursor.execute(query)
                print("Printing result data")
                printTableRows(cursor.fetchall(), cursor.column_names)
            except:
                print ("An error occurred!")
        elif (response == 4):
            if not keys:
                print("Autogenerating keys.")
                keys = cryptoLib.generate_keys()
            query = "SELECT SUM_HE(e.SALARY, e.pubKey) AS SUM FROM Employees e WHERE e.pubKey = \"%s\" AND %s %s HAVING 1 AND %s"
            whereClause = "1 = 1"
            groupClause = ""
            havingClause = "1"
            if (raw_input("Where clause? (y/n) ").lower() == 'y'):
                whereClause = raw_input("Please enter the where clause (no WHERE).\n")
            if (raw_input("Group by age? (y/n) ").lower() == 'y'):
                groupClause = "GROUP BY age"
                query = "SELECT SUM_HE(SALARY, pubKey) AS SUM, age FROM Employees WHERE pubKey = \"%s\" AND %s %s HAVING 1 AND %s"
                if (raw_input("Having clause? (y/n) ").lower() == 'y'):
                    havingClause = raw_input("Please enter the having clause (no HAVING).\n")
            try:
                query = query % (ffi.string(keys.public), whereClause, groupClause, havingClause)
                cursor.execute(query)
                print("Printing result data")
                printTableRowsSum(cursor.fetchall(), cursor.column_names)
            except:
                print "an error occurred!"



        elif (response == 5):
            keys = cryptoLib.generate_keys()
            print("Keys generated.")
        elif (response == 6):
            print "Public:\t%s \nPrivate:\t%s" % (ffi.string(keys.public), ffi.string(keys.private))
            pass
        elif (response == 7):
            break
        response = getNum("Please enter an option " + ("(key generated)" if keys else "(no key generated)") + "\n")
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
        newRow = list(row)
        encryptedSalary = newRow[2]
        encryptLength = len(encryptedSalary)
        ffiUC_encryptedSalary = ffi.new("unsigned char[%i]" % encryptLength, list(encryptedSalary))
        newRow[2] = int(cryptoLib.decrypt_num(cryptoLib.toData(ffiUC_encryptedSalary), keys.public, keys.private, encryptLength))
        rows.append(newRow)
    print(tabulate(rows, headers = columns))
def printTableRowsSum(tuples, columns):
    rows = []
    for row in tuples:
        newRow = list(row)
        encryptedSalaryHex = newRow[0]
        encryptedSalary = newRow[0][:-1].decode('hex_codec')
        encryptLength = len(encryptedSalary)
        ffiUC_encryptedSalary = ffi.new("unsigned char[%i]" % encryptLength, encryptedSalary)
        newRow[0] = int(cryptoLib.decrypt_num(cryptoLib.toData(ffiUC_encryptedSalary), keys.public, keys.private, encryptLength))
        rows.append(newRow)
    print(tabulate(rows, headers = columns))


def decryptSalary(salaryString, pubKey, privKey, size):
    return int(cryptoLib.decrypt_num(cryptoLib.toData(salaryString), pubKey, privKey, size))

def grouped(iterable, n):
    "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
    return izip(*[iter(iterable)]*n)

if __name__ == "__main__":
    sys.exit(main())
