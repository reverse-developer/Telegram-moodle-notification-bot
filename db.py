#!/usr/bin/env python3

import redis
from walrus import Cache, Database

db = redis.Redis(db=0)

cache = Cache(Database(host='localhost', port=6379, db=0))


@cache.cached(timeout=3600)
def get_id(uuid):
    return db.hget(uuid, 'id').decode()


@cache.cached(timeout=3600)
def get_passwd(uuid):
    return db.hget(uuid, 'passwd').decode()


def get_tasks_from_db(uuid):
    """ Returns `set` of tasks names """
    tasks = db.smembers(f'{uuid}:tasks')
    return set(task.decode() for task in tasks)


def set_id(uuid, id):
    get_id.bust()
    db.hset(uuid, 'id', id)


def set_passwd(uuid, passwd):
    get_passwd.bust()
    db.hset(uuid, 'passwd', passwd)


def set_tasks(uuid, set_of_tasks):
    for task in set_of_tasks:
        db.sadd(f'{uuid}:tasks', task)


def remove_task(uuid, task):
    db.srem(f'{uuid}:tasks', task)
