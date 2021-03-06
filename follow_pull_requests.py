#!/usr/bin/env python

# from pdb import set_trace; set_trace()

import redis
import json
from github import Github
from datetime import datetime, timedelta
import config

# g = Github(config.username, config.password)
g = Github(config.pccibottoken)
r = redis.StrictRedis(host='localhost', port=6379, db=0)

# r.set('foo', 'bar')
# r.get('foo')


def totimestamp(dt, epoch=datetime(1970, 1, 1)):
    td = dt - epoch
    # return td.total_seconds()
    return int((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 1e6 )


repos = config.repos

for repo in repos:
    r.sadd('repos', str(repo))
    # from pdb import set_trace; set_trace()
    pulls = g.get_repo(repo).get_pulls()

    for pull in pulls:
        # from pdb import set_trace; set_trace()
        unique_name = repo + "/" + str(pull.number)
        current_merge_commit_sha = pull.merge_commit_sha
        raw = r.get(unique_name)

        print raw
        if raw is None:
            stored_pull = {}
            stored_pull['merge_commit_sha'] = ''
            stored_pull['name'] = unique_name
            stored_pull['number'] = str(pull.number)
            stored_pull['time'] = str(datetime.now())
        else:
            stored_pull = json.loads(raw)

        merge_commit_sha = stored_pull['merge_commit_sha']
        print unique_name
        print merge_commit_sha
        print current_merge_commit_sha
        if merge_commit_sha != current_merge_commit_sha:
            stored_pull['merge_commit_sha'] = current_merge_commit_sha
            job = {}
            job['unique_name'] = unique_name
            job['nodeset'] = 'trusty'
            r.rpush('todo', json.dumps(job))
            job['nodeset'] = 'centos7'
            r.rpush('todo', json.dumps(job))
        r.set(unique_name, json.dumps(stored_pull))
