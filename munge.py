#!/usr/bin/env python
# encoding: utf-8

import os
import json

from bs4 import BeautifulSoup


def parse_messages(input_file):
    msg_to = input_file[6:].split(' - ')[0]
    f = open(input_file, 'r')
    soup = BeautifulSoup(f.read(), 'html.parser')
    messages = soup.find_all('div', class_="message")
    final = []
    for message in messages:
        timestamp = message.abbr.get('title')
        number = message.find_all(class_='tel')[0].get('href').replace("tel:", "")
        sender = message.find_all(class_='tel')[0].find_all(class_='fn')[0].text
        content = message.q.text
        if sender == 'Me':
            to = msg_to
        else:
            to = 'Me'
        blob = {
            'timestamp': timestamp,
            'number': number,
            'sender': sender,
            'to': to,
            'content': content,
        }
        final.append(blob)
    return final


def get_files_list():
    files = os.listdir('Calls')
    files = ["Calls/{}".format(f) for f in files if 'Text' in f]
    return files


def main():
    messages = map(parse_messages, get_files_list())
    f = open('output.json', 'w')
    f.write(json.dumps(messages))

if __name__ == '__main__':
    main()
