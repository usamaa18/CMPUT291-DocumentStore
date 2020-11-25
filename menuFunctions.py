import math
from tabulate import tabulate
from pprint import pprint
from coreFunctions import *
                
ERROR_MESSAGE = "Invalid option. Try again..."

# users prompts to search for a question
def searchQuestionsMenu(userID, db):
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

# user prompts to post a new question
def postQuestionMenu(userID, db):
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
    if postQuestion(title, body, tags, userID, db):
        print("Successfully posted!")               

# generic page-scrolling handler for both question and answer type posts
def displayPosts(postIDs,PostType, db):
    currPage = 1
    maxPerPage = 10
    lenDocuments= len(postIDs)
    numPages = math.ceil(float(lenDocuments)/ maxPerPage)
    updatePage = True
   

    while True:
        # these values are used to index sortedPID to display only 'maxPerPage' elements at a time
        currMaxIndex = currPage * maxPerPage
        currMinIndex = currMaxIndex - maxPerPage
        if (currMaxIndex > lenDocuments):
            currMaxIndex = lenDocuments
        
        # only need to update if page was changed
        if updatePage:
            posts = db.posts.find({"_id": {"$in": postIDs[currMinIndex:currMaxIndex]}})
            if PostType == '1':
                printQuestions(posts)
            else:
                printAnswers(posts)
            
            print("Page " + str(currPage) + " of " + str(numPages))
            updatePage = False

        # condition checking to ensure user cannot go out of bound of pages
        if (numPages == 1):
            inputPrompt = "Select post (s): "
        elif (currPage == 1):
            inputPrompt = "Go to next page (n), or select post (s): "
        elif (currPage == numPages):
            inputPrompt = "Go to previous page (p), or select post (s): "
        else:
            inputPrompt = "Go to previous page (p) or next page (n), or select post (s): "
         
        # handle user input
        user_input = input(inputPrompt).strip().lower()
        if user_input == 'p' and currPage > 1:
            currPage -= 1
            updatePage = True
        elif user_input == 'n' and currPage < numPages:
            currPage += 1
            updatePage = True
        elif user_input == 's':
            updatePage = False
            break
        else:
            print("Invalid selection")


# format search query results in a user-friendly way
def printQuestions(posts):
    #printing posts using tabulate
    questionColumns = ["Id", "Title", "CreationDate", "Score", "AnswerCount" ]
    table= []
    filler= "N/A"
    for post in posts:
        subtable=[]
        Id= post["Id"]
        cdate= post["CreationDate"]
        score= post["Score"]
        if post["PostTypeId"] == "1":
            title= post["Title"]
            answerCount= post["AnswerCount"]
            subtable.extend((Id,title,cdate,score,answerCount))
            table.append(subtable)
        else:
            subtable.extend((Id,filler,cdate,score,filler))
            table.append(subtable)
       
    print(tabulate(table, headers = questionColumns))
        

# format answer list in a user-friendly way
def printAnswers(answers):
    #printing answers using tabulate
    table= []
    max_count = 80
    column_names= ["AnswerId","Body", "CreationDate", "Score"]
            
    for answer in answers:
        subtable2=[]
        # 'isAcceptedAns' is a attribute added by the getAnswers() func
        if "isAcceptedAns" in answer.keys():
            ans_id= '☆ '+ answer["Id"]
        
        else:
            ans_id= answer["Id"]
        
        body= answer["Body"]
        cdate= answer["CreationDate"]
        score= answer["Score"]
        
        if len(body) > max_count:
            subtable2.extend((ans_id,body[0:max_count -1 ],cdate,score))
            table.append(subtable2)
        else:
            subtable2.extend((ans_id,body,cdate,score))
            table.append(subtable2)

    print(tabulate(table, headers = column_names))


# prints selected question in pretty dictionary style
# returns None if the user input doesnt match id in questions from question search
def selectQuestion(postIDs, db):
    # generating this list is a bit slow
    # takes a few seconds
    # list of all question id's in keyword search
    qid_list = db.posts.distinct("Id", {"_id": {"$in": postIDs}})
    print("Select a question (ID)")
    questionID = input("> ").strip()
    # question = db.posts.find_one({"Id":questionID})
    question = None
    if questionID in qid_list:
        question = db.posts.find_one({"Id": questionID})
        pprint(question)          
    else:
        print("The questionID given does not correspond to any posts listed in the search results.")
    
    return question 




# prints selected answer in pretty dictionary form
# returns None if user inputs a value that doesn't correspond to an answer
# needs more stringent error correction imo
def selectAnswer(questionID, db):
    print("Select a answer (AnswerID)")
    answerID = input("> ").strip()
    selectAnswer= db.posts.find_one({"$and":[{"Id": answerID},{"ParentId":questionID}]})
    if selectAnswer != None:
        for keys in selectAnswer.keys(): 
            print ('{', keys, ":" , selectAnswer[keys] , '}' )
    else:
        print("The answerID selected doesn't correspond with the selected question. Please try again.")
        return None
    return answerID

# menu for user-actions after choosing to select a question from search results
def postSearchActions(res, userID, db):
    
    # prompt user to select a question
    question = selectQuestion(res, db)
    if question == None:
        return

    questionID = question["Id"]

    needPrintMenu = True
    while True:
        if needPrintMenu:
            print( '''
                QUESTION ACTION MENU
            1. Answer
            2. List answers
            3. Vote
            0. Main menu
            ''')
            needPrintMenu = False
        try:
            val = int(input("> "))
        except ValueError:
            print(ERROR_MESSAGE)
            continue
        
        # 1. post answer
        if (val == 1):
            print("Enter body:")
            body = input("> ").strip()
            while body == '':
                body = input("> ").strip()
            if (postAnswer(body, questionID, userID, db)):
                print("Successfully posted")
            else:
                print("Error: Answer not posted")
            needPrintMenu = True

        # 2. list answers
        elif (val == 2 ):
        
            ans = getAnswers(questionID, db)
            if len(ans) == 0:
                print("The question you've selected currently has no answers.")
                return

            # this process is very inefficient, but it is what it is
            ans = [row["_id"] for row in ans]
            displayPosts(ans, "2", db)
            answerID = selectAnswer(questionID, db)

            if answerID !=None:
                print("Do you wish to vote for this answer? (y/n)")
                val = input("> ").lower().strip()
                while val not in ['y', 'n']:
                    print(ERROR_MESSAGE)
                    val = input("> ").lower().strip()
                if (val == 'y'):
                    if (votePost(answerID, userID, db)):
                        print("Successfully voted")
                    else:
                        print("You have already voted this post!")

            needPrintMenu = True

        # vote for question    
        elif (val == 3):
            if (votePost(questionID, userID, db)):
                print("Successfully voted")
            else:
                print("You have already voted this post!")
        # exit        
        elif (val == 0):
            break
        else:
            print(ERROR_MESSAGE)