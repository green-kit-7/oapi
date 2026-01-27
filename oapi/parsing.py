from oapi.interface import topic, replie, profile
from oapi.jdict import jdict
from oapi.base import localBase

import json
import os
import traceback
from tqdm import tqdm
import difflib
import requests
from datetime import datetime

import threading


def parserMain(lb=None, id_begin=0, id_end=0, limitsave=100, bar_proc=None, session=None):
    tid = id_begin
    while True:
        topics = topic.main(tid, 40, 40, barload=False, session=session)
        for t in topics:
            if not t.contains(lb):
                t.push(lb)
        if bar_proc != None:
            bar_proc(40)
        lb.flush()
        if topics != []:
            tid = topics[-1].id
        if tid <= id_end or tid <= 4:
            break


def processParsingMain(nums, bar_update=None, proxies=None):
    num = int(nums)
    session = requests.Session()
    if proxies != None:
        session.proxies = proxies
    global bar
    if not os.path.exists(f'bases/base{num}'):
        os.mkdir(f'bases/base{num}')

    # oapi.interface.setSession(s)
    lb = localBase(f'bases/base{num}/base{num}')
    lb.connect()
    try:

        start_id = (num + 1) * 10000
        end_id = num * 10000

        parserMain(lb, start_id, end_id, bar_proc=bar_update, session=session)

    except:
        lb.flush()
        lb.close()
        traceback.print_exc()
    finally:
        lb.close();


def multyParsingMain(num=0, parallcount=1, bar_update=None, proxies_list=[]):
    threads = list()
    for i in range(parallcount):
        proxies = None
        if proxies_list != []:
            proxies = proxies_list[i]

        threads.append(
            threading.Thread(target=processParsingMain, args=(i + num, bar_update, proxies))
        )
        threads[i].start()

    for i in range(parallcount):
        threads[i].join()
