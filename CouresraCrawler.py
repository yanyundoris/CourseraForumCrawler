# -*- coding: utf-8 -*-


""" Python Coursera Discussion Forum Crawler.

This module provides a crawler which can extract forum discussion content and user interact info automatically.


Note:
    Before your start, you should have Coursera account with some classes signed in, otherwise the crawler cannot find your
    authorization.

    Besides, you also need to set a basic environment for crawler.
        e.g. Prepare your browser, and;
             adding webdriver to your local path.

    Finally, remember to fill in your account info and agent info in configuration.cfg


Example:
    To test your crawler, run:
        $ python test.py

    The output:

    LOGGING.log: Logging info
    Test.json: All Forum info
    TestAnswer.json: All Question&Anser info.



"""

import ConfigParser
import json
import requests
import random
import string
import logging
import time


logging.basicConfig(filename='LOGGING.log', level=logging.DEBUG)




class CourseraCrawler:
    """Crawl forum discussion from Coursera

    This class define the body of our crwaler. The workflow to extract all forum discussion is lised below:

        - Initialize crawler with your configuration,
        - Login to your class with a provided url,
        - Extract all forum info e.g. forum id and forum title,
        - Extract all forum question info, e.g. forum question id,
        - The last step, the crawler will find all the discussion (answer) for each question

    Attributes:

        signin_url: the url provided in configuration file.
        account: your Coursera account.
        _password: your password.
        _agent: your local agent.
        _logininfo: the header the crawler will use to post a request.

    Properties:

        GetCourseID: Extract your internal user id and internal course id after login.


    Methods:

        randomString: A simple random string generator.
        LoginToCoursera: Function implements log in and return a authorized session.
        GetForumId: Function sends a request to get all forum Id for the given course, and output all the forum info.
        CheckNoneElement: Check whether the response is empty or not.
        GetQuestionId: Provide the forum info, extract all the question one by one.
        GetAnswer: Extract all the answers and discussion under all of the questions.



    """

    def __init__(self, config_file):

        """ This function initialize the crawler with a provided configuration file.

        After initialization, the crawler will get the following attribute:

            Public:

                signin_url: the url provided in configuration file.
                account: your Coursera account.

            Private:
                _password: your password.
                _agent: your local agent.
                _logininfo: the header the crawler will use to post a request.


        Args:
            config_file: The configuration.cfg file you need to fill in
        """

        cf = ConfigParser.ConfigParser()

        try:
            cf.read(config_file)
        except:

            # Once initialize failed, the error info can be found in LOGGING.log
            print "Read configuration fails!"
            logging.error("Read configuration fails!")

        # Parse your url, account, password and agent.
        self.signin_url = cf.get('coursera', 'url')
        self.account = cf.get('Login', 'username')
        self._password = cf.get('Login', 'password')
        self._agent = cf.get('agent', 'user_agent')

        self._logininfo = {"email": self.account,
                     "password": self._password,
                     "webrequest": "true"
                     }

    def randomString(self, length):
        """ This function provide a simple random string generator with a set lenght

        Args:
            length (int): The lenght of random string you need.

        Returns:
            A random string

        """

        return ''.join(random.choice(string.letters + string.digits) for i in xrange(length))

    def JsonEncoder(self, encode_object, encoding='utf-8'):
        """ This function encode a object recursively.

        Args:
            encode_object: Object you want to encode.
            encoding (str): encoding method, by default is utf-8

        Returns:

            An encoded object.

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

        """This function logs in to Coursera platform automatically.

        Returns:

            coursera_session: A authorized session if success

        """

        # Generate random string to pretend crawler to work as normal user.
        XCSRF2Cookie = 'csrf2_token_%s' % ''.join(self.randomString(8))
        XCSRF2Token = ''.join(self.randomString(24))
        XCSRFToken = ''.join(self.randomString(24))
        cookie = "csrftoken=%s; %s=%s" % (XCSRFToken, XCSRF2Cookie, XCSRF2Token)

        # Create post header to login

        post_headers = {"User-Agent": self._agent,
                        "Referer": "https://www.coursera.org/browse?authMode=login",
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRF2-Cookie": XCSRF2Cookie,
                        "X-CSRF2-Token": XCSRF2Token,
                        "X-CSRFToken": XCSRFToken,
                        "Cookie": cookie
                        }

        coursera_session = requests.Session()

        # Post a request

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
        """ This function will extract your interal user id and internal course id automatically.

        Args:
            course_url (str): The course you need.
            your_session: An authorized session returned by LoginToCoursera

        Returns:

            CourseId (str): The internal course id.
            UserId (str): The interal user id.

        Notes:
            Remember you need to sign in the course first.


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

    def GetForumId(self,cId, forumLimit, your_session, source = 'from_url',filename = ''):
        """ This function will send a request to get all forum Id for the given course, the output is
            a json object. After getting final output, you can specify a filename to save it as json file.

        Args:
            cId (str): course id, this parameter is an output returned from function GetCourseID
            forumLimit (int): max num of forums, by default is 500
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
            # from_url means the forum info will be crawled online.


            # By default askField contains nearly all info, you can specify your own need if you don't like it.
            askField = 'description,forumType,legacyForumId,order,parentForumId,title,groupForums.v1(description,forumType,order,parentForumId,title)'

            # Create a get header
            get_header = {'q': 'course',
                           'courseId': cId,
                           'limit': forumLimit,
                          'fields':askField}



            #This url is provided by Coursera
            get_url = 'https://www.coursera.org/api/onDemandCourseForums.v1'


            # Send the request and get the json object.
            forum_json = your_session.get(get_url, params = get_header).json()


            # If you don't need to output the json object and you only want to print it, set filename == ''.
            if filename != '':
                f = open(filename, "w+")
                forum_json_str = json.dumps(forum_json, ensure_ascii=False, indent= True)
                try:
                    f.write(forum_json_str.encode('ascii', 'ignore').decode('ascii'))
                except:
                    logging.error("Meet encoding errrpr when writing forum ID to File ")
                f.close()

        elif source == 'from_file':
            # from file means you have already output the forum info and you need to reuse it.
            # the file must has same structure as Coursera output.


            # load the json file
            f = open(filename)
            forum_json = json.load(f)


        # Parse the json object


        forum_type = {}
        id_list = []
        print forum_json
        for item in forum_json['elements']:

            title_temp = item['title'].encode(encoding='utf-8')

            # Get forum type, filter the forums and classify them into two types: Week & Assignment related and other
            # general info.
            if title_temp.startswith("Week") or title_temp.startswith("A"):
                forum_flag = 1
            else:
                forum_flag = 0

            # Get forum id
            id_temp = item['id'].encode(encoding='utf-8')

            forum_type[id_temp.split('~')[1]] = []
            forum_type[id_temp.split('~')[1]].append((title_temp, forum_flag))

            id_list.append(id_temp)


        return id_list, forum_type

    def CheckNoneElement(self,response):
        """ This function checks whether the crawler get an empty response.

        Args:
            response (dict): The response returned.

        Returns:

            A Bool type.

        """
        if "elements" in response.keys() and response['elements'] != []:
            return True

    def GetQuestionId(self, forum_id, forum_type, your_session):
        """ This function extract all the question id from forums.

        Args:
            forum_id (list): A list of forum id returned by GetForumId.
            forum_type (dict): A dict specify forum flag and title returned by GetForumId.
            your_session: The authorized session return by LoginToCoursera

        Returns:

            question_list (list): A list of all question id.

        """

        question_list = []
        GapNum = 100

        for courseForumId in forum_id:

            # Set a startpoint for page turning.
            startpoint = 0

            while True:

                print "Round: ", str(startpoint/GapNum), "*"*100

                # This url is speicfied by Coursera
                get_url = 'https://www.coursera.org/api/onDemandCourseForumQuestions.v1/'

                # By default askField contains nearly all info, you can specify your own need if you don't like it.
                askField = 'content,state,creatorId,createdAt,forumId,sessionId,lastAnsweredBy,lastAnsweredAt,' \
                           'upvoteCount,followCount,totalAnswerCount,topLevelAnswerCount,viewCount,isFlagged,isFollowing,' \
                           'isUpvoted,answerBadge,onDemandSocialProfiles.v1(userId,externalUserId,fullName,photoUrl,courseRole)'

                # Create get header
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

                # Send the request
                try:
                    res =  your_session.get(get_url, params = get_header).json()
                except:
                    logging.error("Cannot get forum" + courseForumId)


                # Check whether the crawler get an empty response, if so, break out of the while loop.

                if not self.CheckNoneElement(res):
                    break

                # Append question id fro response
                if len(res['elements'])!= 0:
                    for question in res['elements']:
                        if 'forumQuestionId' in question.keys():
                            question_list.append(question['forumQuestionId'])


                # Update the startpoint and turn one page.

                startpoint = startpoint + GapNum
                print len(question_list)

                # Pause a few seconds

                time.sleep(3)

        question_list = list(set(question_list))

        return question_list

    def GetAnswer(self, question_id,your_session, forum_type, filename = ""):
        """ This function extract all the answer and discussion under all of the question and write them out by a specified
        path and file name.

        Args:
            question_id (list): The list of all question id returned by GetQuestionId
            your_session: The authorized session return by LoginToCoursera
            forum_type (dict): A dict specify forum flag and title returned by GetForumId.
            filename (str): The file path with name where you want to save the output.

        Returns:

            Write the output into a file is filename is not ""

        """

        # Remember to provide the path

        if filename != "":
            f = open(filename, "w+")

        temp = self.UserId + '~' + self.CourseId

        for question in question_id:
            get_url = 'https://www.coursera.org/api/onDemandCourseForumQuestions.v1/'+ temp +'~' +question

            # By default askField contains nearly all info, you can specify your own need if you don't like it.
            askField = 'content,state,creatorId,createdAt,forumId,sessionId,lastAnsweredBy,lastAnsweredAt,' \
                       'upvoteCount,followCount,totalAnswerCount,topLevelAnswerCount,viewCount,isFlagged,' \
                       'isFollowing,isUpvoted,answerBadge,forumAnswerBadgeTagMap,' \
                       'onDemandSocialProfiles.v1(userId,externalUserId,fullName,photoUrl,courseRole),' \
                       'onDemandCourseForumAnswers.v1(content,forumQuestionId,parentForumAnswerId,state,creatorId,' \
                       'createdAt,order,upvoteCount,childAnswerCount,isFlagged,isUpvoted,courseItemForumQuestionId,' \
                       'parentCourseItemForumAnswerId)'

            includes = 'profiles,posts,onDemandCourseForumAnswers.v1(profiles,children)'


            # Create the get header.

            get_header = {'includes':includes,
                          'fields':askField}


            # Send get request

            try:
                res = your_session.get(get_url, params=get_header).json()
            except:
                logging.error("Cannot get Question" + get_url)

            # Check if the crawler get null response

            if self.CheckNoneElement(res):

                # Reconstruct the response into new_res

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

                # This userId is your internal id, not the forum users' id. So we pop it.

                new_res.pop('userId', None)

                print new_res

                time.sleep(3)

                # Write out the result.

                if filename != "":
                    forum_json_str = json.dumps(new_res, ensure_ascii=False, indent=True)

                    try:
                        f.write(forum_json_str.encode('ascii', 'ignore').decode('ascii'))
                        f.write("\n")
                    except:
                        logging.error("Meet encoding error when writing answer to File " + get_url)
        f.close()







