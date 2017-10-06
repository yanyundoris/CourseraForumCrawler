import requests
import random
import string
from requests.auth import HTTPBasicAuth
import ConfigParser
import json
import ast
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
    if response['elements'] != []:
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


def GetForumIDlist(source,filename='',login_session='',url ='',save_file = ''):

    if source == 'from_url':

        forum_json = login_session.get(url).json()
        forum_json = JsonEncoder(forum_json)
        print json.dumps(forum_json, ensure_ascii=False)
        forum_json = json.dumps(forum_json, ensure_ascii=False)
        forum_json = JsonEncoder(forum_json)
        if save_file != '':
            # forum_json = JsonEncoder(forum_json)
            # print json.dumps(forum_json, ensure_ascii=False)
            # forum_json = json.dumps(forum_json, ensure_ascii=False)
            f = open(save_file, "w")
            f.write(forum_json)
            f.close()

    elif source == 'from_file':

        f = open(filename)
        forum_json = json.load(f)

        print forum_json

    forum = forum_json

    forum_type = {}
    id_list = []
    for item in forum['elements']:

        title_temp = item['title']
        title_temp = title_temp.encode(encoding='utf-8')
        if title_temp.startswith("Week") or title_temp.startswith("A"):
            forum_flag = 1
        else:
            forum_flag = 0
        id_temp = item['id']
        id_temp = id_temp.encode(encoding='utf-8')
        forum_type[id_temp.split('~')[1]]=[]
        forum_type[id_temp.split('~')[1]].append((title_temp,forum_flag))

        id_list.append(id_temp)

    print id_list
    print forum_type

    return id_list, forum_type



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

    myurl = 'https://www.coursera.org/api/onDemandCourseForums.v1?q=course&courseId=Gtv4Xb1-EeS-ViIACwYKVQ&limit=500&fields=title,description,parentForumId,order,legacyForumId,forumType,groupForums.v1(title,description,parentForumId,order,forumType)'


    filename = '/Users/yanyunliu/PycharmProjects/CourseraCrawl/forum_id_new.json'
    id_list, forum_type = GetForumIDlist('from_file', filename, login_session=coursera_session, url=myurl, save_file='')

    print id_list




