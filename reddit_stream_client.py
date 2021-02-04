import praw
from prettytable import PrettyTable
import textwrap
import datetime
from praw.models import MoreComments

import threading, queue
import time
import json
import csv
import os
import argparse
import logging

from deepstream_client import DeepstreamClient
from file_writer import FileWriter

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')
user_agent = f'linux:pyredditclient:0.0.1 (by /u/{username}'


reddit = praw.Reddit(client_id=client_id, client_secret=client_secret,
                     password=password, user_agent=user_agent,
                     username=username)
reddit.read_only = True


def get_submissions(pull_type=None, sub_reddit=None, flair=None, q=None):
    wsb = reddit.subreddit(sub_reddit)
    for c in wsb.stream.submissions():
        q.put(c)
        break


def get_comments(pull_type=None, sub_reddit=None, submission=None, flair=None, q=None):
    wsb = reddit.subreddit(sub_reddit)

    counter = 0
    cdata = []
    for c in wsb.stream.comments(skip_existing=True):
        q.put(c)
        counter += 1

    q.put('quit')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get reddit comments and submissions')
    parser.add_argument('--reddit', type=str)
    parser.add_argument('--type', type=str)
    parser.add_argument('--save', action='store_true')
    args = parser.parse_args()

    # handler = logging.StreamHandler()
    # handler.setLevel(logging.DEBUG)
    # for logger_name in ("praw", "prawcore"):
    #     logger = logging.getLogger(logger_name)
    #     logger.setLevel(logging.DEBUG)
    #     logger.addHandler(handler)

    sub_reddit = args.reddit

    fw_queue = None
    if args.save:
        fw_queue = queue.Queue()
        fw = FileWriter(fw_queue, sub_reddit=sub_reddit, data_type=args.type)
        fw.start()

    queue = queue.Queue()

    dsc = DeepstreamClient(queue, file_writer_queue=fw_queue)
    dsc.start()

    # sub_reddit = 'stocks'
    if args.type == 'comments':
        get_comments(sub_reddit=sub_reddit, q=queue)
    elif args.type == 'submissions':
        get_submissions(sub_reddit=sub_reddit, q=queue)
    else:
        queue.put('quit')

    dsc.join()

    if args.write:
        fw.join()



