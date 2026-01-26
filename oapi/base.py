import oapi.interface as api
from tqdm import tqdm
from oapi.jdict import jdict
from datetime import datetime


class localTopicBase(jdict):
    def __init__(self):
        super().__init__()

    def load(self, listid):
        for i in tqdm(range(len(listid))):
            tid = listid[i]
            if not super().contains(tid):
                value = topic.readAll(tid)
                super().push(tid, value)

    def get(self, topic_id):
        return api.topic(content=super().get(topic_id))

    def restore(self, barload=True):
        super().beginRestore()
        bar = tqdm(desc="Востановление ключей", unit="key", miniters=100)
        while True:
            content, pos = super().next()
            if len(content) == 0:
                return
            else:
                topi = api.topic(content=content)
                super().rekey(topi.id, pos)
                bar.update(1)


class localReplieBase(jdict):
    def __init__(self):
        super().__init__()

    def loadFromTopics(self, listid, ltb):
        for i in tqdm(range(len(listid))):
            tid = listid[i]
            if ltb.contains(tid):
                topi = ltb.get(tid)
                answers = topi.allAnswer
                for a in answers:
                    super().push(a.id, a.content)

    def get(self, replie_id):
        return api.replie(content=super().get(replie_id))


class localProfileBase(jdict):
    def __init__(self):
        super().__init__()

    def loadFromReplies(self, listid, lrb):
        for i in tqdm(range(len(listid))):
            tid = listid[i]
            if lrb.contains(tid):
                repl = lrb.get(tid)
                prof = profile(content=repl.author)
                if prof.content != None:
                    super().push(prof.id, prof.content)

    def loadFromTopics(self, listid, ltb):
        for i in tqdm(range(len(listid))):
            tid = listid[i]
            if ltb.contains(tid):
                topi = ltb.get(tid)
                prof = profile(content=topi.author)
                if prof.content != None:
                    super().push(prof.id, prof.content)

    def get(self, profile_id):
        return api.profile(content=super().get(profile_id))


class localProfileRepliesIdBase(jdict):
    def __init__(self):
        super().__init__()


class localProfileTopicsIdBase(jdict):
    def __init__(self):
        super().__init__()


class localBase:
    def __init__(self, path):
        self.path = path
        self.lbProfile = localProfileBase()
        self.lbTopics = localTopicBase()
        self.lbReplies = localReplieBase()
        self.lbProfTopsId = localProfileTopicsIdBase()
        self.lbProfRepsId = localProfileRepliesIdBase()

    def connect(self):
        self.lbProfile.connect(f'{self.path}.profiles')
        self.lbTopics.connect(f'{self.path}.topics')
        self.lbReplies.connect(f'{self.path}.replies')
        self.lbProfTopsId.connect(f'{self.path}.proftops')
        self.lbProfRepsId.connect(f'{self.path}.profreps')

    def close(self):
        self.lbProfile.close()
        self.lbTopics.close()
        self.lbReplies.close()
        self.lbProfTopsId.close()
        self.lbProfRepsId.close()

    def flush(self):
        self.lbProfile.flush()
        self.lbTopics.flush()
        self.lbReplies.flush()
        self.lbProfTopsId.flush()
        self.lbProfRepsId.flush()

    def topics_id(self):
        return list(self.lbTopics.dpos.keys())

    def replies_id(self):
        return list(self.lbReplies.dpos.keys())

    def profiles_id(self):
        return list(self.lbProfile.dpos.keys())

    def firstTopic(self):
        topics_id = self.topics_id()
        topi = api.topic.byId(topics_id[0], self)
        dt1 = datetime.fromisoformat(topi['created_at'])
        for t in topics_id:
            topi = api.topic.byId(t, self)
            dt2 = datetime.fromisoformat(topi['created_at'])
            if dt1 > dt2:
                tid = t
                dt1 = dt2
        return tid

    def backTopic(self):
        topics_id = self.topics_id()
        topi = api.topic.byId(topics_id[0], self)
        dt1 = datetime.fromisoformat(topi['created_at'])
        for t in topics_id:
            topi = api.topic.byId(t, self)
            dt2 = datetime.fromisoformat(topi['created_at'])
            if dt1 < dt2:
                tid = t
                dt1 = dt2
        return tid

    def clear(self):
        self.lbProfile.clear()
        self.lbTopics.clear()
        self.lbReplies.clear()
        self.lbProfTopsId.clear()
        self.lbProfRepsId.clear()

    def union(self, un=None, bar_update=None):
        profiles_id = un.profiles_id()
        for p in profiles_id:
            if not self.lbProfile.contains(p):
                self.lbProfile.push(p, un.lbProfile.get(p).content)
                self.lbProfTopsId.push(p, un.lbProfTopsId.get(p))
                self.lbProfRepsId.push(p, un.lbProfRepsId.get(p))
            if bar_update != None:
                bar_update(1)

        topics_id = un.topics_id()
        for p in topics_id:
            if not self.lbTopics.contains(p):
                self.lbTopics.push(p, un.lbTopics.get(p).content)
            if bar_update != None:
                bar_update(1)

        replies_id = un.replies_id()
        for p in replies_id:
            if not self.lbReplies.contains(p):
                self.lbReplies.push(p, un.lbReplies.get(p).content)
            if bar_update != None:
                bar_update(1)

    """
    def clone(self,path):
    def union(self,localBase):
    def clear(self):
    def move(self,path):
    def 
    """