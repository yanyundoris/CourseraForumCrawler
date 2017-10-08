# Coursera Discussion Forum Crawler

Coursera is an popular online learning platform which provides a variety of fields. Students interact with peers and teaching staff though internal discussion forum. So the forum discussion has rich information worthy to be used, like question & answer text, student activity. This module provides a crawler which can extract forum discussion content and user interact info automatically.

## Prepare your environment

Before your start, please make sure:

  1.  You have Coursera account with some classes signed in;
  2.  Check the following requirement clearly.

### You need to pre-install: 

```python
import ConfigParser
import json
import requests
import random
import string
import logging
import time

```

### Make sure you have a useable web browser

  1. Prepare your browser, and;
  2. Adding webdriver to your local path.
  
### Don't forget to fill in configuration.cfg file

  1. [coursera]: This url is fixed. Please don't change it.
  2. [local]: Please add your local brower.
  3. [Login]: Please enter your Coursera account name and password.
  4. [agent]: Please enter your agent.
  
  
## How to use it:

### You can simply run 

```
$ python test.py
```

with command line


## You will get the following output:

  1. LOGGING.log: Show you the Logging info.
  2. Test.json: All Forum info.
  3. TestAnswer.json: All Question&Anser info.
  
### The output format:

#### Test.json:

```
{
 "paging": {}, 
 "elements": [
  {
   "forumType": {
    "typeName": "customForumType", 
    "definition": {}
   }, 
   "description": {
    "typeName": "cml", 
    "definition": {
     "value": "<co-content><text>This is a space for learners to ask overarching course-related questions or questions that do not apply to specific assignments.</text></co-content>", 
     "dtdId": "discussions/1"
    }
   }, 
   "title": "General Course Questions", 
   "parentForumId": "Bkx-PB00Eea0YQ7Ij7lJXw~iiwpfij0Eea8jw6UvTi2Tw", 
   "id": "Bkx-PB00Eea0YQ7Ij7lJXw~uwHgYXbAEeeh0gq4yYKIVA", 
   "order": 0
  }, 
```
#### TestAnswer.json

```
{
 "isFollowing": false, 
 "forumId": "_GW-FFXkEeenoRI2_PCm-g", 
 "courseId": "Bkx-PB00Eea0YQ7Ij7lJXw", 
 "followCount": 1, 
 "isUpvoted": false, 
 "linked": {
  "onDemandCourseForumAnswers": [], 
  "onDemandSocialProfiles": [
   {
    "courseId": XXXXX, 
    "userId": XXXXX, 
    "externalUserId": XXXXX, 
    "learnerId": XXXXX, 
    "courseRole": "LEARNER", 
    "fullName": XXXXX, 
    "id": XXXXX
   }
  ]
 }, 
 "createdAt": 1507402788242, 
 "answerBadge": {}, 
 "forumFlag": 1, 
 "sessionId": "VOv41HPNEeenPAowRltXdg", 
 "id": XXXXX, 
 "content": {
  "question": XXXXX, 
  "details": {
   "typeName": "cml", 
   "definition": {
    "value": XXXXX, 
    "dtdId": "discussion/1"
   }
  }
 }, 
 "state": {
  "edited": {
   "timestamp": 1507402845025, 
   "userId": XXXXX
  }
 }, 
 "forumQuestionId": "sMVXsauREee7eQoPPhIfbA", 
 "viewCount": 3, 
 "isFlagged": false, 
 "forumTitle": "Week 1", 
 "totalAnswerCount": 0, 
 "topLevelAnswerCount": 0, 
 "forumAnswerBadgeTagMap": {}, 
 "creatorId": XXXXX, 
 "upvoteCount": 0
}

```
