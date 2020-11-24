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
from functools import partial

DATABASE_NAME = "291db"
COLLECTION_NAMES = {
    "tags": "Tags.json",
    "posts": "Posts.json",
    "votes": "Votes.json"
}
ERROR_MESSAGE = "Invalid option. Try again..."
NUM_PROCESSES = 8

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

def indexTerms(db):
    startTime = time.time()
    db["posts"].create_index("terms", name = "termsIndexRegular")
    print ("Time to index 'terms': " + str(((time.time() - startTime)))) 

def indexText(db):
    startTime = time.time()
    print ("Beginning text indexing... (background)")
    db["posts"].create_index([("Title", pymongo.TEXT), ("Body", pymongo.TEXT), ("Tags", pymongo.TEXT)], name = "textIndex")
    print("Successfully created text index (" + str(time.time()-startTime) + " sec)")
    

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]
        
def fastBSON(item):
    return RawBSONDocument(bsonjs.loads(orjson.dumps(item)))
        
def extractWords(row, keyName):
    text = row[keyName].lower()
    words = re.findall("[\w']{3,}", text)
    return words    

def buildTerms(row):
    words = extractWords(row, "Body")
    if "Title" in row:
        words += extractWords(row, "Title")
    if "Tags" in row:
        words += extractWords(row, "Tags")
    wordSet = list(set(words))
    row["terms"] = wordSet
    return row
    #print(row["terms"])

# creates a collection in db called colName and inserts data from filename
def createCollection(colName, db):
    client = pymongo.MongoClient('localhost', 12345, document_class=RawBSONDocument)
    db = client[DATABASE_NAME]
    filename = COLLECTION_NAMES[colName]
    print("===============")
    time1 = time.time()
    collection = db[colName]
    with open(filename, 'rt') as file:
        #data is a list
        #print(file.read())
        data = orjson.loads(file.read())[colName]["row"]
    time2 = time.time()
    print("Time to load " + filename + ": " + str(time2 - time1))
    count = len(data)
    chunkSize = int (count / (NUM_PROCESSES * 2))
    if (colName == "posts"):
        time4 = time.time()
        pool = multiprocessing.Pool(processes=NUM_PROCESSES)
        data = list(pool.imap_unordered(buildTerms,data,chunksize=chunkSize))  #creates chunks of 1000 document id's
        pool.close()
        #print(data)
        print("Time to add 'terms': " + str(time.time() - time4))
    pool = multiprocessing.Pool(processes=NUM_PROCESSES) #spawn 8 processes
    bsonData = pool.imap_unordered(fastBSON,data,chunksize=chunkSize)  #creates chunks of 1000 document id's
    pool.close()
    bsonData = list(bsonData)
    # for item in data:
    #     bsonData.append(fastBSON(item))
    #print(bsonData)
    time3 = time.time()
    print("Time to convert '" + colName + "': " + str(time3-time2))
    if isinstance(data, list):
        collection.insert_many(bsonData)
    else:
        collection.insert_one(bsonData)
    print("Time to insert '" + colName + "': " + str(time.time() - time3))
    if (colName == "posts"):
        threading.Thread(target=indexTerms, args=(db,)).start()

    print("DONE!!!!" + colName)
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
    
    # multiprocessing approach - does not work becasue "AssertionError: daemonic processes are not allowed to have children"
    # pool = multiprocessing.Pool(processes=8)
    # pool.map(createCollection, ["votes", "tags"])
    # pool.close()

    # threading approach - slower than sequential (idk why)
    # threading.Thread(target=createCollection, args=("posts",)).start()
    # for colName in ["votes", "tags"]:
    #     threading.Thread(target=createCollection, args=(colName,)).start()

    # sequential approach - fastest
    createCollection("posts")
    for colName in ["votes", "tags"]:
        createCollection(colName, db)

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
        startTime = time.time()
        # connecting to server
        client = pymongo.MongoClient('localhost', port, document_class=RawBSONDocument)
        # TODO: uncomment this
        resetDB(client)
        db = client[DATABASE_NAME]
        #createIndexAggregate("posts", db)
        #threading.Thread(target=indexText, args=(db,)).start()
        wait = input(">> ")
        print("TIME: " + str(time.time() - startTime))
        print(db)
        # TODO: create index
        #mainMenu(db)
        

