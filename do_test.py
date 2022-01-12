#!/usr/bin/env python
import json
import time
import logging
import hashlib
import socket
import ssl
import warnings
warnings.simplefilter('ignore')

import requests
from requests.exceptions import RequestException
import arrow
import elasticsearch
from elasticsearch.connection import create_ssl_context
import netifaces as ni


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('tester')
URL = 'http://checkip.brainwire.ca'


_es = None


def connect_es():
    global _es
    if not _es:
        es_hosts = ['https://elastic:admin159@204.209.29.10:9200']
        context = create_ssl_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        _es = elasticsearch.Elasticsearch(hosts=es_hosts,
                                          ssl_context=context)
    return _es


def record_data_es(document):
    es = connect_es()
    index_name = 'outage-tracking'
    exists = es.indices.exists(index=index_name)
    if not exists:
        raise ValueError(f'Index {index_name} does not exist')
    return es.index(index=index_name, document=document)


MY_HOSTNAME = 'test-client'
INTERFACE = 'eth0'


def do_test():
    if MY_HOSTNAME == 'test-client':
        raise ValueError(f'Cannot post to Elasticsearch with hostname test-client')
    my_ip_address = [x['addr'] for x in ni.ifaddresses(INTERFACE)[ni.AF_INET]][0]

    r_session = requests.Session()
    r_session.headers['Connection'] = 'close'  # disable keep-alive

    while True:
        data_result = {'time': arrow.now().isoformat(),
                       'hostname': MY_HOSTNAME,
                       'local_ip': my_ip_address,
                       'url': URL,
                       'response_code': None,
                       'response_hash': None,
                       'response_snippet': None,
                       'error': None}
        try:
            result = r_session.get(URL)
            result.raise_for_status()
            data_result['response_code'] = result.status_code
            data_result['response_hash'] = hashlib.md5(result.text.encode('utf8')).hexdigest()
            try:
                data_result['response_snippet'] = result.text[:50].strip()
            except Exception as exc:
                logger.exception('Error saving response_snippet')
                pass
        except Exception as exc:
            data_result['error'] = f'{type(exc)}: {str(exc)}'

        try:
            record_data_es(data_result)
        except Exception as exc:
            logger.exception('Error posting result to ES')

        time.sleep(1)


if __name__ == '__main__':
    connect_es()
    do_test()
