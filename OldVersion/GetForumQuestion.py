import requests
import random
import string
from requests.auth import HTTPBasicAuth
import ConfigParser
import json
import ast
from GetForumID import *


if __name__ == '__main__':

    cf = ConfigParser.ConfigParser()
    cf.read("configuration.cfg")

    signin_url = cf.get('coursera','url')
    your_email_account = cf.get('Login','username')
    your_password = cf.get('Login','password')
    your_agent = cf.get('agent','user_agent')
    #signin_url = 'https://www.coursera.org/api/login/v3'
    logininfo = {"email": your_email_account,
                 "password": your_password,
                 "webrequest": "true"
                 }


    coursera_session = LoginToCoursera(logininfo, your_agent, signin_url)



    f = open('QuestionIDjsonForOld.json','w+')
    f_log = open('QuestionLog.txt','w+')

    question_list = []
    filename = 'forum_id.json'
    forum_id, forum_type = GetForumIDlist('from_file',filename)

    print forum_type


    for item in forum_id:
        print item
    #for item in test['elements']:

        startpoint = 0

        #print item['id']
        #courseForumId = item['id']
        courseForumId = item

        questionurl = 'https://www.coursera.org/api/onDemandCourseForumQuestions.v1/' \
                      '?userId=22004063&shouldAggregate=true&includeDeleted=false&' \
                      'sort=lastActivityAtDesc&fields=content%2Cstate%2CcreatorId%2CcreatedAt' \
                      '%2CforumId%2CsessionId%2ClastAnsweredBy%2ClastAnsweredAt%2CupvoteCount' \
                      '%2CfollowCount%2CtotalAnswerCount%2CtopLevelAnswerCount%2CviewCount' \
                      '%2CanswerBadge%2CisFlagged%2CisUpvoted%2CisFollowing%2' \
                      'ConDemandSocialProfiles.v1(userId%2CexternalUserId%2CfullName%2CphotoUrl%2CcourseRole)' \
                      '&includes=profiles&limit=100&q=byCourseForumId&' \
                      'courseForumId=' + courseForumId + '&sessionFilter=all'+'&start='+str(startpoint)
        print questionurl

        res = coursera_session.get(questionurl, auth=HTTPBasicAuth('dorisliu9318@gmail.com', 'Wawzxklyy9318')).json()
        print res
        """
        check_len = len(question_list)

        i = 0

        while CheckNoneElement(res):
            print "round i", i
            i = i +1
            print len(res['elements']), res['paging']




            for keyvalue in res['elements']:
                # print keyvalue
                # print type(keyvalue)
                keyvalue_encode = JsonEncoder(keyvalue)
                keyvalue_encode = json.dumps(keyvalue_encode,ensure_ascii=False)
                question_list.append(keyvalue_encode)
                #print keyvalue_encode


            startpoint = startpoint + 100

            questionurl = 'https://www.coursera.org/api/onDemandCourseForumQuestions.v1/' \
                          '?userId=22004063&shouldAggregate=true&includeDeleted=false&' \
                          'sort=lastActivityAtDesc&fields=content%2Cstate%2CcreatorId%2CcreatedAt' \
                          '%2CforumId%2CsessionId%2ClastAnsweredBy%2ClastAnsweredAt%2CupvoteCount' \
                          '%2CfollowCount%2CtotalAnswerCount%2CtopLevelAnswerCount%2CviewCount' \
                          '%2CanswerBadge%2CisFlagged%2CisUpvoted%2CisFollowing%2' \
                          'ConDemandSocialProfiles.v1(userId%2CexternalUserId%2CfullName%2CphotoUrl%2CcourseRole)' \
                          '&includes=profiles&limit=100&q=byCourseForumId&' \
                          'courseForumId=' + courseForumId + '&sessionFilter=all'+'&start='+str(startpoint)

            try:
                res = coursera_session.get(questionurl, auth=HTTPBasicAuth('dorisliu9318@gmail.com', 'Wawzxklyy9318')).json()
            except:
                print "Error for ID", courseForumId
                f_log.write(courseForumId)
                f_log.write('\n')



        print item['id'], item['title'],len(question_list), len(question_list)-check_len
        print str(startpoint)




    question_dict = json.dumps(question_list)
    json.dump(question_dict,f)

    f.close()

    f_log.close()

    """




