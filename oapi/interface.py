import requests
import json
from time import *
import os
from tqdm import tqdm
from oapi.jdict import jdict
from oapi.base import *

from datetime import datetime

class topic:
    def __init__(self, content=dict()):
        self.content = None
        if content != None:
            self.content = content
        else:
            self.content = dict()

    @property
    def validity(self):
        if self.empty:
            return False
        else:
            if self.id != 0 and self.title != '' and self.content.get('created_at', '') != '':
                return True
            else:
                return False

    # Свойства топиков
    @property
    def id(self):
        if 'id' in self.content:
            return self.content['id']
        else:
            return 0

    @property
    def title(self):
        if 'title' in self.content:
            return self.content['title']
        else:
            return ''

    @property
    def author(self):
        if 'author' in self.content:
            if self.content['author'] != None:
                return profile(self.content['author'])
            else:
                return profile()
        else:
            return profile()

    @property
    def authorId(self):
        if 'author' in self.content:
            if self.content['author'] != None:
                return self.content['author']['id']
        else:
            return 0

    @property
    def answer(self):
        if 'answer' in self.content:
            return self.content['answer']
        else:
            return []

    @property
    def replies_view_count(self):
        if 'replies_view_count' in self.content:
            return self.content['replies_view_count']
        else:
            return 0

    @property
    def created_at(self):
        return datetime.fromisoformat(self.content.get('created_at', ''))

    @property
    def updated_at(self):
        return datetime.fromisoformat(self.content.get('update_at', ''))

    @property
    def empty(self):
        return len(self.content) == 0

    @staticmethod
    def authors(topics):
        result = list()
        for t in topics:
            prof = t.author
            if not prof in result:
                result.append(t.author)
        return result

    # база данных
    @staticmethod
    def byIds(listid=[], localbase=None):
        result = list()
        for t in listid:
            result.append(topic.byId(t, localbase))
        return result

    @staticmethod
    def byId(topic_id, localbase=None):
        if localbase == None:
            return topic(get(f'topic/question/{topic_id}?postID={topic_id}'))
        else:
            return localbase.lbTopics.get(topic_id)

    def push(self, localbase=None):
        localbase.lbTopics.push(self.id, self.content)

    def contains(self, localbase=None):
        return localbase.lbTopics.contains(self.id)

    # доступ к api
    @staticmethod
    def top(user_id, limit=200, session=None):
        content = get(
            f'topic/profile/{user_id}/topics?userID={user_id}&dir=0&pos=0&limit={limit}&storage=profile-{user_id}-topics',
            session)
        if 'error' in content or len(content) == 0:
            return []
        topics = content['result']['feed']
        result = list()
        if topics == None:
            return []
        for t in topics:
            topi = topic(t)
            if not topi.empty:
                result.append(topi)

        return result

    @staticmethod
    def read(user_id=0, pos=0, limit=200, session=None):
        content = get(
            f'topic/profile/{user_id}/topics?userID={user_id}&dir=1&pos={pos}&limit={limit}&storage=profile-{user_id}-posts',
            session)
        if 'error' in content or len(content) == 0:
            return []
        topics = content['result']['feed']
        result = list()
        if topics == None:
            return []
        for t in topics:
            topi = topic(t)
            if not topi.empty:
                result.append(topi)

        return result

    @staticmethod
    def parse(prof=None, pos=0, limit=20, bar_update=None, session=None):
        result = list()
        if pos == 0:
            buffer = topic.top(user_id=prof.id, limit=200, session=session)
        else:
            buffer = topic.read(user_id=prof.id, pos=pos, limit=200, session=session)
        if buffer == []:
            return []
        count = 0
        index = 0
        for r in buffer:
            result.append(r)
            count += 1
            index += 1
            if count == limit:
                if bar_update != None:
                    bar_update(index)
                prof.topics_id.extend(topic.listid(result))
                return result

        if bar_update != None:
            bar_update(index)
        while True:
            index = 0
            pos = result[-1].id
            buffer = topic.read(user_id=prof.id, pos=pos, limit=200, session=session)
            if buffer == []:
                prof.topics_id.extend(topic.listid(result))
                return result
            for r in buffer:
                result.append(r)
                count += 1
                index += 1
                if count == limit:
                    if bar_update != None:
                        bar_update(index)
                    prof.topics_id.extend(topic.listid(result))
                    return result
            if bar_update != None:
                bar_update(index)

    def loadAnswer(self, session=None):
        replies = get(f'topic/answers/{self.id}?limit={self.replies_view_count}&dir=0&sort=rating&order', session)
        if len(replies) == 0:
            return []
        if replies['result']['replies'] == None:
            replies['result']['replies'] = []
        result = list()
        for r in replies['result']['replies']:
            result.append(replie(r))
        self.content['answer'] = replie.listid(result)
        return result

    # Другие
    @staticmethod
    def listid(topics):
        result = list()
        for t in topics:
            result.append(t.id)
        return result

    @staticmethod
    def main(pos, limit=200, interval=10, barload=True, session=None):
        tid = pos
        result = list()
        bar = None
        for i in range(limit // interval):
            sublist, tid = topic.Main(tid, interval, session=session)
            if sublist == []:
                return result
            result.extend(sublist)
            if barload:
                bar.update(interval)
        for i in range(limit % interval):
            sublist = topic.Main(tid, interval, session=session)
            if sublist == []:
                return result
            result.extend(sublist)
        if barload:
            bar.update(limit % interval)
        return result

    @staticmethod
    def Main(pos, limit=20, session=None):
        if pos == 0:
            content = get(f'topic/feed?limit=20&pos={pos}&dir=0&storage=main&sort=id', session)
        else:
            content = get(f'topic/feed?limit=20&pos={pos}&dir=1&storage=main&sort=id', session)
        if 'error' in content or len(content) == 0:
            return ([], pos)
        if content['result']['feed'] == None:
            return ([], pos)
        result = list()
        for c in content['result']['feed']:
            topi = topic(content=c)
            result.append(topi)
        return (result, content['result']['params']['pos'])

    def tree(self, session=None):
        if self.replies_view_count == 0:
            return []
        result = self.loadAnswer()
        replies = result
        while True:
            buffer = []
            for r in replies:
                if r.replyToReplyCount != 0:
                    buffer.extend(r.loadAnswer(session=session))
            if buffer == []:
                self.content['answer'] = result
                return result
            result.extend(buffer)
            replies = buffer

    @staticmethod
    def print(topics):
        for t in topics:
            if t.validity:
                print(t.id, t.authorId, t.created_at, t.title)
            else:
                print('?', '?', '?', '?')

    def __getitem__(self, attr):
        return self.content[attr]

    def __setitem__(self, attr, value):
        self.content[attr] = value

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id

    def __lt__(self, other):
        return self.id < other.id

    def __le__(self, other):
        return self.id <= other.id

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id

    def __str__(self):
        if self.validity:
            return f'{self.id} {self.authorId} {self.created_at} {self.title}'
        else:
            return '? ? ? ?'
