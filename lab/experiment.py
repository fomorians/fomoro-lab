import os
import time
import random
import requests
import subprocess

ENV = os.environ.get('ENV', 'development')

if ENV == 'production':
    API_URL = 'https://api.fomoro.com/api/v0.1/experiments/{}/results'
else:
    API_URL = 'http://localhost:3000/api/v0.1/experiments/{}/results'
    # API_URL = 'http://dev.api.fomoro.com/api/0.1/experiments/{}/results'

def get_git_describe():
    return subprocess.check_output(['git', 'describe', '--always', '--dirty', '--abbrev=0'], stderr=subprocess.STDOUT)

class Experiment(object):
    def __init__(self, api_key, experiment_id):
        self.api_key = api_key
        self.experiment_id = experiment_id

        try:
            self.hash = get_git_describe().strip()
            self.dirty = False

            if self.hash.endswith('-dirty'):
                print('WARNING: You have uncommitted changes.')
                self.hash = self.hash[:-len('-dirty')]
                self.dirty = True

        except subprocess.CalledProcessError as e:
            print('Failed to retrieve current git commit hash.')
            print('Make sure you are running inside of git repo and committed.')

        self.reset()

    def reset(self):
        self.start_time = None
        self.end_time = None
        self.loss = None

    def begin(self):
        self.start_time = time.time()

    def end(self):
        self.end_time = time.time()

    def iter(self, iterable, total=None):
        self.begin()

        if total is None:
            try:
                total = len(iterable)
            except TypeError:
                total = None

        for obj in iterable:
            yield obj

        self.end()

    def report(self, loss, accuracy=None):
        api_url = API_URL.format(self.experiment_id)

        json = {
            "hash": self.hash,
            "dirty": self.dirty,
            "loss": random.random(),
        }

        headers = {
            'Authorization': 'Bearer {}'.format(self.api_key)
        }

        r = requests.post(api_url, json=json, headers=headers)
        if r.status_code == 200:
            print(r.json())
        else:
            print(r.text)
