import json


def GetForumQuestionOld(filename):

    forum_type = {}

    f = open(filename)
    forum = json.load(f)

    print forum['elements']
    print type(forum['elements']), len(forum['elements'])


    id_list = []
    for item in forum['elements']:
        print item['id']
        #print item['title']
        title = item['title']
        title = title.encode(encoding='utf-8')
        if title.startswith("Week") or title.startswith("A"):
            print item['title']
            forum_flag = 1
        else:
            print item['title']
            forum_flag = 0
        id_temp = item['id']
        id_temp = id_temp.encode(encoding='utf-8')
        forum_type[id_temp.split('~')[1]]=[]
        forum_type[id_temp.split('~')[1]].append((title,forum_flag))

        #id_temp = (id_temp, title, forum_flag)
        print id_temp
        id_list.append(id_temp)

    print id_list
    print forum_type

    return id_list, forum_type



