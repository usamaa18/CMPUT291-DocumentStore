from datetime import datetime
import random, string
from pymongo.errors import OperationFailure 
from tabulate import tabulate
import math
# return string formatted datetime
def formatDate(date):

    return date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

# generate a unique ID for the collection
def generateID(collection):
    #Haven't tested this yet, I hope its not too slow
    max_Id= collection.find().sort({"Id":-1}).limit(1)
    Id= max_Id + 1

    return Id


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
<<<<<<< HEAD
=======
    postType= '1'
    count = 0
>>>>>>> 6208ac45226d6a5320eb2d1aa07759fa263404a7
    keywordsLarge = list()
    keywordsSmall = list()
    res= None
    for word in keywords:
        if len(word) >= 3:
            keywordsLarge.append(word)
        else:
            keywordsSmall.append(word)
<<<<<<< HEAD

    projection = ["Id"]
=======
    print(keywordsLarge)
    count += db.posts.count_documents({"terms": {"$in": keywordsLarge}})
    print(count)
    if count != 0:
        res = list(db.posts.find({"terms": {"$in": keywordsLarge}}))


        
>>>>>>> 6208ac45226d6a5320eb2d1aa07759fa263404a7

    query = {"terms": {"$in": keywordsLarge}}
    if (len(keywordsSmall) > 0):
        try:
            query = { 
                "$or": [
                    {"terms": {"$in": keywordsLarge}},
                    { "$text": { "$search": " ".join(keywordsSmall) }}
                ]
            }
        except OperationFailure as f:
            print ("Skipping " + str(keywordsSmall) + " because text index is still building. Please try again later")
<<<<<<< HEAD

    return list (db.posts.find(query, projection))
=======
            print(count)

    return res
>>>>>>> 6208ac45226d6a5320eb2d1aa07759fa263404a7

# lists all answers to a given question
def getAnswers(questionID, userID, db):
    postType= '2'
    ansCount= db.posts.count_documents({"ParentId": questionID})       
    if ansCount == 0:
        print("The question you've selected currently has no answers.")
    else:
        check_for_accepted= db.posts.find_one({"$and": [{"Id": questionID}, {"AcceptedAnswerId":{"$exists": True}}]})
        if check_for_accepted == None:
            ans= list(db.posts.find({"ParentId": questionID}))
            
            displayPosts(ans,postType)
        else:
            accepted_ansID= check_for_accepted["AcceptedAnswerId"]
            accepted_ans= db.posts.find_one({"Id": accepted_ansID})
            ans= [accepted_ans] + list(db.posts.find({"$and":[{"Id": {"$ne": accepted_ansID}},{"ParentId":questionID}]}))
            displayPosts(ans,postType)

                
                

def displayPosts(res,PostType):
    currPage = 1
    maxPerPage = 10
    lenDocuments= len(res)
    numPages = math.ceil(float(lenDocuments)/ maxPerPage)
    updatePage = True
   

    while True:
        currMaxIndex = currPage * maxPerPage
        currMinIndex = currMaxIndex - maxPerPage
        if (currMaxIndex > lenDocuments):

            currMaxIndex = lenDocuments
        
        if updatePage:
            if PostType == '1':
                printQuestions(res[currMinIndex:currMaxIndex])
            else:
                printAnswers(res[currMinIndex:currMaxIndex])
            
            print("Page " + str(currPage) + " of " + str(numPages))
            updatePage = False
        if (currPage == 1):
            inputPrompt = "Go to next page (n), or select post (s): "
        elif (currPage == numPages):
            inputPrompt = "Go to previous page (p), or select post (s): "
        else:
            inputPrompt = "Go to previous page (p) or next page (n), or select post (s): "
         
        
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
    postTable =[]
    questionColumns = ["Id", "Title", "CreationDate", "Score", "AnswerCount" ]
    answerColumns= ["Id", "Title", "CreationDate", "Score"]
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
        if answer == answers[0]:
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
#prints selected question in pretty dictionary style
#returns None if the user input doesnt match id in questions from question search
def selectQuestion(db,res):
    #generating this list is a bit slow
    #takes a few seconds
    #list of all question id's in keyword search
    qid_list = []
    for post in res:
        if post["PostTypeId"] == "1":
             qid_list.append(post["Id"])
    print("Select a question (ID)")
    questionID = input("> ").strip()
    question = db.posts.find_one({"Id":questionID})
    if question != None and  question["Id"] in qid_list:
        for keys in question.keys(): 
            print ('{', keys, ":" , question[keys] , '}' )
            
    else:
        print("The questionID given does not correspond to any posts listed in the search results.")
        return None
    
    return question["Id"]  




#prints selected answer in pretty dictionary form
# returns None if user inputs a value that doesn't correspond to an answer
#needs more stringent error correction imo
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


def postSearchActions(res, userID, db):
    
    
    ERROR_MESSAGE = "Invalid option. Try again..."
    questionID= selectQuestion(db,res)
    if questionID == None:
        return

    # get user input for post-search action

    # 1. post answer
    # get user input for body
    print( '''
               USER ACTIONS
            1. Post a answer
            2. Print list the selected questions answers."
            ''')
    try:
         val = int(input("> "))
    except ValueError:
         print(ERROR_MESSAGE)
    if (val == 1):
         print("Enter body:")
         body = input("> ").strip()
         if (postAnswer(body, questionID, userID, db)):
             print("Successfully posted")
    elif (val == 2 ):
         getAnswers(questionID, userID, db)
         ans= selectAnswer(questionID, db)
        if ans == None:
        else:
            #wantToVote = True
            #if (wantToVote):
            # if (votePost(answerID, userID, db)):
            # print("Successfully voted")
            break
    else:
        print(ERROR_MESSAGE)
    #print("Enter body:")
    #body = input("> ").strip()
    #if (postAnswer(body, questionID, userID, db)):
       # print("Successfully posted")
   # else:
       # print("Error: Answer not posted")

    # 2. List answers
    #ans = getAnswers(questionID, userID, db)
    #printAnswers(ans)
    # get user input for answerID
    #print("Select a answer (answerID)")
    #answerID = input("> ")

    # display details

    # ask if they want to vote for the answer
    #wantToVote = True
    #if (wantToVote):
      #  if (votePost(answerID, userID, db)):
          #  print("Successfully voted")


  


            



