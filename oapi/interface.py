import requests
import json
from time import *
import os
from tqdm import tqdm
from oapi.jdict import jdict
from oapi.base import *

from datetime import datetime

def get(method='',session=None):
    """
    Метод отправляет HTTPS запрос на сервер.

    Параметры:
        method (str):Метод api.
        session:Сессия для обращения к сервер.
    """
    if session==None:
        responce=requests.get('https://otvet.mail.ru/api/'+method)
    else:
        responce=session.get('https://otvet.mail.ru/api/'+method)
    if responce.status_code==200:
        return json.loads(responce.text)
    else:
        return dict()


class profile:
    """
    Класс предоставляет более удобный способ работы с контентом в котором содержится информация о профиле пользователя.
    """

    def __init__(self, content=dict()):
        """
        Конструктор создаёт профиль из словоря с информацией о нём.

        Параметры:
            content (dict):Словарь в котором содержится информация о профиле.
        """
        self.content = None
        if content == None:
            self.content = dict()
        else:
            self.content = content

    @staticmethod
    def byId(profile_id=0, localbase=None):
        """
        Метод возвращает профиль по его id, если локальная база localbase!=None, то ищет и читает его из локальной базы.

        Параметры:
            profile_id (int):Уникальный индетификатор профиля.
            localbase (oapi.base.localBase):Локальная база.

        Возвращает:
            profile:Информация о профиле.
        """
        result = profile()
        if localbase == None:
            """Больше не работает 
            count=get(f"topic/profile/{profile_id}/content/count")
            print(count)
            if len(count)!=0:
                if 'username' in count:
                    result.username=count['username']
                result.content=get(f"auth/users/{result.username}")
                result.content['topics_count']=count['result']['topics_count']
                result.content['replies_count']=count['result']['replies_count']
            """
        else:
            result = localbase.lbProfile.get(profile_id)
        return result

    @staticmethod
    def byNames(listname=[], localbase=None):
        """
        Метод загружает информацию о профилях по их id из списка

        Параметры:
            listid (list):Список индетификаторов профилей.
            localbase (oapi.base.localBase):Локальная база, если не None, то читает информацию о профиле из базы.
        """
        result = list()
        for n in listname:
            result.append(profile.byName(n))
        return result

    @staticmethod
    def byName(username=''):
        """
        Метод запрашивает информаю о профиле по его имени с сервера.

        Параметры:
            username (str):Имя профиля.

        Возвращает:
            profile:Информация о профиле.
        """
        result = profile()
        result.content = get(f"auth/users/{username}")
        if not result.empty:
            count = get(f"topic/profile/{result.id}/content/count")
            result.content['topics_count'] = count['result']['topics_count']
            result.content['replies_count'] = count['result']['replies_count']
        return result

    def contains(self, localbase):
        """
        Метод возвращает истину, если текущий профиль содержится в localbase. Проверка ведётся только по ID.

        Параметры:
            localbase (oapi.base.localBase):Локальная база.
        """
        return localbase.lbProfile.contains(self.id)

    def push(self, localbase=None):
        """
        Метод сохраняет информацию о профиле в localbase.

        Параметры:
            localbase (oapi.base.localBase):Локальная база.
        """
        localbase.lbProfile.push(self.id, self.content)

    @staticmethod
    def pushs(profiles=[], localbase=None):
        """
        Добовляет информацию из списка профилей в базу.

        Параметры:
            profiles (list):Список с информацией о профилях которую необходимо записать в базу.
            localbase (oapi.base.localBase):Локальная база в которую производится запись.
        """
        for p in profiles:
            p.push(localbase)

    @property
    def validity(self):
        """
        Метод возврощает истину, если информация профиля валидна.

        Возврощает:
            bool:Истина если данный профиль валиден.
        """
        if self.empty:
            return False
        else:
            if self.id != 0 and self.username != '' and self.content.get('created_at', '') != '':
                return True
            else:
                return False

    @property
    def id(self):
        """
        Свойство возвращает уникальный индетификатор профиля.

        Возвращает:
            int:Индетификатор пользователя, если content валиден иначе 0.
        """
        return self.content.get('id', 0)

    @property
    def created_at(self):
        """
        Свойство возвращает уникальный индетификатор профиля.

        Возвращает:
            int:Индетификатор пользователя, если content валиден иначе 0.
        """
        return datetime.fromisoformat(self.content.get('created_at', ''))

    @property
    def updated_at(self):
        """
        The property returns a unique profile identifier.

        return:
            int:The user ID if the content is valid, otherwise 0.
        """
        return datetime.fromisoformat(self.content.get('updated_at', ''))

    @property
    def username(self):
        """
        Свойство возвращает имя профиля.

        Возвращает:
            srt:Полное имя профиля.
        """
        return self.content.get('username', '')

    @property
    def topics_count(self):
        """
        Свойство возвращает количество постов в профиле.

        Возвращает:
            int:Количество постов.
        """
        return self.content.get('topics_count', '')

    @property
    def replies_count(self):
        """
        Свойство возвращает количество ответов в профиле.

        Возвращает:
            int:Количество ответов.
        """
        return self.content.get('replies_count', '')
        if 'replies_count' in self.content:
            return int(self.content['replies_count'])
        else:
            return 0

    @property
    def topics_id(self):
        """
        Свойство возвращает список id постов в профиле(этот список может отличатся от реального т.к этот список содержит только информацию о подгруженных постах).

        Возвращает:
            list:Список постов.
        """
        return self.content.get('topics_id', [])

    @topics_id.setter
    def topics_id(self, value):
        """
        Свойство устанавливает новый список индетификаторов постов которые будут содержатся в этом профиле.

        Параметры:
            value (list):Новый список индетификаторов постов.
        """
        self.content['topics_id'] = value

    @property
    def replies_id(self):
        """
        Свойство возвращает список id ответов профиля(этот список не отражает реальное количество ответов профиля, а содержит только ту информацию, которая известна)

        Возврощает:
            list:Список индетификаторов ответов в профиле.
        """
        return self.content.get('topics_id', [])

    @replies_id.setter
    def replies_id(self, value):
        """
        Свойство устанавливает новый список индетификаторов ответов которые будут содержатся в этом профиле.

        Параметры:
            value (list):Новый список индетефикаторов ответов.
        """
        self.content['replies_id'] = value

    def __getitem__(self, attr):
        return self.content.get(att)

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

    @staticmethod
    def print(profiles):
        """
        Метод выводит в консоль основную информацию о профилях. Предназначен для отладки и оценки валидности работы методов.

        Параметры:
            profiles (list):Список профилей информацию о которых необходимо вывести в консоль.
        """
        for p in profiles:
            if p.validity:
                print(f'{p.id} C{p.created_at} {p.username}')
            else:
                print('? ? ? ?')

    @staticmethod
    def listid(profiles=[]):
        """
        Метод возарощет список индетификаторов профилей из списка классов профилей.

        Возвращает:
            list:Список уникальныз индетификаторов пользователей.
        """
        result = list()
        for p in profiles:
            result.append(p.id)
        return result

    @staticmethod
    def listname(profiles=[]):
        """
        Метод возарощет список имён профилей из списка классов профилей.

        Возвращает:
            list:Список уникальныз индетификаторов пользователей.
        """
        result = list()
        for p in profiles:
            result.append(p.username)
        return result

    @property
    def empty(self):
        """
        Свойство возвращает истину, если информация о профиле отсутствует.

        Возвращает:
            bool:
        """
        return len(self.content) == 0

    def __str__(self):
        if self.validity:
            return f'{self.id} C{self.created_at} {self.username}'
        else:
            return '? ? ? ?'


class replie:
    def __init__(self, content=dict()):
        """
        Конструктор создаёт ответ из контента.

        Параметры:
            content (dict):Контент который несёт всю информацию об ответе на пост некоторого профиля.
        """
        self.content = None
        if self.content == None:
            self.content = content
        else:
            self.content = dict()

    @property
    def validity(self):
        """
        Свойство возвраращет истину, если данный ответ является валидным т.е несет достаточно информации чтобы считаться ответом пользователя.

        Возвращает:
            bool:Истина если валидно.
        """
        if self.empty:
            return False
        else:
            if self.id != 0 and self.content.get('created_at', '') != '':
                return True
            else:
                return False

    @property
    def id(self):
        """
        Свойство возвращает уникальный индетефикатор ответа.

        Возвращает:
            int:Уникальный индетефикатор пользователя.
        """
        if 'id' in self.content:
            return self.content['id']
        else:
            return 0

    @property
    def topic_id(self):
        """
        Свойство возвращает уникальный индетефикатор поста под которым был оставлен данный ответ.

        Возвращате:
            int:Уникальный индетефикатор поста.
        """
        if 'topic_id' in self.content:
            return self.content['topic_id']
        else:
            return 0

    @property
    def authorId(self):
        """
        Свойство возвращает уникальный индетефикатор автора который дал данный ответ.

        Возврощает:
            int:Уникальный индетефикатор автора.
        """
        if 'author' in self.content:
            if self.content['author'] != None:
                return self.content['author']['id']
            else:
                return 0
        else:
            return 0

    @property
    def author(self):
        """
        Свойство возвращает неполную информацию об авторе(Важно! Данная информаци является не полно и может содержать не все свойства)

        Возвращает:
            profile:Информация о профиле пользователя.
        """
        if 'author' in self.content:
            if self.content['author'] != None:
                return profile(self.content['author'])
            else:
                return profile()
        else:
            return profile()

    @property
    def reply_to(self):
        """
        Свойство возвращает уникальный индетефикатор ответа на который был дан данный ответ, если ответ был дан под постом, то возврощает 0.

        Возвращает:
            int:Индетефикатор ответа.
        """
        if 'reply_to' in self.content:
            return self.content['reply_to']
        else:
            return 0

    @property
    def replyToReplyCount(self):
        """
        Свойство возвращает количество ответов, которое было дано под этим ответом.

        Возвращает:
            int:Количество ответов на ответ.
        """
        if 'replyToReplyCount' in self.content:
            return self.content['replyToReplyCount']
        else:
            return 0

    @property
    def content2(self):
        """
        Свойство было введено специально для реализации свойства texts...
        """
        try:
            if self.content['content']['content'] != None:
                return self.content['content']['content']
            else:
                return []
        except:
            return []

    @property
    def texts(self):
        """
        Свойство возвращает всю текстовую информацию под постом +-.

        Возвращает:
            list:Список строк.
        """
        result = list()
        for r in self.content2:
            if 'content' in r:
                for i in r['content']:
                    if i['type'] in {'text', 'paragraph'}:
                        if 'text' in i:
                            result.append(i['text'])
        return result

    @property
    def answer(self):
        """
        Свойство возвращает список индетификаторов ответов на данный ответ.

        Возвращает:
            list:Список уникальных индетификаторов ответов данных на данный ответ.
        """
        if 'answer' in self.content:
            return self.content['answer']
        else:
            return 0

    @property
    def created_at(self):
        """
        Свойство возвращает информацию о дате и времени того когда был дан данный ответ.

        Возвращает:
            datetime:Информация о времени.
        """
        return datetime.fromisoformat(self.content.get('created_at', ''))

    @property
    def updated_at(self):
        """
        Свойство возвращает информацию о дате и времене того когда был обновлён данный ответ.

        Возващает:
            datetime:Информация о времени.
        """
        return datetime.fromisoformat(self.content.get('updated_at', ''))

    @property
    def empty(self):
        """
        Свойство возвращает истину, если контент данного ответа пуст.

        Возвращает:
            bool:
        """
        return len(self.content) == 0

    # Методы для работы с базой дыннах
    @staticmethod
    def byId(replie_id, localbase=None):
        """
        Метод читает ответ на пост с базы данных.

        Параметры:
            replies_id (int):Индетификатор ответа.
            localbase (oapi.base.localBase):Локальная база из которой производится чтение.
        """
        if localbase != None:
            return localbase.lbReplies.get(replie_id)
        else:
            return replie()

    @staticmethod
    def byIds(listid=[], localbase=None):
        """
        Метод расширение для метода byId, но вместо одного читает сразу список ответов на пост.

        Параметры:
            listid (list):Список индетефикаторов ответов которые необходимо прочитать из базы.
            localbase (oapi.base.localBase):Локальная база из которой производится чтение ответов.
        """
        result = list()
        for t in listid:
            result.append(replie.byId(t, localbase))
        return result

    def contains(self, localbase=None):
        """
        Функция вернёт истину, если данный индетефикатор ответа содержится в локальной базе localbase.

        Параметры:
            localbase (oapi.base.localBase):Локальная база в которой производится проверка.
        """
        return localbase.lbReplies.contains(self.id)

    def push(self, localbase=None):
        """
        Метод помещает содержимое этого ответа в локальную базу.

        Параметры:
            localbase (oapi.base.localBase):Локальная база в которую помещается содержимое данного ответа.
        """
        localbase.lbReplies.push(self.id, self.content)

    @staticmethod
    def pushs(replies, localbase=None):
        """
        Метод расширение для метода push, но вместо одного профиля он помещает сразу целый список.

        Параметры:
            replies (list):Список профилей которые необходимо записать в локальную базу.
            localbase (oapi.base.localBase):Локальная база в которую производится запись профилей.
        """
        for r in replies:
            r.push(localbase)

    # api сайта
    @staticmethod
    def top(user_id=0, limit=200, session=None):
        """
        Читает ленту ответов профиля начиная с позиции pos, если данная позиция равна нулю, то читает с последнего данного ответа в списке.

        Параметры:
            user_id (int):Уникальный индетификатор профиля.
            pos (int):Позиция с которой начинается чтение(уникальный индетефикатор ответа в цепочки ответов данных пользователем).
            limit (int):Количество которое будем читать за раз(сервер имеет ограничение так что больше 20-40 за раз прочитать наврядли получистя).
            session (requests.Session):Сессия которая используется при отправки GET запросов к серверу.

        Возврощает:
            list:Список ответов данных пользователем.
        """
        content = get(
            f'topic/profile/{user_id}/replies?userID={user_id}&dir=0&pos=0&limit={limit}&storage=profile-{user_id}-replies',
            session)
        replies = content['result']['replies']
        if replies == None:
            return []
        result = list()
        for r in replies:
            repl = replie(content=r)
            if not repl.empty:
                result.append(repl)
        return result

    @staticmethod
    def read(user_id=0, pos=0, limit=200, session=None):
        """
        Читает ленту ответов профиля начиная с позиции pos, если данная позиция равна нулю, то читает с последнего данного ответа в списке.

        Параметры:
            user_id (int):Уникальный индетификатор профиля.
            pos (int):Позиция с которой начинается чтение(уникальный индетефикатор ответа в цепочки ответов данных пользователем).
            limit (int):Количество которое будем читать за раз(сервер имеет ограничение так что больше 20-40 за раз прочитать наврядли получистя).
            session (requests.Session):Сессия которая используется при отправки GET запросов к серверу.

        Возврощает:
            list:Список ответов данных пользователем.
        """
        content = get(
            f'topic/profile/{user_id}/replies?userID={user_id}&dir=1&pos={pos}&limit={limit}&storage=profile-{user_id}-replies',
            session)
        replies = content['result']['replies']
        if replies == None:
            return []
        result = list()
        for r in replies:
            repl = replie(content=r)
            if not repl.empty:
                result.append(repl)
        return result

    def parse(prof=None, pos=0, limit=20, bar_update=None, session=None):
        result = list()
        if pos == 0:
            buffer = replie.top(user_id=prof.id, limit=200, session=session)
        else:
            buffer = replie.read(user_id=prof.id, pos=pos, limit=200, session=session)
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
                prof.replies_id.extend(topic.listid(result))
                return result

        if bar_update != None:
            bar_update(index)
        while True:
            index = 0
            pos = result[-1].id
            buffer = replie.read(user_id=prof.id, pos=pos, limit=200, session=session)
            if buffer == []:
                prof.replies_id.extend(topic.listid(result))
                return result
            for r in buffer:
                result.append(r)
                count += 1
                index += 1
                if count == limit:
                    if bar_update != None:
                        bar_update(index)
                    prof.replies_id.extend(topic.listid(result))
                    return result
            if bar_update != None:
                bar_update(index)

    def loadAnswer(self, session=None):
        """
        Метод загружает все ответы под этим ответом с сервера, а также записывает новое поле в контент answer, в котором будут хранится все индетификаторы ответов на этот ответ,поэтому следует перезаписать данный ответ в базу, если он уже там имеется.

        Возвращает:
            list:Список ответов.
        """
        replies = get(
            f'topic/answers/{self.topic_id}?reply_id={self.id}&limit={self.replyToReplyCount}&dir=0&sort=id&order_by=asc',
            session)
        if len(replies) == 0:
            return []
        if replies['result']['replies'] == None:
            replies['result']['replies'] = []
        result = list()
        for r in replies['result']['replies']:
            result.append(replie(r))
        self.content['answer'] = replie.listid(result)
        return result

    @staticmethod
    def print(replies):
        """
        Метод выводит в консоль базовую информацию об ответе.
        """
        for r in replies:
            if r.validity:
                print(r.id, r.topic_id, r.created_at, r.texts)
            else:
                print('?', '?', '?')

    @staticmethod
    def authors(replies):
        result = list()
        for r in replies:
            prof = r.author
            if not prof in result:
                result.append(r.author)
        return result

    @staticmethod
    def listid(replies):
        """
        Метод преобразует список ответов в список их индетификаторов.

        Возвращает:
            list:Список индетификаторов.
        """
        result = list()
        for r in replies:
            result.append(r.id)
        return result

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

    def __getitem__(self, attr):
        return self.content[attr]

    def __setitem__(self, attr, value):
        self.content[attr] = value

    def __str__(self):
        if self.validity:
            return f'{self.id} {self.topic_id} {self.created_at} {self.texts}'
        else:
            return '? ? ? ?'


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
        for i in range(limit // interval):
            sublist, tid = topic.Main(tid, interval, session=session)
            if sublist == []:
                return result
            result.extend(sublist)
        for i in range(limit % interval):
            sublist, tid = topic.Main(tid, interval, session=session)
            if sublist == []:
                return result
            result.extend(sublist)
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
                self.content['answer'] = replie.listid(result)
                return result
            result.extend(buffer)
            replies = buffer

    @staticmethod
    def pushs(topics, localbase=None):
        """
        Метод расширение для метода push, но вместо одного поста он помещает сразу целый список.

        Параметры:
            replies (list):Список постов которые необходимо записать в локальную базу.
            localbase (oapi.base.localBase):Локальная база в которую производится запись постов.
        """
        for t in topics:
            t.push(localbase)

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
