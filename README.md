"# CMPUT291-DocumentStore" 

This project is an introduction to the integration of NoSQL family, more specifically mongodb  with Python. This application performs just like any classic Q&A forum would, like the popular website stackoverflow.com. However it is completely command-line based and has no GUI. 

<ul>All major user functionalities are listed below:</ul>
<li>Login (optional)</li>
<li>Post questions</li>
<li>Search for questions using keywords</li>
<li>Answer questions</li>
<li>List answers ( of questions from keyword search)</li>
<li>Post/Answer Votes</li>

</br>

Install pymongo:

<code>pip3 install pymongo</code>

Install orjson:

<code>pip3 install --upgrade "pip>=19.3" # manylinux2014 support</code></br>
<code>pip3 install --upgrade orjson</code>

If you have trouble installing orjson, just replace all "orjson" in main.py to "json" and it should work

Install bsonjs:

<code>python3 -m pip install python-bsonjs</code>

