import threading
import datetime
import csv
import os

WRITE_INTERVAL = 900 # 15 minutes
BASE_DIR = os.environ.get("BASE_DIR")

COMMENT_FIELD_NAMES = ['created_utc', 'id', 'author', 'body', 'link_id', 'parent_id', 'permalink', 'score', 'distinguished', 'tickers']
SUBMISSION_FIELD_NAMES = ['created_utc', 'id', 'author', 'title', 'name', 'body', 'permalink', 'score', 'distinguished', 'is_original_content', 'link_flair_template_id', 'link_flair_text', 'url', 'tickers']

class FileWriter(threading.Thread):
    def __init__(self, queue, sub_reddit, data_type):
        threading.Thread.__init__(self)
        self.queue = queue
        self.data_type = data_type
        self.sub_reddit = sub_reddit
        if self.data_type == 'comments':
            self.fieldnames = COMMENT_FIELD_NAMES
        elif self.data_type == 'submissions':
            self.fieldnames = SUBMISSION_FIELD_NAMES

    def run(self):
        while True:
            d = self.queue.get()
            if d == 'quit':
                break
            self.write(d)

    def write(self, data):
        dt = datetime.datetime.utcnow()
        folder = BASE_DIR + '/data/' + dt.strftime("%Y%m%d")

        if not os.path.exists(folder):
            os.makedirs(folder)

        # replace author object with just author id
        data['author'] = data['author']['id']
        data['tickers'] = "|".join(data['tickers'])

        dt_str = dt.strftime("%Y%m%d%H") + str(dt.minute - (dt.minute % 10))
        filename = f'{folder}/{self.sub_reddit}_{self.data_type}_{dt_str}.txt'

        with open(filename, 'a', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, fieldnames=self.fieldnames, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            w.writerow(data)

