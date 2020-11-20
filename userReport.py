

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