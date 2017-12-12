# -*- coding: utf-8 -*-

import os

from elasticsearch5.helpers import bulk
from elasticsearch5.helpers.test import SkipTest, get_test_client
from mock import Mock
from pytest import fixture, skip

from elasticsearch5_dsl.connections import connections
from .test_integration.test_data import DATA, create_git_index


@fixture(scope='session')
def client(request):
    try:
        connection = get_test_client(nowait='WAIT_FOR_ES' not in os.environ)
        connections.add_connection('default', connection)
        return connection
    except SkipTest:
        skip()

@fixture
def write_client(request, client):
    yield client
    client.indices.delete('test-*', ignore=404)
    client.indices.delete_template('test-template', ignore=404)

@fixture
def mock_client(request):
    client = Mock()
    client.search.return_value = dummy_response()
    connections.add_connection('mock', client)
    yield client
    connections._conn = {}
    connections._kwargs = {}

@fixture(scope='session')
def data_client(request, client):
    # create mappings
    create_git_index(client, 'git')
    # make sure we clean up after ourselves
    request.addfinalizer(lambda: client.indices.delete('git'))
    # load data
    bulk(client, DATA, raise_on_error=True, refresh=True)
    return client

@fixture
def dummy_response():
    return {
      "_shards": {
        "failed": 0,
        "successful": 10,
        "total": 10
      },
      "hits": {
        "hits": [
          {
            "_index": "test-index",
            "_type": "company",
            "_id": "elasticsearch",
            "_score": 12.0,

            "_source": {
              "city": "Amsterdam",
              "name": "Elasticsearch",
            },
          },
          {
            "_index": "test-index",
            "_type": "employee",
            "_id": "42",
            "_score": 11.123,
            "_parent": "elasticsearch",

            "_source": {
              "name": {
                "first": "Shay",
                "last": "Bannon"
              },
              "lang": "java",
              "twitter": "kimchy",
            },
          },
          {
            "_index": "test-index",
            "_type": "employee",
            "_id": "47",
            "_score": 1,
            "_parent": "elasticsearch",

            "_source": {
              "name": {
                "first": "Honza",
                "last": "Král"
              },
              "lang": "python",
              "twitter": "honzakral",
            },
          },
          {
            "_index": "test-index",
            "_type": "employee",
            "_id": "53",
            "_score": 16.0,
            "_parent": "elasticsearch",
          },
        ],
        "max_score": 12.0,
        "total": 123
      },
      "timed_out": False,
      "took": 123
    }

@fixture
def aggs_search():
    from elasticsearch5_dsl import Search
    s = Search(index='git', doc_type='commits')
    s.aggs\
        .bucket('popular_files', 'terms', field='files', size=2)\
        .metric('line_stats', 'stats', field='stats.lines')\
        .metric('top_commits', 'top_hits', size=2, _source=["stats.*", "committed_date"])
    s.aggs.bucket('per_month', 'date_histogram', interval='month', field='info.committed_date')
    s.aggs.metric('sum_lines', 'sum', field='stats.lines')
    return s

@fixture
def aggs_data():
    return {
        'took': 4,
        'timed_out': False,
        '_shards': {'total': 1, 'successful': 1, 'failed': 0},
        'hits': {'total': 52, 'hits': [], 'max_score': 0.0},
        'aggregations': {
            'sum_lines': {'value': 25052.0},
            'per_month': {
                'buckets': [
                    {'doc_count': 38, 'key': 1393632000000, 'key_as_string': '2014-03-01T00:00:00.000Z'},
                    {'doc_count': 11, 'key': 1396310400000, 'key_as_string': '2014-04-01T00:00:00.000Z'},
                    {'doc_count': 3, 'key': 1398902400000, 'key_as_string': '2014-05-01T00:00:00.000Z'},
                ]
            },
            'popular_files': {
                'buckets': [
                    {
                        'key': 'elasticsearch_dsl',
                        'line_stats': {'count': 40, 'max': 228.0, 'min': 2.0, 'sum': 2151.0, 'avg': 53.775},
                        'doc_count': 40,
                        'top_commits': {
                            'hits': {
                                'total': 40,
                                'hits': [
                                    {
                                        '_id': '3ca6e1e73a071a705b4babd2f581c91a2a3e5037',
                                        '_type': 'commits',
                                        '_source': {
                                            'stats': {'files': 4, 'deletions': 7, 'lines': 30, 'insertions': 23},
                                            'committed_date': '2014-05-02T13:47:19'
                                        },
                                        '_score': 1.0,
                                        '_parent': 'elasticsearch-dsl-py',
                                        '_routing': 'elasticsearch-dsl-py',
                                        '_index': 'git'
                                    },
                                    {
                                        '_id': 'eb3e543323f189fd7b698e66295427204fff5755',
                                        '_type': 'commits',
                                        '_source': {
                                            'stats': {'files': 1, 'deletions': 0, 'lines': 18, 'insertions': 18},
                                            'committed_date': '2014-05-01T13:32:14'
                                        },
                                        '_score': 1.0,
                                        '_parent': 'elasticsearch-dsl-py',
                                        '_routing': 'elasticsearch-dsl-py',
                                        '_index': 'git'
                                    }
                                ],
                                'max_score': 1.0
                            }
                        }
                    },
                    {
                        'key': 'test_elasticsearch_dsl',
                        'line_stats': {'count': 35, 'max': 228.0, 'min': 2.0, 'sum': 1939.0, 'avg': 55.4},
                        'doc_count': 35,
                        'top_commits': {
                            'hits': {
                                'total': 35,
                                'hits': [
                                    {
                                        '_id': '3ca6e1e73a071a705b4babd2f581c91a2a3e5037',
                                        '_type': 'commits',
                                        '_source': {
                                            'stats': {'files': 4, 'deletions': 7, 'lines': 30, 'insertions': 23},
                                            'committed_date': '2014-05-02T13:47:19'
                                        },
                                        '_score': 1.0,
                                        '_parent': 'elasticsearch-dsl-py',
                                        '_routing': 'elasticsearch-dsl-py',
                                        '_index': 'git'
                                    }, {
                                        '_id': 'dd15b6ba17dd9ba16363a51f85b31f66f1fb1157',
                                        '_type': 'commits',
                                        '_source': {
                                            'stats': {'files': 3, 'deletions': 18, 'lines': 62, 'insertions': 44},
                                            'committed_date': '2014-05-01T13:30:44'
                                        },
                                        '_score': 1.0,
                                        '_parent': 'elasticsearch-dsl-py',
                                        '_routing': 'elasticsearch-dsl-py',
                                        '_index': 'git'
                                    }
                                ],
                                'max_score': 1.0
                            }
                        }
                    }
                ],
                'doc_count_error_upper_bound': 0,
                'sum_other_doc_count': 120
            }
        }
    }
