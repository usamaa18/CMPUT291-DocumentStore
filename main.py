import re
import sys
import time
import pymongo
import threading
import multiprocessing
from userReport import *
from menuFunctions import *
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
NUM_PROCESSES = 8
PROCESS_MULTIPLIER = 2

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
            postQuestion(title, body, tags, userID, db)
            needPrintMenu = True
        elif (val == 2):
            print("Enter keywords to search:")
            keywords = input("> ").strip().lower()
            while keywords == '':
                keywords = input("> ").strip().lower()
            keywords = keywords.split()
            res = searchQuestions(keywords, db)
            if len(res) > 0:
                displayPosts(res, "1", db)
                postSearchActions(res, userID, db)
            else:
                print("No matching posts")
            needPrintMenu = True

        elif (val == 0):
            break
        else:
            print(ERROR_MESSAGE)
            continue

def indexTerms(db):
    startTime = time.time()
    db["posts"].create_index("terms", name = "termsIndexRegular")
    print ("Time to index 'terms': " + str(((time.time() - startTime)))) 

def indexText(db):
    startTime = time.time()
    print ("Beginning text indexing... (background)")
    db["posts"].create_index([("Title", pymongo.TEXT), ("Body", pymongo.TEXT), ("Tags", pymongo.TEXT)], name = "textIndex")
    print("Successfully created text index (" + str(time.time()-startTime) + " sec)")
        
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

    chunkSize = int (len(data) / (NUM_PROCESSES * PROCESS_MULTIPLIER))
    if (colName == "posts"):
        time4 = time.time()

        pool = multiprocessing.Pool(processes=NUM_PROCESSES)
        data = list(pool.imap_unordered(buildTerms,data,chunksize=chunkSize))
        pool.close()

        print("Time to add 'terms': " + str(time.time() - time4))
    
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

    # sequential approach - fastest
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

        # TODO: remove this
        #port = 12345
        startTime = time.time()

        # TODO: uncomment this
        resetDB('localhost', port)
        
        # connecting to server
        client = pymongo.MongoClient('localhost', port)
        db = client[DATABASE_NAME]
        threading.Thread(target=indexText, args=(db,)).start()
        print("TIME: " + str(time.time() - startTime))
        print(db)
        # TODO: create index
        mainMenu(db)
        #getAnswers("1",None, db)
        

