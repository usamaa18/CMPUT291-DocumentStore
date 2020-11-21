
# posts a question. Returns 1 if successful, 0 otherwise
def postQuestion(title, body, tags, userID, db):
    pass

# posts an answer to a question. Return 1 if successful, 0 otherwise
def postAnswer(body, questionID, userID, db):
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