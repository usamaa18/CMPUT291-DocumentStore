from datetime import datetime
import random, string
def id_generator(collection):
    _id=''
    chars= string.ascii_lowercase + string.digits
    for i in range(4):
        id+= random.choice(chars)
    ret= collection.find_one({"Id": _id })
    if ret == None:
        return _id
    else:
        id_generator(collection)

    
# posts a question. Returns 1 if successful, 0 otherwise
def postQuestion(title, body, tags, userID, collection,db):
    #Hibaq's Job
    #modifying tags
    tag_str= ''.join('{}'.format(tag) for tag in tags)
    cdate= datetime.now()
    dateFormat= cdate.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
    bodyFormat= "<p>"+ body + "<p>"
    #creating _id
    object_id= id_generator()
    if userID == None:
        question= {"_id": object_id, "PostTypeId": "1", "CreationDate": dateFormat, "Score": 0, "Body": bodyFormat, "Title": title, "Owner": None,"Tags": tag_str, "ViewCount": 0 , "AnswerCount": 0 ,"CommentCount":0, "ContentLiscence": "CC BY-SA 2.5" }
    else:
        #Users can interact with db w/o logging in ?
        question= {"_id": object_id, "PostTypeId": "1", "CreationDate": dateFormat, "Score": 0, "Body": bodyFormat, "Title": title, "Owner": userID ,"Tags": tag_str, "ViewCount": 0 , "AnswerCount": 0 ,"CommentCount":0, "ContentLiscence": "CC BY-SA 2.5" }
    collection.insert_one(question)
    return 1





# posts an answer to a question. Return 1 if successful, 0 otherwise
def postAnswer(body, questionID, userID, db):
    #Hibaq's Job
    # TODO
    pass

# casts a vote on postID on behalf of userID. Returns 1 if successful, 0 if not
def votePost(postID, userID, db):
    # TODO
    pass

# searches posts for keywords and return cursor object
def searchQuestions(keywords, userID, db):
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


    # 3. vote for question
    votePost(questionID, userID, db)