# -*- coding: utf-8 -*-
import six
from os import path
from cubes import Workspace, Cell, PointCut, SetCut

from unittest import skip
from django.test import TransactionTestCase
from django.conf import settings

# DjangoBrowser and DjangoStore must be loaded in order to be found by cubes
from django_cubes.backends.django_orm.browser import DjangoBrowser  # NOQA
from django_cubes.backends.django_orm.store import DjangoStore  # NOQA

__all__ = ['ValidateDjangoOrmBrowser']


class ValidateDjangoOrmBrowser(TransactionTestCase):
    fixtures = ['irbdbalance.json']
    maxDiff = None

    def setUp(self):
        super(ValidateDjangoOrmBrowser, self).setUp()
        self.workspace = Workspace(
            cubes_root=settings.SLICER_MODELS_DIR,
            config=path.join(settings.SLICER_MODELS_DIR, 'slicer-django_backend.ini'),
        )
        self.browser = self.workspace.browser("irbd_balance")

    def test_simple_aggregation(self):
        result = self.browser.aggregate()
        self.assertEquals(result.summary, {
            'record_count': 62,
            'amount_sum': 1116860,
        })

    def test_simple_drilldown(self):
        result = self.browser.aggregate(drilldown=["item"])
        values = [
            (row.label, row.record["record_count"], row.record["amount_sum"])
            for row in result.table_rows("item")
        ]
        six.assertCountEqual(self, values, [
            (u'Assets', 32, 558430), (u'Equity', 8, 77592), (u'Liabilities', 22, 480838)
        ])

    def test_simple_slice(self):
        cut = PointCut("item", ["e"])
        cell = Cell(self.browser.cube, cuts=[cut])
        result = self.browser.aggregate(cell, drilldown=["item"])
        values = [
            (row.label, row.record["record_count"], row.record["amount_sum"])
            for row in result.table_rows("item")
        ]
        six.assertCountEqual(self, values, [
            (u'Retained Earnings', 2, 58663),
            (u'Deferred Amounts', 2, 672),
            (u'Capital Stock', 2, 22983),
            (u'Other', 2, -4726)
        ])

    def test_facts_list(self):
        facts = self.browser.facts(page=1, page_size=10, order=['item.line_item', 'amount'])
        six.assertCountEqual(self, facts, [
            {
                'amount': 2707,
                'item.category': u'l',
                'item.subcategory': u'ol',
                'item.subcategory_label': u'Other Liabilities',
                'item.category_label': u'Liabilities',
                'id': 54,
                'year': 2009,
                'item.line_item': u'Accounts payable and misc liabilities'
            }, {
                'amount': 2793,
                'item.category': u'l',
                'item.subcategory': u'ol',
                'item.subcategory_label': u'Other Liabilities',
                'item.category_label': u'Liabilities',
                'id': 53,
                'year': 2010,
                'item.line_item': u'Accounts payable and misc liabilities'
            }, {
                'amount': 1190,
                'item.category': u'l',
                'item.subcategory': u'ol',
                'item.subcategory_label': u'Other Liabilities',
                'item.category_label': u'Liabilities',
                'id': 49,
                'year': 2010,
                'item.line_item': u'Accrued charges on borrowings'
            }, {
                'amount': 1495,
                'item.category': u'l',
                'item.subcategory': u'ol',
                'item.subcategory_label': u'Other Liabilities',
                'item.category_label': u'Liabilities',
                'id': 50,
                'year': 2009,
                'item.line_item': u'Accrued charges on borrowings'
            }, {
                'amount': 764,
                'item.category': u'a',
                'item.subcategory': u'orcv',
                'item.subcategory_label': u'Other Receivables',
                'item.category_label': u'Assets',
                'id': 23,
                'year': 2010,
                'item.line_item': u'Accrued income on loans'
            }, {
                'amount': 889,
                'item.category': u'a',
                'item.subcategory': u'orcv',
                'item.subcategory_label': u'Other Receivables',
                'item.category_label': u'Assets',
                'id': 24,
                'year': 2009,
                'item.line_item': u'Accrued income on loans'
            }, {
                'amount': -3043,
                'item.category': u'e',
                'item.subcategory': u'oe',
                'item.subcategory_label': u'Other',
                'item.category_label': u'Equity',
                'id': 61,
                'year': 2010,
                'item.line_item': u'Accumulated Other Comorehensive Loss'
            }, {
                'amount': -1683,
                'item.category': u'e',
                'item.subcategory': u'oe',
                'item.subcategory_label': u'Other',
                'item.category_label': u'Equity',
                'id': 62,
                'year': 2009,
                'item.line_item': u'Accumulated Other Comorehensive Loss'
            }, {
                'amount': 110040,
                'item.category': u'l',
                'item.subcategory': u'b',
                'item.subcategory_label': u'Borrowings',
                'item.category_label': u'Liabilities',
                'id': 34,
                'year': 2009,
                'item.line_item': u'All'
            }, {
                'amount': 128577,
                'item.category': u'l',
                'item.subcategory': u'b',
                'item.subcategory_label': u'Borrowings',
                'item.category_label': u'Liabilities',
                'id': 33,
                'year': 2010,
                'item.line_item': u'All'
            },
        ])

    def test_multiple_drilldowns(self):
        # "?drilldown=year&drilldown=item&aggregates=amount_sum"
        result = self.browser.aggregate(drilldown=["year", "item"], aggregates=["amount_sum"])
        values = [
            (row.label, row.record)
            for row in result.table_rows("item")
        ]
        six.assertCountEqual(self, values, [
            ('Assets', {'amount_sum': 275420, 'item.category': 'a', 'item.category_label': 'Assets', 'year': 2009}),
            ('Equity', {'amount_sum': 40037, 'item.category': 'e', 'item.category_label': 'Equity', 'year': 2009}),
            ('Liabilities', {'amount_sum': 235383, 'item.category': 'l', 'item.category_label': 'Liabilities', 'year': 2009}),
            ('Assets', {'amount_sum': 283010, 'item.category': 'a', 'item.category_label': 'Assets', 'year': 2010}),
            ('Equity', {'amount_sum': 37555, 'item.category': 'e', 'item.category_label': 'Equity', 'year': 2010}),
            ('Liabilities', {'amount_sum': 245455, 'item.category': 'l', 'item.category_label': 'Liabilities', 'year': 2010})
        ])

    @skip('SetCuts are not yet supported by this backend')
    def test_multiple_drilldowns_with_set_cuts(self):
        # "?drilldown=year&drilldown=item&aggregates=amount_sum&cut=item.category:a;e;l|year:2009;2010"
        cuts = [
            SetCut("item", [['a'], ['e'], ['l']]),
            SetCut("year", [[2009], [2010]]),
        ]
        cell = Cell(self.browser.cube, cuts=cuts)
        result = self.browser.aggregate(cell, drilldown=["year", "item"], aggregates=["amount_sum"])
        values = [
            (row.label, row.record)
            for row in result.table_rows("item")
        ]
        six.assertCountEqual(self, values, [
            ('Assets', {'amount_sum': 275420, 'item.category': 'a', 'item.category_label': 'Assets', 'year': 2009}),
            ('Equity', {'amount_sum': 40037, 'item.category': 'e', 'item.category_label': 'Equity', 'year': 2009}),
            ('Liabilities', {'amount_sum': 235383, 'item.category': 'l', 'item.category_label': 'Liabilities', 'year': 2009}),
            ('Assets', {'amount_sum': 283010, 'item.category': 'a', 'item.category_label': 'Assets', 'year': 2010}),
            ('Equity', {'amount_sum': 37555, 'item.category': 'e', 'item.category_label': 'Equity', 'year': 2010}),
            ('Liabilities', {'amount_sum': 245455, 'item.category': 'l', 'item.category_label': 'Liabilities', 'year': 2010})
        ])
