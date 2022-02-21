#Author: Parker Nelms
#Date Last Revised: 2/21/22
#History: Version 1 - Programming Assignment 1
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
currDB = "null"
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
                fn = concat(commandTokens[tokenCounter + 1], ".txt")
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

                        #add first attribute name
                        if commandTokens[tokenCounter + 2][0] == '(' and len(commandTokens[tokenCounter + 2][1:]) > 0:
                            fileLine = fileLine + (commandTokens[tokenCounter + 2][1:] + " ")
                        else:
                            syntaxOK = False

                        #add first attribute number
                        if commandTokens[tokenCounter + 3][:-1] in varTypes:
                            fileLine = fileLine + (commandTokens[tokenCounter + 3].split(",", 1)[0] + ",    ")
                        elif commandTokens[tokenCounter + 3].split("(", 1)[0] in varTypes:
                            fileLine = fileLine + (commandTokens[tokenCounter + 3].split(",", 1)[0] + ",    ")
                        else:
                            syntaxOK = False

                        #add any amount of in-between attributes
                        while commandTokens[tokenCounter + i + 2][-1] != ')':
                            fileLine = fileLine + (commandTokens[tokenCounter + i+1] + " ")
                            if commandTokens[tokenCounter + i][:-1] in varTypes:
                                fileLine = fileLine + (commandTokens[tokenCounter + i+2].split(",", 1)[0] + ",    ")
                            elif commandTokens[tokenCounter + i].split("(", 1)[0] in varTypes:
                                fileLine = fileLine + (commandTokens[tokenCounter + i+2].split(",", 1)[0] + ",    ")
                            else:
                                syntaxOK = False
                                break
                            i += 2 

                        #add last attribute
                        fileLine = fileLine + (commandTokens[tokenCounter + i+1] + " ")
                        if commandTokens[tokenCounter + i][:-1] in varTypes:
                            fileLine = fileLine + (commandTokens[tokenCounter + i+2].split(",", 1)[0][:-1])
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
                        f.write(fileLine)
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

#select function handles all action required by the 'select' keyword
def select(commandTokens):
    global tokenCounter

    #select all from specified file 
    if commandTokens[tokenCounter] == '*' and commandTokens[tokenCounter + 1].lower() == "from":
        fn = concat(commandTokens[tokenCounter + 2], ".txt")
        filepath = os.path.join(cwd, currDB)
        filepath = os.path.join(filepath, fn)

        #check if file exists in current database
        if (os.path.exists(filepath)):
            f = open(filepath, "r")
            #formats each line taken from file then outputs
            for x in f:
                fullLine = x.split(",   ")
                for t in fullLine[:-1]:
                    print(t, end = ' | ')
                print(fullLine[-1])
        else:
            print("!Cannot select from '" + commandTokens[tokenCounter + 2] + "' because it does not exist.")
    else:
        print("!Cannot select from table due to syntax error.")

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
    keywords = ["create", "drop", "select", "alter", "use"]

    #associate keywords with functions to be automatically called when parsed
    key_commands = {'create':create, 'drop':drop, 'select':select, 'alter':alter, 'use':use}

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
