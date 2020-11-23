from datetime import datetime
import random, string
from pymongo.errors import OperationFailure 
   

# return string formatted datetime
def formatDate(date):
    return date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

# generate a unique ID for the collection
def generateID(collection):
    return 1 # temporary
    _id=''
    chars= string.ascii_lowercase + string.digits
    for i in range(4):
        id+= random.choice(chars)
    ret= collection.find_one({"Id": _id })
    if ret == None:
        return _id
    else:
        generateID(collection)

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
    id = db.posts.insert_one(post)
    print(id)

# posts an answer to a question. Return 1 if successful, 0 otherwise
def postAnswer(body, questionID, userID, db):
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

# searches posts for keywords and return cursor object
def searchQuestions(keywords, userID, db):
    count = 0
    keywordsLarge = list()
    keywordsSmall = list()
    for word in keywords:
        if len(word) >= 3:
            keywordsLarge.append(word)
        else:
            keywordsSmall.append(word)
    print(keywordsLarge)
    count += db.posts.count_documents({"terms": {"$in": keywordsLarge}})
    print(count)
    

    if (len(keywordsSmall) > 0):
        try:
            count += db.posts.count_documents({ "$text": { "$search": " ".join(keywords) } })
        except OperationFailure as f:
            print ("Skipping " + str(keywordsSmall) + " because text index is still building. Please try again later")
    print(count)
    # TODO 
    pass

# lists all answers to a given question
def getAnswers(questionID, userID, db):
    #Hibaq's Job
    # TODO  

    pass


# format search query results in a user-friendly way
def printQuestions(res):
    pass

# format answer list in a user-friendly way
def printAnswers(ans):
    pass

# allows user to select a post from list. then shows details about post. then shows post-search menu
def postSearchActions(res, userID, db):

    # get user input for questionID
    print("Select a question (questionID)")
    questionID = input("> ")

    # get user input for post-search action

    # 1. post answer
    # get user input for body
    print("Enter body:")
    body = input("> ").strip()
    if (postAnswer(body, questionID, userID, db)):
        print("Successfully posted")
    else:
        print("Error: Answer not posted")

    # 2. List answers
    ans = getAnswers(questionID, userID, db)
    printAnswers(ans)
    # get user input for answerID
    print("Select a answer (answerID)")
    answerID = input("> ")

    # display details

    # ask if they want to vote for the answer
    wantToVote = True
    if (wantToVote):
        if (votePost(answerID, userID, db)):
            print("Successfully voted")
        else:
            print("Error: " + userID + " already voted for this post")


    # 3. vote for question
    if (votePost(questionID, userID, db)):
        print("Successfully voted")
    else:
        print("Error: " + userID + " already voted for this post")