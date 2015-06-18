# -*- coding: utf-7 -*-
import json
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model

from rest_framework.reverse import reverse

User = get_user_model()

__all__ = [
    'CubesApiIndex', 'CubesVersionAPI', 'CubesInfoAPI',
    'CubeListAPI', 'CubeModelAPI', 'CubeAggregationAPI',
    'CubeCellAPI', 'CubeFactsAPI', 'CubeFactAPI',
    'CubeMembersAPI'
]


class BaseCubesAPITest(TransactionTestCase):
    url_name = None
    url_args = {}
    method = None
    maxDiff = None

    def setUp(self):
        super(BaseCubesAPITest, self).setUp()
        self.username = 'jadice'
        self.password = 'teste'
        self.user = User.objects.create(
            username=self.username,
            first_name='Jadice',
            last_name='Karai',
            email='jadicekarai@example.test',
        )
        self.user.set_password(self.password)
        self.user.save()

    def make_request(self, url=None, data=None):
        if url is None:
            url = reverse(self.url_name, kwargs=self.url_args)
        return getattr(self.client, self.method)(url)

    def login(self):
        self.client.login(username=self.username, password=self.password)

    def test_requires_authentication(self):
        response = self.make_request()
        self.assertEquals(response.status_code, 403)


class CubesApiIndex(BaseCubesAPITest):
    url_name = 'index'
    method = 'get'

    def test_api_request(self):
        self.login()
        response = self.make_request()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'cubes/index.html')


class CubesVersionAPI(BaseCubesAPITest):
    url_name = 'version'
    method = 'get'

    def test_api_request(self):
        self.login()
        response = self.make_request()
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content, {
            "version": "1.0.1",
            "server_version": "1.0.1",
            "api_version": 2
        })


class CubesInfoAPI(BaseCubesAPITest):
    url_name = 'info'
    method = 'get'

    def test_api_request(self):
        self.login()
        response = self.make_request()
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content, {
            'api_version': 2,
            'cubes_version': u'1.0.1',
            'first_weekday': 0,
            'timezone': u'CDT'
        })


class CubeListAPI(BaseCubesAPITest):
    url_name = 'cubes'
    method = 'get'

    def test_api_request(self):
        self.login()
        response = self.make_request()
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content, [{
            'info': {'min_date': '2010-01-01', 'max_date': '2010-12-31'},
            'label': 'irbd_balance', 'category': None, 'name': 'irbd_balance'
        }])


class CubeModelAPI(BaseCubesAPITest):
    url_name = 'cube_model'
    url_args = {'cube_name': 'irbd_balance'}
    method = 'get'

    def test_api_request(self):
        self.login()
        response = self.make_request()
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content, {
            'aggregates': [
                {
                    'function': 'sum', 'info': {}, 'label': 'Sum of Amount',
                    'measure': 'amount', 'name': 'amount_sum', 'ref': 'amount_sum'
                },
                {
                    'function': 'count', 'info': {}, 'label': 'Record Count',
                    'name': 'record_count', 'ref': 'record_count'
                }
            ],
            'details': [],
            'dimensions': [
                {
                    'default_hierarchy_name': 'default',
                    'has_details': True,
                    'hierarchies': [{'info': {}, 'levels': ['category', 'subcategory', 'line_item'], 'name': 'default'}],
                    'info': {},
                    'is_flat': False,
                    'levels': [
                        {
                            'attributes': [
                                {'info': {}, 'locales': [], 'name': 'category', 'ref': 'item.category'},
                                {'info': {}, 'locales': [], 'name': 'category_label', 'ref': 'item.category_label'}
                            ],
                            'info': {},
                            'key': 'category',
                            'label': 'Category',
                            'label_attribute': 'category_label',
                            'name': 'category',
                            'order_attribute': 'category'
                        },
                        {
                            'attributes': [
                                {'info': {}, 'locales': [], 'name': 'subcategory', 'ref': 'item.subcategory'},
                                {'info': {}, 'locales': [], 'name': 'subcategory_label', 'ref': 'item.subcategory_label'}
                            ],
                            'info': {},
                            'key': 'subcategory',
                            'label': 'Sub-category',
                            'label_attribute': 'subcategory_label',
                            'name': 'subcategory',
                            'order_attribute': 'subcategory'
                        },
                        {
                            'attributes': [{'info': {}, 'locales': [], 'name': 'line_item', 'ref': 'item.line_item'}],
                            'info': {},
                            'key': 'line_item',
                            'label': 'Line Item',
                            'label_attribute': 'line_item',
                            'name': 'line_item',
                            'order_attribute': 'line_item'
                        }
                    ],
                    'name': 'item'
                },
                {
                    'default_hierarchy_name': 'default',
                    'has_details': False,
                    'hierarchies': [{'info': {}, 'levels': ['year'], 'name': 'default'}],
                    'info': {},
                    'is_flat': True,
                    'levels': [{
                        'attributes': [{'info': {}, 'locales': [], 'name': 'year', 'ref': 'year'}],
                        'info': {},
                        'key': 'year',
                        'label_attribute': 'year',
                        'name': 'year',
                        'order_attribute': 'year',
                        'role': 'year'
                    }],
                    'name': 'year',
                    'role': 'time'
                }
            ],
            'features': {
                'actions': ['aggregate', 'members', 'facts', 'cell'],
                'aggregate_functions': ['avg', 'count', 'max', 'min', 'sum'],
                'post_aggregate_functions': ['sma', 'smrsd', 'sms', 'smstd', 'smvar', 'wma']
            },
            'info': {'max_date': '2010-12-31', 'min_date': '2010-01-01'},
            'label': 'Irbd balance',
            'measures': [{'aggregates': ['sum'], 'info': {}, 'label': 'Amount', 'name': 'amount', 'ref': 'amount'}],
            'name': 'irbd_balance'
        })


class CubeAggregationAPI(BaseCubesAPITest):
    url_name = 'cube_aggregation'
    url_args = {'cube_name': 'irbd_balance'}
    method = 'get'
    fixtures = ['irbdbalance.json']

    def test_aggregation_summary(self):
        self.login()
        response = self.make_request()
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content, {
            'summary': {'record_count': 62, 'amount_sum': 1116860},
            'cells': [],
            'cell': [],
            'remainder': {},
            'aggregates': ['amount_sum', u'record_count']
        })

    def test_drilldown_with_cut(self):
        self.login()
        base_url = reverse(self.url_name, kwargs=self.url_args)
        url = "%s?drilldown=item&cut=item:a" % base_url
        response = self.make_request(url)
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content, {
            'remainder': {},
            'summary': {'record_count': 32, 'amount_sum': 558430},
            'cells': [
                {
                    'item.category': 'a',
                    'item.subcategory_label': 'Derivative Assets',
                    'item.category_label': 'Assets',
                    'amount_sum': 244691,
                    'record_count': 8,
                    'item.subcategory': 'da'
                }, {
                    'item.category': 'a',
                    'item.subcategory_label': 'Due from Banks',
                    'item.category_label': 'Assets',
                    'amount_sum': 4847,
                    'record_count': 4,
                    'item.subcategory': 'dfb'
                }, {
                    'item.category': 'a',
                    'item.subcategory_label':
                    'Investments', 'item.category_label':
                    'Assets', 'amount_sum': 77024,
                    'record_count': 2,
                    'item.subcategory': 'i'
                }, {
                    'item.category': 'a',
                    'item.subcategory_label': 'Loans Outstanding',
                    'item.category_label': 'Assets',
                    'amount_sum': 221761,
                    'record_count': 2,
                    'item.subcategory': 'lo'
                }, {
                    'item.category': 'a',
                    'item.subcategory_label': 'Nonnegotiable',
                    'item.category_label': 'Assets',
                    'amount_sum': 2325,
                    'record_count': 2,
                    'item.subcategory': 'nn'
                }, {
                    'item.category': 'a',
                    'item.subcategory_label': 'Other Assets',
                    'item.category_label': 'Assets',
                    'amount_sum': 5318,
                    'record_count': 6,
                    'item.subcategory': 'oa'
                }, {
                    'item.category': 'a',
                    'item.subcategory_label': 'Other Receivables',
                    'item.category_label': 'Assets',
                    'amount_sum': 1795,
                    'record_count': 4,
                    'item.subcategory': 'orcv'
                }, {
                    'item.category': 'a',
                    'item.subcategory_label': 'Receivables',
                    'item.category_label': 'Assets',
                    'amount_sum': 347,
                    'record_count': 2,
                    'item.subcategory': 'rcv'
                }, {
                    'item.category': 'a',
                    'item.subcategory_label': 'Securities',
                    'item.category_label': 'Assets',
                    'amount_sum': 322,
                    'record_count': 2,
                    'item.subcategory': 's'
                }
            ],
            'total_cell_count': 9,
            'aggregates': ['amount_sum', 'record_count'],
            'cell': [{
                'hidden': False,
                'dimension':
                'item',
                'type':
                'point',
                'level_depth': 1,
                'invert': False,
                'hierarchy':
                'default',
                'path': ['a']
            }],
            'levels': {'item': ['category', 'subcategory']}
        })

    def test_drilldown_with_multiple_aggregates(self):
        self.login()
        base_url = reverse(self.url_name, kwargs=self.url_args)
        url = "%s?drilldown=item&cut=item:a&aggregates=amount_sum|record_count" % base_url
        response = self.make_request(url)
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content, {
            'remainder': {},
            'summary': {'record_count': 32, 'amount_sum': 558430},
            'cells': [
                {
                    'item.category': 'a',
                    'item.subcategory_label': 'Derivative Assets',
                    'item.category_label': 'Assets',
                    'amount_sum': 244691,
                    'record_count': 8,
                    'item.subcategory': 'da'
                }, {
                    'item.category': 'a',
                    'item.subcategory_label': 'Due from Banks',
                    'item.category_label': 'Assets',
                    'amount_sum': 4847,
                    'record_count': 4,
                    'item.subcategory': 'dfb'
                }, {
                    'item.category': 'a',
                    'item.subcategory_label':
                    'Investments', 'item.category_label':
                    'Assets', 'amount_sum': 77024,
                    'record_count': 2,
                    'item.subcategory': 'i'
                }, {
                    'item.category': 'a',
                    'item.subcategory_label': 'Loans Outstanding',
                    'item.category_label': 'Assets',
                    'amount_sum': 221761,
                    'record_count': 2,
                    'item.subcategory': 'lo'
                }, {
                    'item.category': 'a',
                    'item.subcategory_label': 'Nonnegotiable',
                    'item.category_label': 'Assets',
                    'amount_sum': 2325,
                    'record_count': 2,
                    'item.subcategory': 'nn'
                }, {
                    'item.category': 'a',
                    'item.subcategory_label': 'Other Assets',
                    'item.category_label': 'Assets',
                    'amount_sum': 5318,
                    'record_count': 6,
                    'item.subcategory': 'oa'
                }, {
                    'item.category': 'a',
                    'item.subcategory_label': 'Other Receivables',
                    'item.category_label': 'Assets',
                    'amount_sum': 1795,
                    'record_count': 4,
                    'item.subcategory': 'orcv'
                }, {
                    'item.category': 'a',
                    'item.subcategory_label': 'Receivables',
                    'item.category_label': 'Assets',
                    'amount_sum': 347,
                    'record_count': 2,
                    'item.subcategory': 'rcv'
                }, {
                    'item.category': 'a',
                    'item.subcategory_label': 'Securities',
                    'item.category_label': 'Assets',
                    'amount_sum': 322,
                    'record_count': 2,
                    'item.subcategory': 's'
                }
            ],
            'total_cell_count': 9,
            'aggregates': ['amount_sum', 'record_count'],
            'cell': [{
                'hidden': False,
                'dimension':
                'item',
                'type':
                'point',
                'level_depth': 1,
                'invert': False,
                'hierarchy':
                'default',
                'path': ['a']
            }],
            'levels': {'item': ['category', 'subcategory']}
        })

    def test_drilldown_with_single_aggregate(self):
        self.login()
        base_url = reverse(self.url_name, kwargs=self.url_args)
        url = "%s?drilldown=item&aggregates=amount_sum" % base_url
        response = self.make_request(url)
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content, {
            'aggregates': ['amount_sum'],
            'cell': [],
            'cells': [
                {
                    'amount_sum': 558430,
                    'item.category': 'a',
                    'item.category_label': 'Assets'
                }, {
                    'amount_sum': 77592,
                    'item.category': 'e',
                    'item.category_label': 'Equity'
                }, {
                    'amount_sum': 480838,
                    'item.category': 'l',
                    'item.category_label': 'Liabilities'
                }
            ],
            'levels': {'item': ['category']},
            'remainder': {},
            'summary': {'amount_sum': 1116860},
            'total_cell_count': 3
        })


class CubeCellAPI(BaseCubesAPITest):
    url_name = 'cube_cell'
    url_args = {'cube_name': 'irbd_balance'}
    method = 'get'
    fixtures = ['irbdbalance.json']

    def test_cell(self):
        self.login()
        response = self.make_request()
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content, {
            'cube': 'irbd_balance', 'cuts': []
        })

    def test_cell_with_cut(self):
        self.login()
        base_url = reverse(self.url_name, kwargs=self.url_args)
        url = "%s?cut=item:a" % base_url
        response = self.make_request(url)
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content, {
            'cube': 'irbd_balance',
            'cuts': [{
                'details': [
                    {'_key': 'a', '_label': 'a', 'item.category': 'a', 'item.category_label': 'a'}
                ],
                'dimension': 'item',
                'hidden': False,
                'hierarchy': 'default',
                'invert': False,
                'level_depth': 1,
                'path': ['a'],
                'type': 'point'
            }]
        })


class CubeFactsAPI(BaseCubesAPITest):
    url_name = 'cube_facts'
    url_args = {'cube_name': 'irbd_balance'}
    method = 'get'
    fixtures = ['irbdbalance.json']

    def test_facts(self):
        self.login()
        response = self.make_request()
        self.assertEquals(response.status_code, 200)
        facts = json.loads(response.content)
        self.assertEquals(len(facts), 62)

    def test_facts_with_cut(self):
        self.login()
        base_url = reverse(self.url_name, kwargs=self.url_args)
        url = "%s?page=1&cut=item:e" % base_url
        response = self.make_request(url)
        self.assertEquals(response.status_code, 200)
        facts = json.loads(response.content)
        self.assertEquals(len(facts), 8)
        self.assertEquals(facts, [
            {
                'amount': 11492,
                'id': 55,
                'item.category': 'e',
                'item.category_label': 'Equity',
                'item.line_item': 'Paid-in capital',
                'item.subcategory': 'cs',
                'item.subcategory_label': 'Capital Stock',
                'year': 2010
            },
            {
                'amount': 11491,
                'id': 56,
                'item.category': 'e',
                'item.category_label': 'Equity',
                'item.line_item': 'Paid-in capital',
                'item.subcategory': 'cs',
                'item.subcategory_label': 'Capital Stock',
                'year': 2009
            },
            {
                'amount': 313,
                'id': 57,
                'item.category': 'e',
                'item.category_label': 'Equity',
                'item.line_item': 'Deferred Amounts to Maintain Value of Currency Holdings',
                'item.subcategory': 'da',
                'item.subcategory_label': 'Deferred Amounts',
                'year': 2010
            },
            {
                'amount': 359,
                'id': 58,
                'item.category': 'e',
                'item.category_label': 'Equity',
                'item.line_item': 'Deferred Amounts to Maintain Value of Currency Holdings',
                'item.subcategory': 'da',
                'item.subcategory_label': 'Deferred Amounts',
                'year': 2009
            },
            {
                'amount': 28793,
                'id': 59,
                'item.category': 'e',
                'item.category_label': 'Equity',
                'item.line_item': 'Retained Earnings',
                'item.subcategory': 're',
                'item.subcategory_label': 'Retained Earnings',
                'year': 2010
            },
            {
                'amount': 29870,
                'id': 60,
                'item.category': 'e',
                'item.category_label': 'Equity',
                'item.line_item': 'Retained Earnings',
                'item.subcategory': 're',
                'item.subcategory_label': 'Retained Earnings',
                'year': 2009
            },
            {
                'amount': -3043,
                'id': 61,
                'item.category': 'e',
                'item.category_label': 'Equity',
                'item.line_item': 'Accumulated Other Comorehensive Loss',
                'item.subcategory': 'oe',
                'item.subcategory_label': 'Other',
                'year': 2010
            },
            {
                'amount': -1683,
                'id': 62,
                'item.category': 'e',
                'item.category_label': 'Equity',
                'item.line_item': 'Accumulated Other Comorehensive Loss',
                'item.subcategory': 'oe',
                'item.subcategory_label': 'Other',
                'year': 2009
            }
        ])


class CubeFactAPI(BaseCubesAPITest):
    url_name = 'cube_fact'
    url_args = {'cube_name': 'irbd_balance', 'fact_id': 1}
    method = 'get'
    fixtures = ['irbdbalance.json']

    def test_fact_is_disabled_on_the_browser(self):
        self.login()
        response = self.make_request()
        self.assertEquals(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEquals(
            content,
            {'detail': "The action 'fact' is not enabled"}
        )


class CubeMembersAPI(BaseCubesAPITest):
    url_name = 'cube_members'
    url_args = {'cube_name': 'irbd_balance', 'dimension_name': 'item'}
    method = 'get'
    fixtures = ['irbdbalance.json']

    def test_members_with_cut(self):
        self.login()
        base_url = reverse(self.url_name, kwargs=self.url_args)
        url = "%s?level=category&cut=item:e" % base_url
        response = self.make_request(url)
        self.assertEquals(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEquals(content, {
        })
