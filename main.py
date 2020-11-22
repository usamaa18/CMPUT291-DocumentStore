import json
import sys
import time
import pymongo
from userReport import *
from menuFunctions import *

DATABASE_NAME = "291db"
COLLECTION_NAMES = {
    "tags": "Tags.json",
    "posts": "Posts.json",
    "votes": "Votes.json"
}
ERROR_MESSAGE = "Invalid option. Try again..."

def mainMenu(db):
    # TODO
    userID = input("User ID (optional): ").strip().lower()
    if userID != '':
        printUserReport(userID, db)

    needPrintMenu = True
    while True:
        if needPrintMenu:
            print('''
                MAIN MENU
            1. Post a question
            2. Search for questions
            0. Exit
            ''')
            needPrintMenu = False
        try:
            val = int(input("> "))
        except ValueError:
            print(ERROR_MESSAGE)
            continue
        if (val == 1):
            print("Enter title:")
            title = input("> ").strip()
            while title == '':
                title = input("> ").strip()
            print("Enter body:")
            body = input("> ").strip()
            while body == '':
                body = input("> ").strip()
            print("Enter tags (optional):")
            tags = input("> ").strip().lower().split()
            print(tags)
            postQuestion(title, body, tags, userID, db)
            needPrintMenu = True
        elif (val == 2):
            print("Enter keywords to search:")
            keywords = input("> ").strip().split()
            res = searchQuestions(keywords, userID, db)
            printQuestions(res)
            postSearchActions(res, userID, db)
        elif (val == 0):
            break
        else:
            print(ERROR_MESSAGE)
            continue

def createIndexAggregate(colName, db):
    startTime = time.time()
    db[colName].update_many(
        {},
        [{
            "$set": {
                "terms": {
                    "$setDifference": [{
                        "$map": {
                            "input": {
                                "$regexFindAll": {
                                    "input": {
                                        "$toLower": {
                                            "$concat": ["$Body", "$Title", "$Tags"]
                                        }
                                    },
                                    "regex": "[\w']{3,}"
                                }
                            },
                            "in": "$$this.match"
                        }, 
                    }, 
                    [] ]
                }
            }
        }]
    )
    print ("AggregateRegexTime: " + str(((time.time()-startTime))))

        
# creates a collection in db called colName and inserts data from filename
def createCollection(colName, filename, db):
    collection = db[colName]
    with open(filename) as file:
        #data is a list
        data = json.load(file)[colName]["row"]
    if isinstance(data, list):
        collection.insert_many(data)
    else:
        collection.insert_one(data)
    return collection


# delete existing db and create new one. Fill db with collections using json files
def resetDB(client):
    print("Resetting " + DATABASE_NAME + " database...")
    startTime = time.time()
    # deleting pre-existing db
    if DATABASE_NAME in client.list_database_names():
        client.drop_database(DATABASE_NAME)
    db = client[DATABASE_NAME]

    # build datbase using json files
    for colName, filename in COLLECTION_NAMES.items():
        createCollection(colName, filename, db)
    timeTaken = time.time() - startTime
    print("Sucessfully reset (" + str(timeTaken) + " seconds)")

    


if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print("INCORRECT USAGE")
        print("CORRECT USAGE: python main.py <port-no>")
    else:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number.  Try again...")
            exit()

        # TODO: remove this
        port = 12345

        # connecting to server
        client = pymongo.MongoClient('localhost', port)
        # TODO: uncomment this
        resetDB(client)
        db = client[DATABASE_NAME]
        createIndexAggregate("posts", db)

        print(db)
        # TODO: create index
        mainMenu(db)
        

