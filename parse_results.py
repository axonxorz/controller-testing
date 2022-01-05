#!/usr/bin/env python
import json
import time
import logging
import hashlib

import requests
from requests.exceptions import RequestException
import arrow


logging.basicConfig()
logger = logging.getLogger('parse_output')
DATA_OUTPUT = '/home/ubuntu/results.json'


def parse_results():

    response_hashes = {}
    response_snippets = {}

    with open(DATA_OUTPUT, 'r', encoding='utf8') as fd:
        lines = fd.read().split('\n')
        for line_no, line in enumerate(lines, start=1):
            if not line: continue
            try:
                r = json.loads(line)
                response_hashes[r['response_hash']] = True
                response_snippets[r['response_snippet']] = True
            except Exception as exc:
                print(f'line_no={line_no}')
                raise exc

    print(response_hashes)
    print(response_snippets)

if __name__ == '__main__':
    parse_results()
