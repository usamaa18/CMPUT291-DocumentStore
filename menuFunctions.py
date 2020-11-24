from datetime import datetime
from tabulate import tabulate
import pprint
# return string formatted datetime
def formatDate(date):
    return date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

# generate a unique ID for the collection
def generateID(collection):
    # TODO
    return 1 

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
        "Body": body,
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
        "Body": body,
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
    # TODO
    pass

# searches posts for keywords and return cursor object
def searchQuestions(keywords, userID, db):
    # TODO 
    pass

# lists all answers to a given question
def getAnswers(questionID, userID, db):

    
    while True:
        #questionID=str(input("> questionID:"))
        question= db.posts.find_one({"$and": [{"Id":questionID},{"PostTypeId": "1"}]})
        if question == None:
            print("The post selected is not a question")
            
        else:
            ansCount= db.posts.count_documents({"ParentId": questionID})       
            if ansCount == 0:
                print("The question you've selected currently has no answers.")
                break
            else:
                check_for_accepted= db.posts.find_one({"$and": [{"Id": questionID}, {"AcceptedAnswerId":{"$exists": True}}]})
                if check_for_accepted == None:
                    ans= db.posts.find({"ParentId": questionID})
                    printAnswers(check_for_accepted,ans,questionID)
                    selectAnswer(questionID,db)
                    break
                else:
                    accepted_ansID= check_for_accepted["AcceptedAnswerId"]
                    accepted_ans= db.posts.find_one({"Id": accepted_ansID})
                    ans= db.posts.find({"$and":[{"Id": {"$ne": accepted_ansID}},{"ParentId":questionID}]})
                    printAnswers(accepted_ans,ans,questionID)
                    selectAnswer(questionID,db)
                    break
          
                
              

            



    
    


# format search query results in a user-friendly way
def printQuestions(res):
    pass

# format answer list in a user-friendly way
def printAnswers(accepted_ans,answers,questionID):
    table= []
    
    
    max_count = 80
    column_names= ["Id","Body", "CreationDate", "Score"]

    if accepted_ans != None:
        subtable1=[]
        accepted_ans_id= '☆ '+ accepted_ans["Id"]
        body= accepted_ans["Body"]
        cdate= accepted_ans["CreationDate"]
        score= accepted_ans["Score"]

        
        if len(body) > max_count:
            subtable1.extend(( accepted_ans_id, body[0:max_count -1 ],cdate,score))
            table.append(subtable1)
        else:
            subtable1.extend((accepted_ans_id, body,cdate,score))
            table.append(subtable1)
            
    for answer in answers:
        subtable2=[]
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
    


def selectAnswer(questionID, db):
    maxCount= 80
    while True:

        print("Select a answer (AnswerID)")
        answerID = input("> ").strip()
        selectAnswer= db.posts.find_one({"$and":[{"Id": answerID},{"ParentId":questionID}]})
        postAnswer = []
       
        
        if selectAnswer != None:
            pprint.pprint(selectAnswer)
            break
            
        else:
            print("The answerID selected doesn't correspond with the selected question. Please try again.")


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