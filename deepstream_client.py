import requests
import json
import threading
import praw
import prawcore
import datetime
import redis
import os
from utilities import get_ticker_symbols, remove_punctuation
from context_extractor import extract_company

URL = 'http://localhost:6020/api'

headers = {
    'Content-Type': 'application/json'
}

stop_words = {'the','to','and','a','i','of','is','in','this','you','for','on','are','it','that','my','will','be','they','have','at','but','or','with','we','what','all','buy','if','their','shares','just','not','short','🚀🚀🚀🚀','up','so','has','your','stock','do','can','now','like','from','was','who','some','squeeze',"i'm",'going','get','me','as','when','price','out','about','people','been','because','think','new','sell','by','am','bb','money','go','one','next','after','would','only','more','hedge','know','into','those','need','there','our','market'}


class DeepstreamClient(threading.Thread):
    def __init__(self, queue, file_writer_queue=None):
        threading.Thread.__init__(self)
        self.queue = queue
        self.ticker_list = None
        self.file_writer_queue = file_writer_queue
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, password=os.environ.get("REDIS_PASSWORD"))

    def run(self):
        self.ticker_list = get_ticker_symbols()

        while True:
            d = self.queue.get()
            if d == 'quit':
                break

            if type(d) is praw.models.reddit.submission.Submission:
                self.process_submission(d)
            elif type(d) is praw.models.reddit.comment.Comment:
                self.process_comment(d)
        self.file_writer_queue.put('quit')

    def process_submission(self, d):
        title = d.title
        selftext = d.selftext
        tickers = set()
        orgs, tokens = extract_company(id=d.id, text=title)

        for t in orgs + tokens:
            t = t.lower()
            if t in self.ticker_list:
                tickers.add(t)

        orgs, tokens = extract_company(id=d.id, text=selftext)
        for t in orgs + tokens:
            t = t.lower()
            if t in self.ticker_list:
                tickers.add(t)


        try:
            data = {
                'author': {
                    'id': d.author.id,
                    'created_utc': d.author.created_utc,
                    'name': d.author.name,
                    'comment_karma': d.author.comment_karma,
                    'link_karma': d.author.link_karma,
                    'is_mod': d.author.is_mod,
                    'is_employee': d.author.is_employee,
                    'is_friend': d.author.is_friend,
                    'is_gold': d.author.is_gold,
                    'has_verified_email': d.author.has_verified_email,
                },
                'id': d.id,
                'title': d.title,
                'name': d.name,
                'body': d.selftext,
                'created_utc': d.created_utc,
                'permalink': d.permalink,
                'score': d.score,
                'distinguished': d.distinguished,
                'is_original_content': d.is_original_content,
                'link_flair_template_id': d.link_flair_template_id,
                'link_flair_text': d.link_flair_text,
                'url': d.url,
                'tickers': list(tickers)
            }



            self.post(data, 'submissions')
            if self.file_writer_queue:
                self.file_writer_queue.put(data)

        except prawcore.exceptions.NotFound as e:
            print("PRAW Exception")
            print(e)
            print(d.id)

    def process_comment(self, d):
        dt = datetime.datetime.utcnow()
        one_hour_before = dt - datetime.timedelta(hours=1)
        tickers = set()
        orgs, tokens = extract_company(id=d.id, text=d.body)

        for t in orgs + tokens:
            t = t.lower()
            if t in self.ticker_list:
                tickers.add(t)

        try:
            data = {
                'author': {
                    'id': d.author.id,
                    'created_utc': d.author.created_utc,
                    'name': d.author.name,
                    'comment_karma': d.author.comment_karma,
                    'link_karma': d.author.link_karma,
                    'is_mod': d.author.is_mod,
                    'is_employee': d.author.is_employee,
                    'is_friend': d.author.is_friend,
                    'is_gold': d.author.is_gold,
                    # 'is_suspended': d.author.is_suspended,
                    'has_verified_email': d.author.has_verified_email,
                },
                'id': d.id,
                'body': d.body,
                'created_utc': d.created_utc,
                'link_id': d.link_id,
                'parent_id': d.parent_id,
                'permalink': d.permalink,
                'score': d.score,
                'distinguished': d.distinguished,
                'tickers': list(tickers)
            }

            key = d.author.id + '_author'
            self.redis_client.zadd(key, {d.id: d.created_utc})
            one_hour_post_count = self.redis_client.zcount(key, int(one_hour_before.timestamp()), int(dt.timestamp()))
            data['author']['one_hour_post_count'] = one_hour_post_count
            self.post(data, "comments")

            if self.file_writer_queue:
                self.file_writer_queue.put(data)

        except prawcore.exceptions.NotFound as e:
            print("PRAW Exception")
            print(e)
            print(d.id)



    def post(self, data, data_type):
        body = {
            'body': [
                {
                    "topic": "event",
                    "action": "emit",
                    "eventName": data_type,
                    "data": data
                }
            ]
        }

        # print(json.dumps(body, indent=2))

        r = requests.post(URL, json.dumps(body), headers=headers)
        if r.status_code != 200:
            print(r.status_code, r.content)
