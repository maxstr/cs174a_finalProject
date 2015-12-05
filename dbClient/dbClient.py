#!/usr/bin/env python
from cffi import FFI
from tabulate import tabulate
import sys
import mysql.connector

ffi = FFI()
cdef = None
with open('WrappedCrypto.h', 'r') as f:
    cdef = f.read()
ffi.cdef(cdef)
cryptoLib = ffi.dlopen('cryptoLib.o')

global_data = []
keys = None

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
            ffiUC_encrypted = cryptoLib.toText(cryptoLib.encrypt_num(ffiInt_salary[0], keys.public, ffiInt_ctSize), ffiInt_ctSize[0])
            encryptedString = ""
            for i in range(ffiInt_ctSize[0]):
                encryptedString += str(chr(int(ffiUC_encrypted[i])))
            print("Encrypted value: %s" % encryptedString)
            queryDict['empSalary'] = encryptedString.encode('hex_codec')

            try:
                cursor.execute("INSERT INTO Employees VALUES"\
                           "(%(empID)i, %(empAge)i, \"%(empSalary)s\")" % queryDict)
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
                query = "SELECT * FROM Employees "
                cursor.execute(query)
                print("Printing result data")
                printTableRows(cursor.fetchall(), cursor.column_names)
            except:
                print ("An error occurred!")
        elif (response == 4):
            if not keys:
                print("Autogenerating keys.")
                keys = cryptoLib.generate_keys()
            pass
        elif (response == 5):
            keys = cryptoLib.generate_keys()
            print("Keys generated.")
        elif (response == 6):
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
        encryptedSalary = newRow[2].decode('hex_codec')
        encryptLength = len(encryptedSalary)
        ffiUC_encryptedSalary = ffi.new("unsigned char[%i]" % encryptLength, map(ord, list(encryptedSalary)))
        newRow[2] = int(cryptoLib.decrypt_num(cryptoLib.toData(ffiUC_encryptedSalary), keys.public, keys.private, encryptLength))
        rows.append(newRow)
    print(tabulate(rows, headers = columns))

def decryptSalary(salaryString, pubKey, privKey, size):
    return int(cryptoLib.decrypt_num(cryptoLib.toData(salaryString), pubKey, privKey, size))













if __name__ == "__main__":
    sys.exit(main())
