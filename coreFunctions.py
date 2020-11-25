from datetime import datetime
from pymongo.errors import OperationFailure 


# return string formatted datetime
def formatDate(date):
    return date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

# generate a unique ID for the collection
def generateID(collection):
    #startTime = time.time()
    colName = collection.name
    # initialize maxID as a dict
    # only runs when the function is called for the first time globally
    if not hasattr(generateID, "maxID"):
        generateID.maxID = dict()
    
    # find maxID from database for a given collection
    # only runs when the func is called for the first time for that collection
    if colName not in generateID.maxID.keys():
        stringIDs = collection.distinct("Id")
        intIDs = [int(ID) for ID in stringIDs]
        generateID.maxID[colName] = max(intIDs)
    
    # increment maxID for that collection
    generateID.maxID[colName] += 1
    #print("New ID: " + str(generateID.maxID[colName]) + " (" + str(time.time()-startTime) + " sec)")
    return str(generateID.maxID[colName])


# increment tag count by 1, or create new tag with unique id
def updateTag(tag, db):
    query = { "TagName": tag }
    if (db.tags.find_one(query) != None):
        update = { "$inc": { "Count": 1 } }
        db.tags.update_one(query, update)
    else:
        newTag = {
            "Id": generateID(db.tags),
            "TagName": tag,
            "Count": 1
        }
        db.tags.insert_one(newTag)
    

# posts a question. Returns 1 if successful, 0 otherwise
def postQuestion(title, body, tags, userID, db):
    if (title == '' or body == ''):
        return False
    newId = generateID(db.posts)
    datatimeString = formatDate(datetime.today())
    post = {
        "Id": newId,
        "PostTypeId": "1",
        "CreationDate": datatimeString,
        "Title": title,
        "Body": "<p>"+body+"</p>",
        "Score": 0,
        "ViewCount": 0,
        "AnswerCount": 0,
        "CommentCount": 0,
        "FavoriteCount": 0,
        "ContentLicense": "CC BY-SA 2.5"
    }
    if (len(tags) > 0):
        tagString = "<" + "><".join(tags) + ">"
        post["Tags"] = tagString
        for tag in tags:
            updateTag(tags, db)
    if (userID != ''):
        post["OwnerUserId"] = userID
    db.posts.insert_one(post)
    return True

# posts an answer to a question. Return 1 if successful, 0 otherwise
def postAnswer(body, questionID, userID, db):
    if (body == ''):
        return False
    newId = generateID(db.posts)
    datatimeString = formatDate(datetime.today())
    post = {
        "Id": newId,
        "PostTypeId": "2",
        "CreationDate": datatimeString,
         "Body": "<p>"+body+"</p>",
        "ParentId": questionID,
        "Score": 0,
        "CommentCount": 0,
        "ContentLicense": "CC BY-SA 2.5"
    }
    if (userID != ''):
        post["OwnerUserId"] = userID
    db.posts.insert_one(post)
    return True

# casts a vote on postID on behalf of userID. Returns 1 if successful, 0 if not
def votePost(postID, userID, db):
    vote = {
        "Id": generateID(db.votes),
        "PostId": postID,
        "VoteTypeId": "2",
        "CreationDate": formatDate(datetime.today())
    }
    if (userID != ''):
        vote["UserId"] = userID
        if (db.votes.find_one({"UserId": userID, "PostId": postID})):
            return 0
    db.votes.insert_one(vote)
    db.posts.update_one( {"Id": postID}, {"$inc": {"Score": 1} } )
    return 1

# searches posts for keywords and list of ObjectIds (_id)
def searchQuestions(keywords, db):
    keywordsLarge = list()
    keywordsSmall = list()
    for word in keywords:
        if len(word) >= 3:
            keywordsLarge.append(word)
        else:
            keywordsSmall.append(word)

    postTypeID = "1"

    filter = {
        "terms": {"$in": keywordsLarge},
        "PostTypeId": postTypeID
    }
    if (len(keywordsSmall) > 0):
        try:
            filter = { 
                "$or": [
                    {"terms": {"$in": keywordsLarge}},
                    { "$text": { "$search": " ".join(keywordsSmall) }}
                ],
                "PostTypeId": postTypeID
            }
        except OperationFailure as f:
            print ("Skipping " + str(keywordsSmall) + " because text index is still building. Please try again later")

    return db.posts.distinct("_id", filter)

# lists all answers to a given question
def getAnswers(questionID, db):
    postType= '2'
    ansCount= db.posts.count_documents({"ParentId": questionID})       
    if ansCount == 0:
        return []
    else:
        ans = []
        check_for_accepted= db.posts.find_one({"$and": [{"Id": questionID}, {"AcceptedAnswerId":{"$exists": True}}]})
        if check_for_accepted == None:
            ans= list(db.posts.find({"ParentId": questionID}))
            
        else:
            accepted_ansID= check_for_accepted["AcceptedAnswerId"]
            accepted_ans= db.posts.find_one({"Id": accepted_ansID})
            ans= [accepted_ans] + list(db.posts.find({"$and":[{"Id": {"$ne": accepted_ansID}},{"ParentId":questionID}]}))
        
        return ans
