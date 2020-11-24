import json
import re
import sys
import time
import pymongo
import threading
from pprint import pprint
from userReport import *
from menuFunctions import *
import multiprocessing
import orjson
import bsonjs
from bson.raw_bson import RawBSONDocument

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
            keywords = input("> ").strip().lower().split()
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
    endTime = time.time()
    print ("Time to insert 'terms': " + str(((endTime-startTime))))
    db["posts"].create_index("terms", name = "termsIndexRegular")
    print ("Time to index 'terms': " + str(((time.time() - endTime)))) 

def indexText(placeholder):
    startTime = time.time()
    print ("Beginning text indexing... (background)")
    db["posts"].create_index([("Title", pymongo.TEXT), ("Body", pymongo.TEXT), ("Tags", pymongo.TEXT)], name = "textIndex", background=True)
    print("Successfully created text index (" + str(time.time()-startTime) + " sec)")
    

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]
        
def fastBSON(item):
    return RawBSONDocument(bsonjs.loads(orjson.dumps(item)))
        
# creates a collection in db called colName and inserts data from filename
def createCollection(colName, filename, db):
    print("===============")
    time1 = time.time()
    collection = db[colName]
    with open(filename, 'rt') as file:
        #data is a list
        #print(file.read())
        data = orjson.loads(file.read())[colName]["row"]
    time2 = time.time()
    print("Time to load file: " + str(time2 - time1))
    count = len(data)
    numProc = 8
    multiple = 1
    chunkSize = int (count / (numProc * 2))
    print(count)
    print(chunkSize)
    pool = multiprocessing.Pool(processes=numProc) #spawn 8 processes
    bsonData = pool.imap_unordered(fastBSON,data,chunksize=chunkSize)  #creates chunks of 1000 document id's
    pool.close()
    bsonData = list(bsonData)
    # for item in data:
    #     bsonData.append(fastBSON(item))
    #print(bsonData)
    time3 = time.time()
    print("Time to load: " + str(time3-time2))
    if isinstance(data, list):
        collection.insert_many(bsonData)
    else:
        collection.insert_one(bsonData)
    print("Time to insert: " + str(time.time() - time3))
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
    endTime = time.time()
    timeTaken = endTime - startTime
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
        client = pymongo.MongoClient('localhost', port, document_class=RawBSONDocument)
        # TODO: uncomment this
        resetDB(client)
        db = client[DATABASE_NAME]
        #createIndexAggregate("posts", db)
        #threading.Thread(target=indexText, args=(None,)).start()

        print(db)
        # TODO: create index
        mainMenu(db)
        

