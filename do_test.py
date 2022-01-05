#!/usr/bin/env python
import json
import time
import logging
import hashlib

import requests
from requests.exceptions import RequestException
import arrow


logging.basicConfig()
logger = logging.getLogger('tester')
URL = 'http://checkip.brainwire.ca'
DATA_OUTPUT = '/home/ubuntu/results.json'


def do_test():
    while True:
        data_result = {'time': arrow.now().format(),
                       'url': URL,
                       'response_code': None,
                       'response_hash': None,
                       'response_snippet': None,
                       'error': None}
        try:
            result = requests.get(URL)
            result.raise_for_status()
            print(result)
            data_result['response_code'] = result.status_code
            data_result['response_hash'] = hashlib.md5(result.text.encode('utf8')).hexdigest()
            try:
                data_result['response_snippet'] = result.text[:50].strip()
            except Exception as exc:
                logger.exception('Error saving response_snippet')
                pass
        except Exception as exc:
            data_result['error'] = f'{type(exc)}: {str(exc)}'

        logger.info(str(data_result))

        with open(DATA_OUTPUT, 'a', encoding='utf8') as fd:
            fd.write(json.dumps(data_result))
            fd.write('\n')

        time.sleep(1)


if __name__ == '__main__':
    do_test()
