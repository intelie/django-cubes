# -*- coding: utf-8 -*-
from django.db.models import get_model
from django.db.models import Count, Max, Min, Sum, Avg

from cubes.logging import get_logger
from cubes.browser import AggregationBrowser, AggregationResult, Cell, Facts
from cubes.statutils import calculators_for_aggregates, available_calculators

from .mapper import DjangoMapper


__all__ = ['DjangoBrowser', ]


_aggregate_functions = {
    'count': {
        'aggregate_fn': Count,
    },
    'sum': {
        'aggregate_fn': Sum,
    },
    'max': {
        'aggregate_fn': Max,
    },
    'min': {
        'aggregate_fn': Min,
    },
    'avg': {
        'aggregate_fn': Avg,
    },
}


def get_aggregate_function(name):
    """Returns an aggregate function `name`. The returned function takes two
    arguments: `aggregate` and `context`. When called returns a labelled
    SQL expression."""

    name = name or "identity"
    return _aggregate_functions[name]


def available_aggregate_functions():
    """Returns a list of available aggregate function names."""
    return _aggregate_functions.keys()


class DjangoBrowser(AggregationBrowser):
    __extension_name__ = "django"
    __options__ = [
        {
            "name": "include_summary",
            "type": "bool"
        },
        {
            "name": "include_cell_count",
            "type": "bool"
        },
        {
            "name": "safe_labels",
            "type": "bool"
        }
    ]

    def __init__(self, cube, store, locale=None, calendar=None, **options):
        super(DjangoBrowser, self).__init__(cube, store)

        self.logger = get_logger()
        self.cube = cube

        # Locale support is not implemented
        self.locale = locale or cube.locale

        self.class_name = store.class_name
        if self.cube.browser_options.get('class_name'):
            self.class_name = self.cube.browser_options.get('class_name')

        # São usados no `provide_aggregate`
        self.include_summary = options.get("include_summary", True)
        self.include_cell_count = options.get("include_cell_count", True)
        self.safe_labels = options.get("safe_labels", False)
        self.label_counter = 1

        # Whether to ignore cells where at least one aggregate is NULL
        self.exclude_null_agregates = options.get("exclude_null_agregates", True)

        self.mapper = DjangoMapper(self.cube, self.class_name, self.locale)
        self.model = get_model(*self.class_name.split('.'))

    def features(self):
        """
        Return SQL features. Currently they are all the same for every
        cube, however in the future they might depend on the SQL engine or
        other factors.
        """

        return {
            "actions": ["aggregate", "facts", "cell"],
            "aggregate_functions": sorted(available_aggregate_functions()),
            "post_aggregate_functions": sorted(available_calculators())
        }

    def is_builtin_function(self, function_name, aggregate):
        """
        Returns `True` if function `function_name` for `aggregate` is
        bult-in. Returns `False` if the browser can not compute the function
        and post-aggregation calculation should be used.
        """
        return function_name in available_aggregate_functions()

    def _build_cell_cut_qset(self, cell):
        filter_kwargs = {}
        for cut in cell.cuts:
            path = cut.path
            depth = cut.level_depth()
            dim = self.cube.dimension(cut.dimension)
            hier = dim.hierarchy(cut.hierarchy)
            keys = [level.key for level in hier[0:depth]]
            for key in keys:
                filter_kwargs[u'%s__in' % key.name] = path

        return self.model.objects.filter(**filter_kwargs)

    def build_query(self, cell, attributes, page=None, page_size=None, order=None, include_fact_key=False):
        qset = self._build_cell_cut_qset(cell)
        if order:
            order_fields = [item[0].name for item in order]
            qset = qset.order_by(*order_fields)
        if page and page_size:
            start = (page - 1) * page_size
            end = start + page_size
            qset = qset[start:end]
        return qset.values()

    def build_aggregation(self, cell, aggregates, drilldown, summary_only=False):
        args, kwargs = [], {}
        qset = self._build_cell_cut_qset(cell)

        for item in aggregates:
            measure = item.measure if item.measure else 'pk'
            function = _aggregate_functions[item.function]['aggregate_fn']
            kwargs[item.name] = function(measure)

        if summary_only:
            result = qset.aggregate(*args, **kwargs)
        else:
            args = [item.name for item in drilldown.all_attributes()]
            result = qset.values(*args).annotate(**kwargs).order_by(*args)

        return result

    def provide_aggregate(self, cell, aggregates, drilldown, split, order, page, page_size, **options):
        """
        Return aggregated result.

        Arguments:

        * `cell`: cell to be aggregated . Guaranteed to be a `Cell` object even
            for an empty cell
        * `measures`: aggregates of these measures will be considered. Contains
            list of cube aggregate attribute objects.
        * `aggregates`: aggregates to be considered
        * `drilldown`: list of dimensions or list of tuples: (`dimension`,
            `hierarchy`, `level`). `Drilldown` instance
        * `split`: an optional cell that becomes an extra drilldown segmenting
            the data into those within split cell and those not within.
            `Cell` instance
        * `order` – list of tuples: (`attribute`, `order`)
        * `attributes`: list of attributes from drilled-down dimensions to be
            returned in the result

        Query tuning:

        * `include_cell_count`: if ``True`` (``True`` is default) then
            `result.total_cell_count` is computed as well, otherwise it will
            be ``None``.
        * `include_summary`: if ``True`` (default) then summary is computed,
            otherwise it will be ``None``

        Result is paginated by `page_size` and ordered by `order`.

        Number of database queries:

        * without drill-down: 1 – summary
        * with drill-down (default): 3 – summary, drilldown, total drill-down
            record count

        Notes:

        * measures can be only in the fact table
        """
        result = AggregationResult(cell=cell, aggregates=aggregates)

        ## Summary
        ## -------
        result.summary = self.build_aggregation(cell, aggregates, drilldown, summary_only=True)

        # Drill-down
        # ----------
        # Note that a split cell if present prepends the drilldown
        if drilldown or split:
            if not (page_size and page is not None):
                self.assert_low_cardinality(cell, drilldown)

            result.levels = drilldown.result_levels(include_split=bool(split))
            self.logger.debug("preparing drilldown statement")

            #
            # Find post-aggregation calculations and decorate the result
            #
            result.calculators = calculators_for_aggregates(
                self.cube, aggregates, drilldown, split, available_aggregate_functions()
            )

            query = self.build_aggregation(cell, aggregates, drilldown)
            result.cells = self.result_iterator(query)
            if result.cells:
                result.labels = result.cells[0].keys()

            if self.include_cell_count:
                result.total_cell_count = query.count()

        elif result.summary is not None:
            # Do calculated measures on summary if no drilldown or split
            # TODO: should not we do this anyway regardless of
            # drilldown/split?
            calculators = calculators_for_aggregates(
                self.cube, aggregates, drilldown, split, available_aggregate_functions()
            )
            for calc in calculators:
                calc(result.summary)

        # If exclude_null_aggregates is True then don't include cells where
        # at least one of the bult-in aggregates is NULL
        if result.cells is not None and self.exclude_null_agregates:
            afuncs = available_aggregate_functions()
            aggregates = [agg for agg in aggregates if not agg.function or agg.function in afuncs]
            names = [str(agg) for agg in aggregates]
            result.exclude_if_null = names

        return result

    def facts(self, cell=None, fields=None, order=None, page=None, page_size=None):
        """
        Return an iterable object with of all facts within cell.
        `fields` is list of fields to be considered in the output.

        Subclasses overriding this method sould return a :class:`Facts` object
        and set it's `attributes` to the list of selected attributes.
        """

        ## Da documentação:
        cell = cell or Cell(self.cube)
        attributes = self.cube.get_attributes(fields)
        order = self.prepare_order(order, is_aggregate=False)

        facts = self.result_iterator(
            self.build_query(
                cell, attributes, page=page, page_size=page_size, order=order
            )
        )
        return Facts(facts, attributes)

    def result_iterator(self, cells):
        result = []
        for cell in cells:
            new_cell = dict(
                (self.mapper.reverse_mappings.get(k, k), v)
                for k, v in cell.items()
            )
            result.append(new_cell)
        return result
