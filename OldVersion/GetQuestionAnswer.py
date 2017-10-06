import requests
import random
import string
from requests.auth import HTTPBasicAuth
import ConfigParser
import json
import ast
from MongoImport import GetUserCourseQuestionId
from GetForumQuestionForOld import GetForumQuestionOld

def randomString(length):
    return ''.join(random.choice(string.letters + string.digits) for i in xrange(length))

def LoginToCoursera(accountInfo, your_agent, signin_url):

    XCSRF2Cookie = 'csrf2_token_%s' % ''.join(randomString(8))
    XCSRF2Token = ''.join(randomString(24))
    XCSRFToken = ''.join(randomString(24))
    cookie = "csrftoken=%s; %s=%s" % (XCSRFToken, XCSRF2Cookie, XCSRF2Token)
    #cookie = '__204u=8104371819-1487229824875; __204r=; CSRF3-Token=1497603240.it8PKk8cxk6qrU5B; ip_origin=HK; ip_currency=USD; __400v=7017cc84-cb08-475a-e691-d4ab119c5949; _dc_gtm_UA-28377374-1=1; _dc_gtm_UA-86370891-1=1; _ga=GA1.2.1502214987.1487229828; _gid=GA1.2.177416310.1496739245; _uetsid=_uetcf933edd; stc113717=env:1496754900%7C20170707131500%7C20170606134512%7C2%7C1030880:20180606131512|uid:1496739245419.604444845.8252726.113717.693343111.3:20180606131512|srchist:1030880%3A1496754900%3A20170707131500:20180606131512|tsa:1496754900697.1718652966.2916284.6758469617569263.:20170606134512; __400vt=1496754913604'


    post_headers = {"User-Agent": your_agent,
                    "Referer": "https://www.coursera.org/browse?authMode=login",
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRF2-Cookie": XCSRF2Cookie,
                    "X-CSRF2-Token": XCSRF2Token,
                    "X-CSRFToken": XCSRFToken,
                    "Cookie": cookie
                    }

    coursera_session = requests.Session()

    login_res = coursera_session.post(signin_url,
                                      data=accountInfo,
                                      headers=post_headers,
                                      )
    if login_res.status_code == 200:
        print "Login Successfully!"
        print login_res.text
        return coursera_session
    else:
        print "Fail!"
        print login_res.text

#def GetAllForumID(url,coursera_session):

def CheckNoneElement(response):
    if "elements" in response.keys() and response['elements'] != [] and int(len(res['elements']))==1:
        return True



def JsonEncoder(encode_object,encoding ='utf-8'):

    if isinstance(encode_object,dict):
        return {JsonEncoder(key,encoding):JsonEncoder(value,encoding) for key, value in encode_object.iteritems()}
    elif isinstance(encode_object, list):
        return [JsonEncoder(item,encoding) for item in encode_object]
    elif isinstance(encode_object,unicode):
        return encode_object.encode(encoding)
    else:
        return encode_object


if __name__ == '__main__':

    cf = ConfigParser.ConfigParser()
    cf.read("/Users/yanyunliu/PycharmProjects/CourseraCrawl/configuration.cfg")

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

    #
    f = open('QuestionAnswerElementForOld.json','w+')
    f_logfile = open('logfileForOld.log',"w+")

    user_course_questionId = GetUserCourseQuestionId()
    id_list, forum_type = GetForumQuestionOld('/Users/yanyunliu/PycharmProjects/CourseraCrawl/forum_id_new.json')

    question_list = []

    startpoint = 0

    #print user_course_questionId

    for each_id in user_course_questionId:
        questionurl = 'https://www.coursera.org/api/onDemandCourseForumQuestions.v1/' \
                      +each_id+ \
                      '/?includes=profiles%2Cposts%2ConDemandCourseForumAnswers.v1' \
                      '(profiles%2Cchildren)&fields=content%2Cstate%2CcreatorId' \
                      '%2CcreatedAt%2CforumId%2CsessionId%2ClastAnsweredBy%2ClastAnsweredAt' \
                      '%2CupvoteCount%2CfollowCount%2CtotalAnswerCount%2CtopLevelAnswerCount' \
                      '%2CviewCount%2CisFlagged%2CisFollowing%2CisUpvoted%2CanswerBadge%' \
                      '2CforumAnswerBadgeTagMap%2ConDemandSocialProfiles.v1(userId%2CexternalUserId' \
                      '%2CfullName%2CphotoUrl%2CcourseRole)%2ConDemandCourseForumAnswers.v1' \
                      '(content%2CforumQuestionId%2CparentForumAnswerId%2Cstate%2CcreatorId' \
                      '%2CcreatedAt%2Corder%2CupvoteCount%2CchildAnswerCount%2CisFlagged%2CisUpvoted)'
        res = coursera_session.get(questionurl, auth=HTTPBasicAuth(your_email_account, your_password)).json()

        # print res

        if CheckNoneElement(res):
            # print res['elements']
            # print type(res['linked'])
            new_res = {}

            new_res = res['elements'][0]
            print new_res['forumId']
            print forum_type[new_res['forumId']]
            title_flag = forum_type[new_res['forumId']][0]
            print title_flag
            new_res['linked'] = {}
            new_res['forumTitle'] = title_flag[0]
            new_res['forumFlag'] = title_flag[1]
            # print new_res
            # print type(new_res)
            # print new_res.keys()
            # print new_res['linked'].keys()
            new_res['linked']['onDemandSocialProfiles'] = res['linked']['onDemandSocialProfiles.v1']
            new_res['linked']['onDemandCourseForumAnswers'] = res['linked']['onDemandCourseForumAnswers.v1']

            new_res.pop('userId', None)

            res = new_res

            res = JsonEncoder(res)
            #print type(res)
            dict_json = JsonEncoder(res)
            writerjson = json.dumps(dict_json, ensure_ascii=False)

            f.write(writerjson)
            f.write("\n")

            print startpoint, len(user_course_questionId)
            startpoint = startpoint +1
        else:

            f_logfile.write("Error")
            dict_json = JsonEncoder(res)
            writerjson = json.dumps(dict_json, ensure_ascii=False)
            f_logfile.write(writerjson)
            f_logfile.write("\n")


    f.close()
    f_logfile.close()
