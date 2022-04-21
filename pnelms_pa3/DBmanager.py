#Author: Parker Nelms
#Date Last Revised: 4/20/22
#History: Version 3 - Programming Assignment 3
#Purpose: take sql commands and do basic database operations to manage database properties and metadata

from operator import concat
import os
import sys
from posixpath import split

#this will allow error messages to specify which command caused an error when multiple commands are given in one line
commandCounter = 0
#tokenCounter helps keep track of progress when parsing through command (1 when analyzing first token, 2 when analyzing second token, and so on)
tokenCounter = 0
#keeps track of whether or not a database is in use
dbUsed = False
#keeps track of the name of the database that is currently being used
currDB = None

setCol = 0

currUpdate = None
#current working directory - this naming may not be right, but it defines the directory that DBmanager.py exists in
#all database operations are done here
cwd = os.path.dirname(os.path.abspath(__file__))

#create function handles all action required by the 'create' keyword
def create(commandTokens):
    global tokenCounter

    #possible keywords that can follow 'create'
    createKeys = ["database", "table"]
    varTypes = ["float","char","int","varchar"]

    #if the token is a keyword, implement it's expected actions
    if (tokenCounter < len(commandTokens)) and (commandTokens[tokenCounter].lower() in createKeys):

        #if keyword is database, create a directory in the cwd with the same name as the next token
        if commandTokens[tokenCounter].lower() == "database":
            listDirs = os.listdir(cwd)

            #check if database already exists
            if commandTokens[tokenCounter + 1] not in listDirs:
                path = os.path.join(cwd, commandTokens[tokenCounter + 1])
                os.mkdir(path)
                print("Database '" + commandTokens[tokenCounter + 1] + "' created")
            else: 
                print("!Database '" + commandTokens[tokenCounter + 1] + "' already exists")

        #if keyword is table, create a table in the directory of the currently used database, if one is used
        elif commandTokens[tokenCounter].lower() == "table" and dbUsed == True:
            try:
                fn = concat(commandTokens[tokenCounter + 1].split('(')[0], ".txt")
                filepath = os.path.join(cwd, currDB)
                filepath = os.path.join(filepath, fn)

                #check if file already exists in current database
                if not (os.path.exists(filepath)):
                    fileLine = ""
                    syntaxOK = True

                    #offset from current token to begining of attribute list
                    i = 3
                    #parses attribute list
                    if commandTokens[tokenCounter + 3][-1] != ')':

                        #if no space between table name and attribute list, add one
                        if len(commandTokens[2].split('(')) > 1: 
                            d = '('
                            commandTokens = " ".join(commandTokens)
                            commandTokens = [d+e for e in commandTokens.split(d, 1) if e]
                            commandTokens[0] = commandTokens[0][1:]
                            commandTokens = " ".join(commandTokens)
                            commandTokens = commandTokens.split()

                        #add first attribute name
                        if commandTokens[tokenCounter + 2][0] == '(' and len(commandTokens[tokenCounter + 2][1:]) > 0:
                            fileLine = fileLine + (commandTokens[tokenCounter + 2][1:] + " ")
                        else:
                            syntaxOK = False

                        #add first attribute number
                        if commandTokens[tokenCounter + 3][:-1] in varTypes:
                            fileLine = fileLine + (commandTokens[tokenCounter + 3].split(",", 1)[0] + "|")
                        elif commandTokens[tokenCounter + 3].split("(", 1)[0] in varTypes:
                            fileLine = fileLine + (commandTokens[tokenCounter + 3].split(",", 1)[0] + "|")
                        else:
                            syntaxOK = False

                        #add any amount of in-between attributes
                        while commandTokens[tokenCounter + i + 2][-1] != ')':
                            fileLine = fileLine + (commandTokens[tokenCounter + i+1] + " ")
                            if commandTokens[tokenCounter + i][:-1] in varTypes:
                                fileLine = fileLine + (commandTokens[tokenCounter + i+2].split(",", 1)[0] + "|")
                            elif commandTokens[tokenCounter + i].split("(", 1)[0] in varTypes:
                                fileLine = fileLine + (commandTokens[tokenCounter + i+2].split(",", 1)[0] + "|")
                            else:
                                syntaxOK = False
                                break
                            i += 2 

                        #add last attribute
                        fileLine = fileLine + (commandTokens[tokenCounter + i+1] + " ")
                        if commandTokens[tokenCounter + i][:-1] in varTypes:
                            fileLine = fileLine + (commandTokens[tokenCounter + i+2].split(",", 1)[0][:-1] + "|")
                        elif commandTokens[tokenCounter + i].split("(", 1)[0] in varTypes:
                            fileLine = fileLine + (commandTokens[tokenCounter + i+2].split(",", 1)[0][:-1])
                        else:
                            syntaxOK = False
                    
                    #add attribute if only one exists
                    else:
                        if commandTokens[tokenCounter + 2][0] == '(' and len(commandTokens[tokenCounter + 2][1:]) > 0:
                            fileLine = fileLine + (commandTokens[tokenCounter + 2][1:] + " ")
                        else:
                            syntaxOK = False

                        if commandTokens[tokenCounter + 3][:-1] in varTypes:
                            fileLine = fileLine + (commandTokens[tokenCounter + 3][:-1])
                        elif commandTokens[tokenCounter + 3].split("(", 1)[0] in varTypes:
                            fileLine = fileLine + (commandTokens[tokenCounter + 3][:-1])
                        else:
                            syntaxOK = False

                    #writes full string, which was added to from previous attribute parsing, to specified table
                    if syntaxOK is True:
                        f = open(filepath, "x")
                        f = open(filepath, "w")
                        f.write(fileLine )
                        f.close()
                        print("Table '" + commandTokens[tokenCounter + 1] + "' created")
                    else:
                        print("!Table cannot be created due to syntax error.")
                else:
                    print("!Table already exists in '" + currDB + "'")
            except:
                print("!Table cannot be created due to syntax error.")
        #requires a databased to be in use in order to create a table
        elif commandTokens[tokenCounter].lower() == "table" and dbUsed == False:
            print("!Please select a database before creating a table")
    
    #checks for invalid syntax in the context of create
    elif (tokenCounter < len(commandTokens)) and not(commandTokens[tokenCounter].lower() in createKeys): 
        print("!Call '" + commandTokens[tokenCounter].lower() + "' not valid after 'CREATE'")
    elif (tokenCounter >= len(commandTokens)): 
        print("!Missing call after 'CREATE'")

#drop function handles all action required by the 'drop' keyword
def drop(commandTokens):

    #if drop target is a database
    if commandTokens[tokenCounter].lower() == "database":
        #checks if database exists, if so, deletes all files inside then deletes whole directory
        listDirs = os.listdir(cwd)
        if commandTokens[tokenCounter + 1] in listDirs:
            dbDir = os.path.join(cwd, commandTokens[tokenCounter + 1])
            for f in os.listdir(dbDir):
                os.remove(os.path.join(dbDir, f))
            os.rmdir(dbDir)
            if currDB == commandTokens[tokenCounter + 1]:
                global dbUsed 
                dbUsed = False
            print("Database '" + commandTokens[tokenCounter + 1] + "' deleted.")
        else:
            print("!Failed to delete database '" + commandTokens[tokenCounter + 1] + "' because it does not exist.")
    #if drop target is a table
    elif commandTokens[tokenCounter].lower() == "table":
        #checks if a database is used
        if dbUsed == True:
            fn = concat(commandTokens[tokenCounter + 1], ".txt")
            filepath = os.path.join(cwd, currDB)
            filepath = os.path.join(filepath, fn)

            #check if file exists in current database then deletes the database
            if (os.path.exists(filepath)):
                os.remove(filepath)
                print("Table '" + commandTokens[tokenCounter + 1] + "' deleted.")
            else:
                print("!Cannot delete to table '" + commandTokens[tokenCounter + 1] + "', because it does not exist.")
        else:
            print("!Please select a database before deleting table")
    else:
        print("!Call 'DROP' failed due to syntax error, must specify if deleting database or table.")


#left outer join select
def leftOuterJoinSelect(line2, line3):

    """
        - Perform a left outer join then output the result to the console
        - Pass this function the "from" line (from Employee E left outer join Sales S ) and then the "on"/"where" line (on E.id = S.employeeID;)
    """

    colNum = 0
    colNum2 = 0

    #first table open 
    tableName1 = line2.split()[1]
    tableName2 = line2.split()[-2]

    temp1 = line2.split()[2]

    if temp1[-1] == ',':
        temp = temp1[:-1]
        tableLabels = [[line2.split()[1], temp],[line2.split()[-2], line2.split()[-1]]] 

    else: 
        tableLabels = [[line2.split()[1], line2.split()[2]],[line2.split()[-2], line2.split()[-1]]] 
    
    
    try:
        fn = concat(tableName1, ".txt")
        filepath = os.path.join(cwd, currDB)
        filepath = os.path.join(filepath, fn)
        
        #second table open
        fn2 = concat(tableName2, ".txt")
        filepath2 = os.path.join(cwd, currDB)
        filepath2 = os.path.join(filepath2, fn2)
    except:
        print("!Please Select a database")

    #check if file exists in current database
    if (os.path.exists(filepath)) and (os.path.exists(filepath2)):
        f = open(filepath, "r")
        
        f2 = open(filepath2, "r")
        #formats each line taken from file then outputs

        f.seek(0)
        lineNum = 0

        firstLine = f.readline()

        #get the attribute index number for the first given table
        isCol = -1 
        for x in firstLine.split('|'):
            if x.split()[0] == line3[1].split('.')[1]:
                isCol += 1
                break
            else:
                colNum += 1
        if isCol == -1:
            print("!Attribute " + line3[1].split('.')[1] + " does not exist in table " + tableLabels[0][0])

        firstLine = f2.readline()

        #get the attribute index number for the second given table
        isCol = -1 
        for x in firstLine.split('|')[:-1]:

            if x.split()[0] == line3[3].split('.')[1][:-1]:
                isCol += 1
                break
            else:
                colNum2 += 1
        if isCol == -1:
            print("!Attribute " + line3[3].split('.')[1][:-1] + " does not exist in table " + tableLabels[1][0])

        #print attributes from both tables
        f.seek(0)
        f2.seek(0)
        print(f.readline()[:-1] + f2.readline()[:-1])

        #reset read and print remaining lines
        #f.seek(0)

        for x in f:
            f2.seek(0)
            isMatch = False    #if the attributes don't match include the entry for the first table anyway
            for n in f2:
                if x.split('|')[colNum] == n.split('|')[colNum2]:
                    print(x.strip() + n.strip())
                    isMatch = True

            if not isMatch:
                print(x.strip())
    else:
        print("!Cannot select from '" + tableName1 + "' and '" + tableName2 + "' because one or both do not exist.") 

#inner join select
def innerJoinSelect(line2, line3):

    """
        - Perform an inner join then output the result to the console
        - Pass this function the "from" line (from Employee E inner outer join Sales S ) and then the "on"/"where" line (on E.id = S.employeeID;)
    """

    
    colNum = 0
    colNum2 = 0

    #first table open 
    tableName1 = line2.split()[1]
    tableName2 = line2.split()[-2]

    temp1 = line2.split()[2]

    if temp1[-1] == ',':
        temp = temp1[:-1]
        tableLabels = [[line2.split()[1], temp],[line2.split()[-2], line2.split()[-1]]] 

    else: 
        tableLabels = [[line2.split()[1], line2.split()[2]],[line2.split()[-2], line2.split()[-1]]] 
    
    
    try:
        fn = concat(tableName1, ".txt")
        filepath = os.path.join(cwd, currDB)
        filepath = os.path.join(filepath, fn)
        
        #second table open
        fn2 = concat(tableName2, ".txt")
        filepath2 = os.path.join(cwd, currDB)
        filepath2 = os.path.join(filepath2, fn2)
    except:
        print("!Please Select a database")

    #check if file exists in current database
    if (os.path.exists(filepath)) and (os.path.exists(filepath2)):
        f = open(filepath, "r")
        
        f2 = open(filepath2, "r")
        #formats each line taken from file then outputs

        f.seek(0)
        lineNum = 0

        firstLine = f.readline()

        #get the attribute index number for the first given table
        isCol = -1 
        for x in firstLine.split('|'):
            if x.split()[0] == line3[1].split('.')[1]:
                isCol += 1
                break
            else:
                colNum += 1
        if isCol == -1:
            print("!Attribute " + line3[1].split('.')[1] + " does not exist in table " + tableLabels[0][0])

        firstLine = f2.readline()

        #get the attribute index number for the second given table
        isCol = -1 
        for x in firstLine.split('|')[:-1]:

            if x.split()[0] == line3[3].split('.')[1][:-1]:
                isCol += 1
                break
            else:
                colNum2 += 1
        if isCol == -1:
            print("!Attribute " + line3[3].split('.')[1][:-1] + " does not exist in table " + tableLabels[1][0])

        #print attributes from both tables
        f.seek(0)
        f2.seek(0)
        print(f.readline()[:-1] + f2.readline()[:-1])

        #reset read and print remaining lines
        f.seek(0)
        for x in f:
            f2.seek(0)
            for n in f2:
                if x.split('|')[colNum] == n.split('|')[colNum2]:
                    print(x.strip() + n.strip())
    else:
        print("!Cannot select from '" + tableName1 + "' and '" + tableName2 + "' because one or both do not exist.") 

#select function handles all action required by the 'select' keyword
def select(updateStr):

    colNum = 0
    colNum2 = 0
    line2 = ""
    line3 = ""

    #if statement allows for single or multiline select command 
    if updateStr[-1] != ';':
        line2 = input("")
        line3 = input("")

        line3 = line3.split()


        commandTokens = updateStr.split()

        #join selects where all can potentially be selected
        if commandTokens[1] == '*':
            typeJoin = line2.split()[3:-2]
            typeJoin = ''.join(typeJoin)
            typeJoin = typeJoin.lower()

            #execute given join type (inner join, left outer join)
            if (typeJoin == '') or (typeJoin == "innerjoin"):
                try: 
                    innerJoinSelect(line2, line3)
                except:
                    pass
            elif (typeJoin == "leftouterjoin"):
                try: 
                    leftOuterJoinSelect(line2, line3)
                except:
                    pass
            else: 
                print("!Invalid join type " + typeJoin)

        #conditional selects with specific attributes
        else:
            fn = concat(line2.split()[-1], ".txt")
            filepath = os.path.join(cwd, currDB)
            filepath = os.path.join(filepath, fn)  

            selectors = ""
            selectors = selectors.join(commandTokens[1:]).split(',')
     
            if (os.path.exists(filepath)):

                f = open(filepath, "r")
                indexList = []
                lines = f.read().split('\n')
                first = lines[0].split("|")

                if (first[colNum2].split()[0] == line3[1]):
                        colNum2 = 0
                else: 
                    while ((first[colNum2].split()[0] != line3[1]) and (colNum2 < len(first))):
                        colNum2 += 1
                    if colNum2 == 0:
                        print("!Where column does not exist")

                for n in selectors:
                    if (first[0].split()[0] == n):
                        colNum = 0
                    else: 
                        while ((first[colNum].split()[0] != n) and (colNum < len(first))):
                            colNum += 1
                        if colNum == 0:
                            print("!Set column does not exist")
                    indexList.append(colNum)
                
                #select line base on store conditional operator and column location
                f.seek(0)

                temp = 0
                for x in f:
                    fullLine = x.split("|")
                    if temp == 0:
                        temp = 1
                        currStep = 0
                        for t in fullLine:
                            if currStep in indexList:
                                print(t, end = '|')
                            currStep += 1
                        print('')                    
                    elif line3[2] == "=" and float(fullLine[colNum2][0]) == float(line3[3][0]) and temp != 0:
                        currStep = 0
                        for t in fullLine:
                            if currStep in indexList:
                                print(t, end = '|')
                            currStep += 1
                        print('')    
                    elif line3[2] == "!=" and float(fullLine[colNum2][0]) != float(line3[3][0]) and temp != 0:
                        currStep = 0
                        for t in fullLine:
                            if currStep in indexList:
                                print(t, end = '|')
                            currStep += 1
                        print('')    

                    elif line3[2] == "<=" and float(fullLine[colNum2][0]) <= float(line3[3][0]) and temp != 0:
                        currStep = 0
                        for t in fullLine:
                            if currStep in indexList:
                                print(t, end = '|')
                            currStep += 1
                        print('')    
                    elif line3[2] == ">=" and float(fullLine[colNum2][0]) >= float(line3[3][0]) and temp != 0:
                        currStep = 0
                        for t in fullLine:
                            if currStep in indexList:
                                print(t, end = '|')
                            currStep += 1
                        print('')    
                    elif line3[2] == "<" and float(fullLine[colNum2][0]) < float(line3[3][0]) and temp != 0:
                        currStep = 0
                        for t in fullLine:
                            if currStep in indexList:
                                print(t, end = '|')
                            currStep += 1
                        print('')
                    elif line3[2] == ">" and float(fullLine[colNum2][0]) > float(line3[3][0]) and temp != 0:
                        currStep = 0
                        for t in fullLine:
                            if currStep in indexList:
                                print(t, end = '|')
                            currStep += 1
                        print('')    
    else:
        commandTokens = updateStr[:-1].split()
        #select all from specified file 
        fn = concat(commandTokens[-1].lower(), ".txt")
        filepath = os.path.join(cwd, currDB)
        filepath = os.path.join(filepath, fn)

        if commandTokens[1] == '*':
            #check if file exists in current database
            if (os.path.exists(filepath)):
                f = open(filepath, "r")
                #formats each line taken from file then outputs
                for x in f:
                    fullLine = x.split("|")
                    for t in fullLine[:-1]:
                        print(t, end = '|')
                    print('')
            else:
                print("!Cannot select from '" + commandTokens[3] + "' because it does not exist.")
        else:
            selectors = ""
            selectors = selectors.join(commandTokens[1:-2]).split(',')
            print(selectors)
     
            if (os.path.exists(filepath)):

                f = open(filepath, "r")
                indexList = []
                lines = f.read().split('\n')
                first = lines[0].split("|")

                for n in selectors:
                    if (first[0].split()[0] == n):
                        colNum = 0
                    else: 
                        while ((first[colNum].split()[0] != n) and (colNum < len(first))):
                            colNum += 1
                        if colNum == 0:
                            print("!Set column does not exist")
                    indexList.append(colNum)
                
                print(indexList)
                #formats each line taken from file then outputs
                f.seek(0)
                for x in f:
                    fullLine = x.split("|")
                    currStep = 0
                    for t in fullLine:
                        if currStep in indexList:
                            print(t, end = '|')
                        currStep += 1

                    print('')        
                    

#alter function handles all action required by the 'alter' keyword
def alter(commandTokens):
    #keywords list set up for more alter operations
    alterKeys = ["add", ""]
    #dictionary definition for each operation
    key_commands = {"add":add}
    global tokenCounter

    #check if next token is an operation then calls it's corresponding function with a dictionary call
    if commandTokens[tokenCounter + 2].lower() in alterKeys and commandTokens[tokenCounter].lower() == "table":
        tokenCounter += 1
        key_commands[commandTokens[tokenCounter + 1].lower()](commandTokens)
    else:
        print("!Failed to alter due to syntax error")

#use function handles all action required by the 'use' keyword
def use(commandTokens):

    #check if database exists, and if so, toggles dbUsed and sets currDB
    listDirs = os.listdir(cwd)
    if commandTokens[tokenCounter] in listDirs:
        global currDB
        currDB = commandTokens[tokenCounter]
        global dbUsed 
        dbUsed = True
        print("Using Database '" + currDB + "'.")
    else:
        print("Cannot use database '" + commandTokens[tokenCounter] + "' as it does not exist")

#add function handles all action required by the 'add' keyword
def add(commandTokens):
    #define acceptable attribute types
    varTypes = ["float","char","int","varchar"]
    if dbUsed == True:
        fn = concat(commandTokens[tokenCounter], ".txt")
        filepath = os.path.join(cwd, currDB)
        filepath = os.path.join(filepath, fn)

        #check if file exists in current database then writes given attribute to table
        if (os.path.exists(filepath)):
            if (commandTokens[tokenCounter + 3] in varTypes) or (commandTokens[tokenCounter + 3].split("(", 1)[0] in varTypes):
                f = open(filepath, "a")
                f.write(",    " + commandTokens[tokenCounter + 2] + " " + commandTokens[tokenCounter + 3])
                print("Table '" + commandTokens[tokenCounter] + "' modified.")
                f.close()
            else:
                print("!Cannot add to table '" + commandTokens[tokenCounter] + "' due to syntax error.")
        else:
            print("!Cannot add to table '" + commandTokens[tokenCounter] + "', because it does not exist.")
    else:
        print("!Please select a database before altering table")


def insert(commandTokens):
    fullCom = ''.join(commandTokens)
    dataList = fullCom[fullCom.find('(')+1:fullCom.find(')')].split(',')

    if dbUsed == True:
        fn = concat(commandTokens[tokenCounter + 1], ".txt")
        filepath = os.path.join(cwd, currDB)
        filepath = os.path.join(filepath, fn)

        #check if file exists in current database then writes given data to table as a line
        if (os.path.exists(filepath)):
            f = open(filepath, "a")
            f.write("\n")
            for n in dataList:
                f.write(n + '|')
            print("1 new record inserted.")
            f.close()
        else:
            print("!Cannot add to table '" + commandTokens[tokenCounter] + "', because it does not exist.")
    else:
        print("!Please select a database before altering table")

#setData
def deleteData(compField, compVal, operator):

    deletedCount = 0
    colNum2 = 0

    #check if database exists
    if dbUsed == True:
        fn = concat(currUpdate, ".txt")
        filepath = os.path.join(cwd, currDB)
        filepath = os.path.join(filepath, fn)

        #check if file exists in current database then writes given attribute to table
        if (os.path.exists(filepath)):
            f = open(filepath, "r+")
            lines = f.read().split('\n')
            first = lines[0].split("|")

            #stores 'where' column based on input 
            if (first[colNum2].split()[0] == compField):
                colNum2 = 0
            else: 
                while ((first[colNum2].split()[0] != compField) and (colNum2 < len(first))):
                    colNum2 += 1
                if colNum2 == 0:
                    print("!Where column does not exist")

            #deletes lines and checks for each which operator is used
            numloop = 0
            f.seek(0)
            linesList = f.readlines()
            lines = linesList[0]
            if operator == '=':
                for line in linesList[1:]:
                    numloop += 1
                    if line.split("|")[colNum2].split()[0] == compVal: 
                        deletedCount += 1
                        continue 
                    else:
                        lines = lines + line
            elif operator == '!=':
                for line in linesList[1:]:
                    numloop += 1
                    if line.split("|")[colNum2].split()[0] != compVal: 
                        deletedCount += 1
                        continue 
                    else:
                        lines = lines + line
            elif operator == '<=':
                for line in linesList[1:]:
                    numloop += 1
                    val = line.split("|")[colNum2].split()[0]
                    if float(val) <= float(compVal): 
                        deletedCount += 1
                        continue 
                    else:
                        lines = lines + line
            elif operator == '>=':
                for line in linesList[1:]:
                    numloop += 1
                    val = line.split("|")[colNum2].split()[0]
                    if float(val) >= float(compVal): 
                        deletedCount += 1
                        continue 
                    else:
                        lines = lines + line
            elif operator == '<':
                for line in linesList[1:]:
                    numloop += 1
                    val = line.split("|")[colNum2].split()[0]
                    if float(val) < float(compVal): 
                        deletedCount += 1
                        continue  
                    else:
                        lines = lines + line
            elif operator == '>':
                for line in linesList[1:]:
                    numloop += 1
                    val = line.split("|")[colNum2].split()[0]
                    if float(val) > float(compVal): 
                        deletedCount += 1
                        continue 
                    else:
                        lines = lines + line

            #closes file and opens a new file that writes the restructured data over the old data
            f.close()
            writeFile = open(filepath, "w")
            writeFile.write(lines)
            writeFile.close()
            if deletedCount == 1:
                print(str(deletedCount) + " record deleted \n")
            elif deletedCount > 1:
                print(str(deletedCount) + " records deleted \n")
            elif deletedCount == 0:
                print("No records deleted \n")
        else:
            print("!Cannot update table '" + currUpdate + "', because it does not exist.")
    else:
        print("!Please select a database before altering table")


#setData
def setData(setField, setVal, compField, compVal, operator):

    colNum = 0
    colNum2 = 0

    if dbUsed == True:
        fn = concat(currUpdate, ".txt")
        filepath = os.path.join(cwd, currDB)
        filepath = os.path.join(filepath, fn)

        #check if file exists in current database then writes given attribute to table
        if (os.path.exists(filepath)):
            f = open(filepath, "r+")
            lines = f.read().split('\n')
            first = lines[0].split("|")
            if (first[colNum].split()[0] == setField):
                colNum = 0
            else: 
                print(first[colNum].split())
                while ((first[colNum].split()[0] != setField) and (colNum < len(first))):
                    colNum += 1
                if colNum == 0:
                    print("!Set column does not exist")

            if (first[colNum2].split()[0] == compField):
                colNum2 = 0
            else: 
                while ((first[colNum2].split()[0] != compField) and (colNum2 < len(first))):
                    colNum2 += 1
                if colNum2 == 0:
                    print("!Where column does not exist")

            numloop = 0

            f.seek(0)
            linesList = f.readlines()
            lines = linesList[0]
            if operator == '=':
                for line in linesList[1:]:
                    numloop += 1
                    if line.split("|")[colNum2].split()[0] == compVal: 
                        line = line.split("|")
                        line[colNum] = setVal
                        lines = lines + "|".join(line) 
                    else:
                        lines = lines + line
            elif operator == '!=':
                for line in linesList[1:]:
                    numloop += 1
                    if line.split("|")[colNum2].split()[0] != compVal: 
                        line = line.split("|")
                        line[colNum] = setVal
                        lines = lines + "|".join(line) 
                    else:
                        lines = lines + line
            elif operator == '<=':
                for line in linesList[1:]:
                    numloop += 1
                    if line.split("|")[colNum2].split()[0] <= compVal: 
                        line = line.split("|")
                        line[colNum] = setVal
                        lines = lines + "|".join(line) 
                    else:
                        lines = lines + line
            elif operator == '>=':
                for line in linesList[1:]:
                    numloop += 1
                    if line.split("|")[colNum2].split()[0] >= compVal: 
                        line = line.split("|")
                        line[colNum] = setVal
                        lines = lines + "|".join(line) 
                    else:
                        lines = lines + line
            elif operator == '<':
                for line in linesList[1:]:
                    numloop += 1
                    if line.split("|")[colNum2].split()[0] < compVal: 
                        line = line.split("|")
                        line[colNum] = setVal
                        lines = lines + "|".join(line) 
                    else:
                        lines = lines + line
            elif operator == '>':
                for line in linesList[1:]:
                    numloop += 1
                    if line.split("|")[colNum2].split()[0] > compVal: 
                        line = line.split("|")
                        line[colNum] = setVal
                        lines = lines + "|".join(line) 
                    else:
                        lines = lines + line

            #f.write(lines)
            f.close()
            writeFile = open(filepath, "w")
            writeFile.write(lines)
            writeFile.close()
        else:
            print("!Cannot update table '" + currUpdate + "', because it does not exist.")
    else:
        print("!Please select a database before altering table")

#update function calls setData and feeds it key info
def update(updateStr):
    global currUpdate
    try:
        line1 = updateStr.split()
        currUpdate = line1[1]
        line2 = input("").split()
        line3 = input("").partition(";")[0].split()
        setData(line2[1], line2[3], line3[1], line3[3], line3[2])
    except:
        print("!Cannot insert due to syntax error")
        pass
    
#delete calls deleteData and feeds it key info
def delete(updateStr):
    global currUpdate
    try:
        line1 = updateStr.split()
        currUpdate = line1[2]
        line2 = input("").partition(";")[0].split()
        deleteData(line2[1], line2[3], line2[2])
    except:
        print("!Cannot insert due to syntax error")
        pass

#main function
def main():
    #fancy formating for program start
    print(" ")
    print("-- CS457 PA1 - Parker Nelms --")
    print(" ")

    #allow the global tokenCounter to be used in main
    global tokenCounter

    #
    global commandCounter

    #list of first token keywords
    keywords = ["create", "drop", "select", "alter", "use", "insert", "update", "delete"]

    #associate keywords with functions to be automatically called when parsed
    key_commands = {'create':create, 'drop':drop, 'select':select, 'alter':alter, 'use':use, 'insert':insert, 'update':update, 'delete':delete}

    #list of separated token from user input
    commandTokens = "null"


    #loop program until .exit keyword is entered
    #.exit can currently be succeeded by other tokens as they will be ignored
    while not (commandTokens[0].lower() == ".exit"):
        #reset token and command counter upon new user input
        commandCounter = 0
        tokenCounter = 0

        allCommands = ['']

        userCom = input("")
        userCom = userCom.replace("\r", "")

        userCom = userCom.strip()

        #ignore comments/blank lines and ensures semicolon is placed after commands, unless it is the .EXIT command
        if userCom:
            if "--" in userCom.split()[0]:
                continue
            elif userCom.split()[0].lower() == "update":
                key_commands[userCom.split()[0].lower()](userCom)
            elif userCom.split()[0].lower() == "delete":
                key_commands[userCom.split()[0].lower()](userCom)
            elif userCom.split()[0].lower() == "select":
                key_commands[userCom.split()[0].lower()](userCom)
            elif userCom[-1] == ';':
                allCommands = userCom.split(';')
            elif userCom.lower() == ".exit":
                allCommands = [userCom, '']
            else:
                print("!Missing ';'.")
        else:
            continue

        #support multiple commands per line
        for x in allCommands[:-1]:
            
            tokenCounter = 0
            commandCounter += 1
            
            #splits tokens in command into a list
            #split() will split the characters of .exit into a list, which is undesirable 
            if x != ".exit;":
                commandTokens = x.split()
            else:
                commandTokens = x

            #I can't remember what this fixes
            if len(x) == 0:
                print("!Missing ';'.")

            #if keyword is recognized, automatically call associated function
            #automatically converts case to lower, which is default for the rest of the program
            if commandTokens[0].lower() in keywords:
                tokenCounter += 1
                key_commands[commandTokens[0].lower()](commandTokens)
            elif commandTokens[0].lower() != ".exit": 
                print("!Keyword '" + commandTokens[0] + "' not valid")
            else:
                print("All done.")

if __name__ == "__main__":
    main();
