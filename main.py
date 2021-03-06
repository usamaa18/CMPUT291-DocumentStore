import re
import sys
import time
import threading
import multiprocessing

import pymongo

# orjson is used to convert json file to dict
import orjson
# bsonjs boasts faster JSON<->BSON encoding and decoding times than those built-in pymongo
import bsonjs

from bson.raw_bson import RawBSONDocument

from userReport import *
from menuFunctions import *



DATABASE_NAME = "291db"
COLLECTION_NAMES = {
    "tags": "Tags.json",
    "posts": "Posts.json",
    "votes": "Votes.json"
}
NUM_PROCESSES = 8
PROCESS_MULTIPLIER = 2

# display the main menu
def mainMenu(db):
    # userID is optional
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
            postQuestionMenu(userID, db)
            needPrintMenu = True
        elif (val == 2):
            searchQuestionsMenu(userID, db)
            needPrintMenu = True
        elif (val == 0):
            break
        else:
            print(ERROR_MESSAGE)
            continue

# generateID() should be called when the program initializes
# because it takes 2-3 seconds on large collections (~1.5 mil documents)
def initGenerateID(db):
    for colName in COLLECTION_NAMES.keys():
        generateID(db[colName])

# creates an index of 'terms'
def indexTerms(db):
    startTime = time.time()
    print ("Beginning 'terms' indexing...")
    db["posts"].create_index("terms", name = "termsIndexRegular")
    print("Successfully created 'terms' index (" + str(time.time()-startTime) + " sec)")

# creates an text index of 'Title', 'Body', 'Tags' fields
# only exists to search of keywords less than 2 chars in length
def indexText(db):
    startTime = time.time()
    print ("Beginning text indexing... (background)")
    db["posts"].create_index([("Title", pymongo.TEXT), ("Body", pymongo.TEXT), ("Tags", pymongo.TEXT)], name = "textIndex")
    print("Successfully created text index (" + str(time.time()-startTime) + " sec)")

# encode a python dict -> JSON -> BSON -> RawBSONDocument
def fastBSON(item):
    return RawBSONDocument(bsonjs.loads(orjson.dumps(item)))
        
# find words where len(word) >= 3 
def extractWords(row, keyName):
    text = row[keyName].lower()
    words = re.findall("[\w']{3,}", text)
    return words    

# creates a set of words >= 3 chars that occur in the 'Body', 'Title' and 'Tags' field of any post
def buildTerms(row):
    words = extractWords(row, "Body")
    if "Title" in row:
        words += extractWords(row, "Title")
    if "Tags" in row:
        words += extractWords(row, "Tags")
    wordSet = list(set(words))
    row["terms"] = wordSet
    return row

# creates a collection in db called colName and inserts data from filename
def createCollection(colName, db):
    print("===============")
    time1 = time.time()

    filename = COLLECTION_NAMES[colName]
    collection = db[colName]
    with open(filename, 'rt') as file:
        data = orjson.loads(file.read())[colName]["row"]

    time2 = time.time()
    print("Time to load " + filename + ": " + str(time2 - time1))
    # chunksize determine how many chunks the list should be divided into for multiprocessing
    chunkSize = int (len(data) / (NUM_PROCESSES * PROCESS_MULTIPLIER))
    if (colName == "posts"):
        time4 = time.time()

        # use multiple processing cores to add 'terms' field in every post
        pool = multiprocessing.Pool(processes=NUM_PROCESSES)
        data = list(pool.imap_unordered(buildTerms,data,chunksize=chunkSize))
        pool.close()

        print("Time to add 'terms': " + str(time.time() - time4))
    
    # encode this to RawBSONDocument to feed into database faster
    pool = multiprocessing.Pool(processes=NUM_PROCESSES)
    bsonData = list(pool.imap_unordered(fastBSON,data,chunksize=chunkSize))
    pool.close()

    time3 = time.time()
    print("Time to convert '" + colName + "': " + str(time3-time2))

    if isinstance(data, list):
        collection.insert_many(bsonData)
    else:
        collection.insert_one(bsonData)

    print("Time to insert '" + colName + "': " + str(time.time() - time3))       
    print("DONE WITH " + colName)
    return collection

# delete existing db and create new one. Fill db with collections using json files
def resetDB(ip, port):
    client = pymongo.MongoClient(ip, port, document_class=RawBSONDocument)
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

    # sequentially create collections - fastest approach
    createCollection("posts", db)
    threadIndexTerms = threading.Thread(target=indexTerms, args=(db,))
    threadIndexTerms.start()
    for colName in ["votes", "tags"]:
        createCollection(colName, db)

    endTime = time.time()
    timeTaken = endTime - startTime
    print("Sucessfully reset (" + str(timeTaken) + " seconds)")
    threadIndexTerms.join()


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

        startTime = time.time()

        resetDB('localhost', port)
        
        # connecting to server
        client = pymongo.MongoClient('localhost', port)
        db = client[DATABASE_NAME]
        print("PHASE 1 TIME: " + str(time.time() - startTime))
        threading.Thread(target=indexText, args=(db,)).start()
        threading.Thread(target=initGenerateID, args=(db,)).start()

        mainMenu(db)
        

