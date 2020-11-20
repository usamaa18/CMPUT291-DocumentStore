import json
import sys
import pymongo

DATABASE_NAME = "291db"
COLLECTION_NAMES = {
    "tags": "Tags.json",
    "posts": "Posts.json",
    "votes": "Votes.json"
}

def getQuestionsRep(userID, db):
    pipeline = [ 
        {"$match": {"PostTypeId": "1", "Id": userID} },
        {"$group" : {"_id": {"UserID": "$Id"}, "NumQuestions": {"$sum": 1}, "AvgScore": {"$avg": "$Score"} } } 
    ]
    return db.posts.aggregate(pipeline)

def getAnswersRep(userID, db):
    pipeline = [ 
        {"$match": {"PostTypeId": "2", "Id": userID} },
        {"$group" : {"_id": {"UserID": "$Id"}, "NumAnswers": {"$sum": 1}, "AvgScore": {"$avg": "$Score"} } } 
    ]
    return db.posts.aggregate(pipeline)

def getVotesRep(userID, db):
    pipeline = [ 
        {"$match": {"Id": userID} },
        {"$group" : {"_id": {"UserID": "$Id"}, "NumVotes": {"$sum": "$Score"}} } 
    ]
    return db.posts.aggregate(pipeline)

# check if userID exists in posts, tags, and votes collections
def userExists(userID, db):
    query = {"Id": userID}
    for x in ([db.posts.find_one(query)] + [db.tags.find_one(query)] + [db.votes.find_one(query)]):
        if x is not None:
            return True
    return False

# print analytic info about all posts made by userID
def printUserReport(userID, db):
    if (not userExists(userID, db)):
        print("User ID '" + userID + "' not found!")
        return
    questionsRep = getQuestionsRep(userID, db)
    answersRep = getAnswersRep(userID, db)
    votesRep = getVotesRep(userID, db)
    print(list(questionsRep))
    print(list(answersRep))
    print(list(votesRep))

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
        

