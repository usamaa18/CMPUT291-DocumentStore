import json
import sys
import pymongo
from userReport import *

DATABASE_NAME = "291db"
COLLECTION_NAMES = {
    "tags": "Tags.json",
    "posts": "Posts.json",
    "votes": "Votes.json"
}

def mainMenu(db):
    # TODO
    userID = input("User ID (optional): ").strip().lower()
    if userID != '':
        printUserReport(userID, db)
    pass


# creates a collection in db called colName and inserts data from filename
def createCollection(colName, filename, db):
    collection = db[colName]
    with open(filename) as file:
        data = json.load(file)[colName]["row"]
    if isinstance(data, list):
        collection.insert_many(data)
    else:
        collection.insert_one(data)
    return collection


# delete existing db and create new one. Fill db with collections using json files
def  resetDB(client):
    print("Resetting " + DATABASE_NAME + " database...")

    # deleting pre-existing db
    if DATABASE_NAME in client.list_database_names():
        client.drop_database(DATABASE_NAME)
    db = client[DATABASE_NAME]

    # build datbase using json files
    for colName, filename in COLLECTION_NAMES.items():
        createCollection(colName, filename, db)


if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print("INCORRECT USAGE")
        print("CORRECT USAGE: python main.py <port-no>")
    else:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Oops!  That was no valid port number.  Try again...")
            exit()

        # TODO: remove this
        port = 12345

        # connecting to server
        client = pymongo.MongoClient('localhost', port)
        # TODO: uncomment this
        # resetDB(client)
        db = client[DATABASE_NAME]

        print(db)
        # TODO: create index
        mainMenu(db)
        

