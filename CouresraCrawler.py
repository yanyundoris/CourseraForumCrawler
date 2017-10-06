import ConfigParser
import json
import requests
import random
import string
import logging
import time


logging.basicConfig(filename='example.log', level=logging.DEBUG)




class CourseraCrawler:
    """Crawl forum discussion from Coursera"""

    def __init__(self, config_file):

        """
        :param config_file: file providing your configuration info like url, account, password and agent
        """

        cf = ConfigParser.ConfigParser()

        try:
            cf.read(config_file)
        except:
            print "Read configuration fails!"
            logging.error("Read configuration fails!")


        self.signin_url = cf.get('coursera', 'url')
        self.account = cf.get('Login', 'username')
        self._password = cf.get('Login', 'password')
        self._agent = cf.get('agent', 'user_agent')

        self._logininfo = {"email": self.account,
                     "password": self._password,
                     "webrequest": "true"
                     }

    def randomString(self, length):
        """

        Args:
            length:

        Returns:

        """

        return ''.join(random.choice(string.letters + string.digits) for i in xrange(length))

    def JsonEncoder(self, encode_object, encoding='utf-8'):
        """

        Args:
            encode_object:
            encoding:

        Returns:

        """

        if isinstance(encode_object, dict):
            return {self.JsonEncoder(key, encoding): self.JsonEncoder(value, encoding) for key, value in
                    encode_object.iteritems()}
        elif isinstance(encode_object, list):
            return [self.JsonEncoder(item, encoding) for item in encode_object]
        elif isinstance(encode_object, unicode):
            return encode_object.encode(encoding)
        else:
            return encode_object

    def LoginToCoursera(self):
        """
        :return: return a session object if login success
        """

        XCSRF2Cookie = 'csrf2_token_%s' % ''.join(self.randomString(8))
        XCSRF2Token = ''.join(self.randomString(24))
        XCSRFToken = ''.join(self.randomString(24))
        cookie = "csrftoken=%s; %s=%s" % (XCSRFToken, XCSRF2Cookie, XCSRF2Token)

        post_headers = {"User-Agent": self._agent,
                        "Referer": "https://www.coursera.org/browse?authMode=login",
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRF2-Cookie": XCSRF2Cookie,
                        "X-CSRF2-Token": XCSRF2Token,
                        "X-CSRFToken": XCSRFToken,
                        "Cookie": cookie
                        }

        coursera_session = requests.Session()

        login_res = coursera_session.post(self.signin_url,
                                          data=self._logininfo,
                                          headers=post_headers,
                                          )
        if login_res.status_code == 200:
            print "Login Successfully!"
        else:
            print "Fail!"
            print login_res.text
            logging.error(login_res.text)

        return coursera_session

    def GetCourseID(self, course_url, your_session):
        """

        Args:
            course_url:
            your_session:

        Returns:

        """


        JScontent = your_session.get(course_url).content
        #print JScontent
        IdIndex, UserIdIndex = JScontent.index('"courseId":"'), JScontent.index('"userId":')

        IdIndex, UserIdIndex = IdIndex+len('"courseId":"'), UserIdIndex + len('"userId":')
        self.CourseId, self.UserId = "", ""


        while True:

            if JScontent[IdIndex] == '"':
                break
            self.CourseId = self.CourseId + JScontent[IdIndex]
            IdIndex = IdIndex + 1

        while True:

            if not JScontent[UserIdIndex].isdigit():
                break
            self.UserId = self.UserId + JScontent[UserIdIndex]
            UserIdIndex = UserIdIndex + 1


        return self.CourseId, self.UserId

    def GetForumId(self,cId, forumLimit, needfield, your_session, source = 'from_url',filename = ''):
        """ This function will send a request to get all forum Id for the given course, the output is
            a json object. After getting final output, you can specify a filename to save it as json file.

        Args:
            cId (str): course id, this parameter is an output returned from function GetCourseID
            forumLimit (int): max num of forums, by default is 500
            needfield (str): field in response you need
            your_session: sesssion with authorization created by function LoginToCoursera
            source (str): specify where to get forum id. if use 'from_url', the forum id will be crawled online.
            use 'from_file', the forum id will be readed from a json file.
            filename (str): Filename. if source is from_url, the filename is the directory with filename that you save the output.
            if source is from_file, the filename is the file path you need to input.

        Returns:
            id_list (list): The list contain all forum id
            forum_type (dict): The dict show the title and tag for each forum


        """

        if source == 'from_url':

            get_header = {'q': 'course',
                           'courseId': cId,
                           'limit': forumLimit,
                          'fields':askField}

            get_url = 'https://www.coursera.org/api/onDemandCourseForums.v1'

            forum_json = your_session.get(get_url, params = get_header).json()

            if filename != '':
                f = open(filename, "w+")
                forum_json_str = json.dumps(forum_json, ensure_ascii=False, indent= True)
                try:
                    f.write(forum_json_str.encode('ascii', 'ignore').decode('ascii'))
                except:
                    logging.error("Meet encoding errrpr when writing forum ID to File ")
                f.close()

        elif source == 'from_file':

            f = open(filename)
            forum_json = json.load(f)


        forum_type = {}
        id_list = []
        print forum_json
        for item in forum_json['elements']:

            title_temp = item['title'].encode(encoding='utf-8')
            if title_temp.startswith("Week") or title_temp.startswith("A"):
                forum_flag = 1
            else:
                forum_flag = 0
            id_temp = item['id'].encode(encoding='utf-8')

            forum_type[id_temp.split('~')[1]] = []
            forum_type[id_temp.split('~')[1]].append((title_temp, forum_flag))

            id_list.append(id_temp)


        return id_list, forum_type

    def CheckNoneElement(self,response):
        """

        Args:
            response:

        Returns:

        """
        if "elements" in response.keys() and response['elements'] != []:
            return True

    def GetQuestionId(self, forum_id, forum_type, your_session):
        """

        Args:
            forum_id:
            forum_type:
            your_session:

        Returns:

        """

        question_list = []
        GapNum = 100

        for courseForumId in forum_id:

            startpoint = 0

            while True:
                print "Round: ", str(startpoint/GapNum), "*"*100
                get_url = 'https://www.coursera.org/api/onDemandCourseForumQuestions.v1/'
                askField = 'content,state,creatorId,createdAt,forumId,sessionId,lastAnsweredBy,lastAnsweredAt,' \
                           'upvoteCount,followCount,totalAnswerCount,topLevelAnswerCount,viewCount,isFlagged,isFollowing,' \
                           'isUpvoted,answerBadge,onDemandSocialProfiles.v1(userId,externalUserId,fullName,photoUrl,courseRole)'

                get_header = {'userId': self.UserId,
                              'shouldAggregate': 'true',
                              'includeDeleted': 'false',
                              'sort': 'lastActivityAtDesc',
                              'includes': 'profiles',
                              'fields': askField,
                              'limit': GapNum,
                              'q': 'byCourseForumId',
                              'courseForumId':courseForumId,
                              'sessionFilter':'all',
                              'start':str(startpoint)}

                try:
                    res =  your_session.get(get_url, params = get_header).json()
                except:
                    logging.error("Cannot get forum" + courseForumId)

                #print len(res['elements'])

                if not self.CheckNoneElement(res):
                    break

                if len(res['elements'])!= 0:
                    for question in res['elements']:
                        if 'forumQuestionId' in question.keys():
                            question_list.append(question['forumQuestionId'])

                startpoint = startpoint + GapNum
                print len(question_list)

                time.sleep(3)

        question_list = list(set(question_list))

        return question_list

    def GetAnswer(self, question_id,your_session, forum_type, filename = ""):
        """

        Args:
            question_id:
            your_session:
            forum_type:
            filename:

        Returns:

        """

        if filename != "":
            f = open(filename, "w+")

        temp = self.UserId + '~' + self.CourseId

        for question in question_id:
            get_url = 'https://www.coursera.org/api/onDemandCourseForumQuestions.v1/'+ temp +'~' +question

            askField = 'content,state,creatorId,createdAt,forumId,sessionId,lastAnsweredBy,lastAnsweredAt,' \
                       'upvoteCount,followCount,totalAnswerCount,topLevelAnswerCount,viewCount,isFlagged,' \
                       'isFollowing,isUpvoted,answerBadge,forumAnswerBadgeTagMap,' \
                       'onDemandSocialProfiles.v1(userId,externalUserId,fullName,photoUrl,courseRole),' \
                       'onDemandCourseForumAnswers.v1(content,forumQuestionId,parentForumAnswerId,state,creatorId,' \
                       'createdAt,order,upvoteCount,childAnswerCount,isFlagged,isUpvoted,courseItemForumQuestionId,' \
                       'parentCourseItemForumAnswerId)'

            includes = 'profiles,posts,onDemandCourseForumAnswers.v1(profiles,children)'

            get_header = {'includes':includes,
                          'fields':askField}

            try:
                res = your_session.get(get_url, params=get_header).json()
            except:
                logging.error("Cannot get Question" + get_url)

            #print res

            if self.CheckNoneElement(res):

                new_res = {}
                new_res = res['elements'][0]
                print new_res['forumId']
                print forum_type[new_res['forumId']]
                title_flag = forum_type[new_res['forumId']][0]
                print title_flag
                new_res['linked'] = {}
                new_res['forumTitle'] = title_flag[0]
                new_res['forumFlag'] = title_flag[1]
                new_res['linked']['onDemandSocialProfiles'] = res['linked']['onDemandSocialProfiles.v1']
                new_res['linked']['onDemandCourseForumAnswers'] = res['linked']['onDemandCourseForumAnswers.v1']

                new_res.pop('userId', None)

                print new_res

                time.sleep(3)

                if filename != "":
                    forum_json_str = json.dumps(new_res, ensure_ascii=False, indent=True)

                    try:
                        f.write(forum_json_str.encode('ascii', 'ignore').decode('ascii'))
                    except:
                        logging.error("Meet encoding error when writing answer to File " + get_url)
        f.close()




if __name__ == '__main__':

    ForumCrawl = CourseraCrawler("./configuration.cfg")
    ForumCrawlSession = ForumCrawl.LoginToCoursera()
    courseID, userID = ForumCrawl.GetCourseID('https://www.coursera.org/learn/python-text-mining/home/welcome', ForumCrawlSession)


    askField = 'description,forumType,legacyForumId,order,parentForumId,title,groupForums.v1(description,forumType,order,parentForumId,title)'

    ForumCrawl.GetForumId(courseID, 500, askField, ForumCrawlSession)
    forum_id, forum_type = ForumCrawl.GetForumId(courseID, 500, askField, ForumCrawlSession, source = 'from_file',filename = 'Test.json')
    questionID = ForumCrawl.GetQuestionId(forum_id, forum_type, ForumCrawlSession)
    ForumCrawl.GetAnswer(questionID, ForumCrawlSession, forum_type, filename='TestAnswer.json')




