# -*- coding: utf-8 -*-
from django.db.models import get_model

from cubes.logging import get_logger
from cubes.browser import AggregationBrowser, AggregationResult, Cell, Facts, PointCut
from cubes.statutils import calculators_for_aggregates, available_calculators

from .mapper import DjangoMapper


__all__ = ['DjangoBrowser', ]


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

        # XXX: Obter referência à classe do model onde?
        # self.class_name = get_model(self.class_name.split('.'))

        # São usados no `provide_aggregate`
        self.include_summary = options.get("include_summary", True)
        self.include_cell_count = options.get("include_cell_count", True)
        self.safe_labels = options.get("safe_labels", False)
        self.label_counter = 1

        # Whether to ignore cells where at least one aggregate is NULL
        self.exclude_null_agregates = options.get("exclude_null_agregates", True)

        self.mapper = DjangoMapper(self.cube, self.class_name, self.locale)

    def features(self):
        """
        Return SQL features. Currently they are all the same for every
        cube, however in the future they might depend on the SQL engine or
        other factors.
        """

        return {
            "actions": ["aggregate", "fact", "members", "facts", "cell"],
            #"aggregate_functions": available_aggregate_functions(),
            "post_aggregate_functions": available_calculators()
        }

    def is_builtin_function(self, function_name, aggregate):
        """Returns `True` if function `function_name` for `aggregate` is
        bult-in. Returns `False` if the browser can not compute the function
        and post-aggregation calculation should be used.

        Subclasses should override this method."""
        return False

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

        ## Da documentação:
        #
        # ... do the aggregation here ...
        #

        result = AggregationResult(cell=cell, aggregates=aggregates)
        import ipdb; ipdb.set_trace()

        ## Set the result cells iterator (required)
        #result.cells = ...
        #result.labels = ...

        ## Optional:
        #result.total_cell_count = ...
        #result.summary = ...

        return result

        ## Do backend sql
        #result = AggregationResult(cell=cell, aggregates=aggregates)

        ## Summary
        ## -------

        #if self.include_summary or not (drilldown or split):
        #    # TODO: Refazer isso para o orm do django
        #    raise NotImplementedError
        #    builder = QueryBuilder(self)
        #    builder.aggregation_statement(
        #        cell, aggregates=aggregates, drilldown=drilldown, summary_only=True
        #    )

        #    cursor = self.execute_statement(
        #        builder.statement, "aggregation summary"
        #    )
        #    row = cursor.fetchone()
        #    if row:
        #        # Convert SQLAlchemy object into a dictionary
        #        record = dict(zip(builder.labels, row))
        #    else:
        #        record = None
        #    cursor.close()
        #    result.summary = record

        ## Drill-down
        ## ----------
        ##
        ## Note that a split cell if present prepends the drilldown
        #if drilldown or split:
        #    if not (page_size and page is not None):
        #        self.assert_low_cardinality(cell, drilldown)

        #    result.levels = drilldown.result_levels(include_split=bool(split))
        #    self.logger.debug("preparing drilldown statement")

        #    # TODO: Refazer isso para o orm do django
        #    raise NotImplementedError
        #    builder = QueryBuilder(self)
        #    builder.aggregation_statement(
        #        cell, drilldown=drilldown, aggregates=aggregates, split=split
        #    )
        #    builder.paginate(page, page_size)
        #    builder.order(order)

        #    cursor = self.execute_statement(
        #        builder.statement, "aggregation drilldown"
        #    )

        #    #
        #    # Find post-aggregation calculations and decorate the result
        #    #
        #    result.calculators = calculators_for_aggregates(
        #        self.cube, aggregates, drilldown, split, available_aggregate_functions()
        #    )
        #    result.cells = ResultIterator(cursor, builder.labels)
        #    result.labels = builder.labels

        #    # TODO: Introduce option to disable this
        #    if self.include_cell_count:
        #        count_statement = builder.statement.alias().count()
        #        row_count = self.execute_statement(count_statement).fetchone()
        #        total_cell_count = row_count[0]
        #        result.total_cell_count = total_cell_count

        #elif result.summary is not None:
        #    # Do calculated measures on summary if no drilldown or split
        #    # TODO: should not we do this anyway regardless of
        #    # drilldown/split?
        #    calculators = calculators_for_aggregates(
        #        self.cube, aggregates, drilldown, split, available_aggregate_functions()
        #    )
        #    for calc in calculators:
        #        calc(result.summary)

        ## If exclude_null_aggregates is True then don't include cells where
        ## at least one of the bult-in aggregates is NULL
        #if result.cells is not None and self.exclude_null_agregates:
        #    afuncs = available_aggregate_functions()
        #    aggregates = [agg for agg in aggregates if not agg.function or agg.function in afuncs]
        #    names = [str(agg) for agg in aggregates]
        #    result.exclude_if_null = names

        #return result

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

        import ipdb; ipdb.set_trace()
        #
        # ... fetch the facts here ...
        #
        # facts = ... an iterable ...
        #

        facts = []
        result = Facts(facts, attributes)
        return result

        ## Do backend sql
        #cell = cell or Cell(self.cube)
        #attributes = self.cube.get_attributes(fields)

        ### TODO: Refazer isso para o orm do django
        #raise NotImplementedError
        #builder = QueryBuilder(self)
        #builder.denormalized_statement(
        #    cell, attributes=attributes, include_fact_key=True
        #)
        #builder.paginate(page, page_size)
        #order = self.prepare_order(order, is_aggregate=False)
        #builder.order(order)

        #cursor = self.execute_statement(builder.statement, "facts")
        #return ResultIterator(cursor, builder.labels)

    def fact(self, key_value, fields=None):
        """
        Get a single fact with key `key_value` from cube.
        """
        attributes = self.cube.get_attributes(fields)
        import ipdb; ipdb.set_trace()

        ## Do backend sql
        ## TODO: Refazer isso para o orm do django
        #raise NotImplementedError
        #builder = QueryBuilder(self)
        #builder.denormalized_statement(attributes=attributes, include_fact_key=True)
        #builder.fact(key_value)

        #cursor = self.execute_statement(builder.statement, "facts")
        #row = cursor.fetchone()
        #if row:
        #    # Convert SQLAlchemy object into a dictionary
        #    record = dict(zip(builder.labels, row))
        #else:
        #    record = None
        #cursor.close()

        #return record

    def provide_members(self, cell, dimension, **kwargs):
        """
        Return values for `dimension` with level depth `depth`. If `depth`
        is ``None``, all levels are returned.

        Number of database queries: 1.
        """
        depth = kwargs.get('depth', None)
        hierarchy = kwargs.get('hierarchy', None)
        levels = kwargs.get('levels', None)
        attributes = kwargs.get('attributes', None)
        page = kwargs.get('page', None)
        page_size = kwargs.get('page_size', None)
        order = kwargs.get('order', None)

        if not attributes:
            attributes = []
            for level in levels:
                attributes += level.attributes

        # Do backend sql
        ## TODO: Refazer isso para o orm do django
        #raise NotImplementedError
        #builder = QueryBuilder(self)
        #builder.members_statement(cell, attributes)
        #builder.paginate(page, page_size)
        #builder.order(order)

        #result = self.execute_statement(builder.statement, "members")

        #return ResultIterator(result, builder.labels)

    def path_details(self, dimension, path, hierarchy=None):
        """
        Returns details for `path` in `dimension`. Can be used for
        multi-dimensional "breadcrumbs" in a used interface.

        Number of SQL queries: 1.
        """
        dimension = self.cube.dimension(dimension)
        hierarchy = dimension.hierarchy(hierarchy)

        cut = PointCut(dimension, path, hierarchy=hierarchy)
        cell = Cell(self.cube, [cut])

        attributes = []
        for level in hierarchy.levels[0:len(path)]:
            attributes += level.attributes

        # TODO: Refazer isso para o orm do django
        raise NotImplementedError
        builder = QueryBuilder(self)
        builder.denormalized_statement(
            cell, attributes=attributes, include_fact_key=True
        )
        builder.paginate(0, 1)
        cursor = self.execute_statement(
            builder.statement, "path details"
        )

        row = cursor.fetchone()
        if row:
            member = dict(zip(builder.labels, row))
        else:
            member = None

        return member
