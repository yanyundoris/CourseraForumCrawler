import CouresraCrawler as Crawler

ForumCrawl = Crawler.CourseraCrawler("./configuration.cfg")


print ForumCrawl.__dict__.keys()

ForumCrawlSession = ForumCrawl.LoginToCoursera()
courseID, userID = ForumCrawl.GetCourseID('https://www.coursera.org/learn/python-text-mining/home/welcome',
                                          ForumCrawlSession)


forum_id, forum_type = ForumCrawl.GetForumId(courseID, 500,  ForumCrawlSession, source='from_url',
                                             filename='Test.json')
questionID = ForumCrawl.GetQuestionId(forum_id, forum_type, ForumCrawlSession)
ForumCrawl.GetAnswer(questionID, ForumCrawlSession, forum_type, filename='TestAnswer.json')