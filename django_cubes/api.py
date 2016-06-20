# -*- coding: utf-8 -*-
import logging
import re
from collections import OrderedDict
from threading import local

from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework.renderers import TemplateHTMLRenderer

from cubes import __version__, browser, cut_from_dict
from cubes.workspace import Workspace, SLICER_INFO_KEYS
from cubes.errors import NoSuchCubeError
from cubes.calendar import CalendarMemberConverter
from cubes.browser import Cell, cuts_from_string

from django.conf import settings
from django.http import Http404
from django.core.exceptions import ImproperlyConfigured

API_VERSION = 2

__all__ = [
    'Index', 'ApiVersion', 'Info',
    'ListCubes', 'CubeModel', 'CubeAggregation',
    'CubeCell', 'CubeReport', 'CubeFacts',
    'CubeFact', 'CubeMembers',
]


data = local()


def create_local_workspace(config, cubes_root):
    """
    Returns or creates a thread-local instance of Workspace
    """
    if not hasattr(data, 'workspace'):
        data.workspace = Workspace(config=config, cubes_root=cubes_root)

    return data.workspace


class ApiVersion(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        info = {
            "version": __version__,
            "server_version": __version__,
            "api_version": API_VERSION
        }
        return Response(info)


class CubesView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    workspace = None
    SET_CUT_SEPARATOR_CHAR = '~'

    def __init__(self, *args, **kwargs):
        super(CubesView, self).__init__(*args, **kwargs)
        self._fix_cut_separators()

    def _fix_cut_separators(self):
        browser.PATH_ELEMENT = r"(?:\\.|[^:%s|-])*" % self.SET_CUT_SEPARATOR_CHAR
        browser.RE_ELEMENT = re.compile(r"^%s$" % browser.PATH_ELEMENT)
        browser.RE_POINT = re.compile(r"^%s$" % browser.PATH_ELEMENT)
        browser.SET_CUT_SEPARATOR_CHAR = self.SET_CUT_SEPARATOR_CHAR
        browser.SET_CUT_SEPARATOR = re.compile(r'(?<!\\)%s' % self.SET_CUT_SEPARATOR_CHAR)
        browser.RE_SET = re.compile(r"^(%s)(%s(%s))*$" % (
            browser.PATH_ELEMENT, self.SET_CUT_SEPARATOR_CHAR, browser.PATH_ELEMENT
        ))

    def initialize_slicer(self):
        if self.workspace is None:
            try:
                config = settings.SLICER_CONFIG_FILE
                cubes_root = settings.SLICER_MODELS_DIR
            except AttributeError:
                raise ImproperlyConfigured('settings.SLICER_CONFIG_FILE and settings.SLICER_MODELS_DIR are not set.')

            self.workspace = create_local_workspace(config=config, cubes_root=cubes_root)

    def get_cube(self, request, cube_name):
        self.initialize_slicer()
        try:
            cube = self.workspace.cube(cube_name, request.user)
        except NoSuchCubeError:
            raise Http404

        return cube

    def get_browser(self, cube):
        return self.workspace.browser(cube)

    def get_cell(self, request, cube, argname="cut", restrict=False):
        """Returns a `Cell` object from argument with name `argname`"""
        converters = {
            "time": CalendarMemberConverter(self.workspace.calendar)
        }

        cuts = []
        for cut_string in request.QUERY_PARAMS.getlist(argname):
            cuts += cuts_from_string(
                cube, cut_string, role_member_converters=converters
            )

        if cuts:
            cell = Cell(cube, cuts)
        else:
            cell = None

        if restrict:
            if self.workspace.authorizer:
                cell = self.workspace.authorizer.restricted_cell(
                    request.user, cube=cube, cell=cell
                )
        return cell

    def get_info(self):
        self.initialize_slicer()
        if self.workspace.info:
            info = OrderedDict(self.workspace.info)
        else:
            info = OrderedDict()

        info["cubes_version"] = __version__
        info["timezone"] = self.workspace.calendar.timezone_name
        info["first_weekday"] = self.workspace.calendar.first_weekday
        info["api_version"] = API_VERSION
        return info

    def assert_enabled_action(self, request, browser, action):
        features = browser.features()
        if action not in features['actions']:
            message = u"The action '{}' is not enabled".format(action)
            logging.error(message)
            raise ParseError(detail=message)

    def _handle_pagination_and_order(self, request):
        try:
            page = request.QUERY_PARAMS.get('page', None)
        except ValueError:
            page = None
        request.page = page

        try:
            page_size = request.QUERY_PARAMS.get('pagesize', None)
        except ValueError:
            page_size = None
        request.page_size = page_size

        # Collect orderings:
        # order is specified as order=<field>[:<direction>]
        order = []
        for orders in request.QUERY_PARAMS.getlist('order'):
            for item in orders.split(","):
                split = item.split(":")
                if len(split) == 1:
                    order.append((item, None))
                else:
                    order.append((split[0], split[1]))
        request.order = order

    def initialize_request(self, request, *args, **kwargs):
        request = super(CubesView, self).initialize_request(request, *args, **kwargs)
        self._handle_pagination_and_order(request)
        return request


class Index(CubesView):
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request):
        info = self.get_info()
        info['has_about'] = any(key in info for key in SLICER_INFO_KEYS)
        return Response(info, template_name="cubes/index.html")


class Info(CubesView):

    def get(self, request):
        return Response(self.get_info())


class ListCubes(CubesView):

    def get(self, request):
        self.initialize_slicer()
        cube_list = self.workspace.list_cubes(request.user)
        return Response(cube_list)


class CubeModel(CubesView):

    def get(self, request, cube_name):
        cube = self.get_cube(request, cube_name)
        if self.workspace.authorizer:
            hier_limits = self.workspace.authorizer.hierarchy_limits(
                request.user, cube_name
            )
        else:
            hier_limits = None

        model = cube.to_dict(
            expand_dimensions=True,
            with_mappings=False,
            full_attribute_names=True,
            create_label=True,
            hierarchy_limits=hier_limits
        )

        model["features"] = self.workspace.cube_features(cube)
        return Response(model)


class CubeAggregation(CubesView):

    def get(self, request, cube_name):
        cube = self.get_cube(request, cube_name)
        browser = self.get_browser(cube)
        self.assert_enabled_action(request, browser, 'aggregate')

        cell = self.get_cell(request, cube, restrict=True)

        # Aggregates
        aggregates = []
        for agg in request.QUERY_PARAMS.getlist('aggregates') or []:
            aggregates += agg.split('|')

        drilldown = []
        ddlist = request.QUERY_PARAMS.getlist('drilldown')
        if ddlist:
            for ddstring in ddlist:
                drilldown += ddstring.split('|')

        split = self.get_cell(request, cube, argname='split')
        result = browser.aggregate(
            cell,
            aggregates=aggregates,
            drilldown=drilldown,
            split=split,
            page=request.page,
            page_size=request.page_size,
            order=request.order
        )

        return Response(result.to_dict())


class CubeCell(CubesView):

    def get(self, request, cube_name):
        cube = self.get_cube(request, cube_name)
        browser = self.get_browser(cube)
        self.assert_enabled_action(request, browser, 'cell')

        cell = self.get_cell(request, cube, restrict=True)
        details = browser.cell_details(cell)

        if not cell:
            cell = Cell(cube)

        cell_dict = cell.to_dict()
        for cut, detail in zip(cell_dict["cuts"], details):
            cut["details"] = detail

        return Response(cell_dict)


class CubeReport(CubesView):

    def make_report(self, request, cube_name):
        cube = self.get_cube(request, cube_name)
        browser = self.get_browser(cube)
        self.assert_enabled_action(request, browser, 'report')

        report_request = request.DATA
        try:
            queries = report_request["queries"]
        except KeyError:
            message = "Report request does not contain 'queries' key"
            logging.error(message)
            raise ParseError(detail=message)

        cell = self.get_cell(request, cube, restrict=True)
        cell_cuts = report_request.get("cell")

        if cell_cuts:
            # Override URL cut with the one in report
            cuts = [cut_from_dict(cut) for cut in cell_cuts]
            cell = Cell(cube, cuts)
            logging.info(
                "Using cell from report specification (URL parameters are ignored)"
            )

            if self.workspace.authorizer:
                cell = self.workspace.authorizer.restricted_cell(
                    request.user, cube=cube, cell=cell
                )
        else:
            if not cell:
                cell = Cell(cube)
            else:
                cell = cell

        report = browser.report(cell, queries)
        return Response(report)

    def get(self, request, cube_name):
        return self.make_report(request, cube_name)

    def post(self, request, cube_name):
        return self.make_report(request, cube_name)


class CubeFacts(CubesView):

    def get(self, request, cube_name):
        cube = self.get_cube(request, cube_name)
        browser = self.get_browser(cube)
        self.assert_enabled_action(request, browser, 'facts')

        # Construct the field list
        fields_str = request.QUERY_PARAMS.get('fields')
        if fields_str:
            attributes = cube.get_attributes(fields_str.split(','))
        else:
            attributes = cube.all_attributes

        fields = [attr.ref() for attr in attributes]
        cell = self.get_cell(request, cube, restrict=True)

        # Get the result
        facts = browser.facts(
            cell,
            fields=fields,
            page=request.page,
            page_size=request.page_size,
            order=request.order
        )

        return Response(facts)


class CubeFact(CubesView):

    def get(self, request, cube_name, fact_id):
        cube = self.get_cube(request, cube_name)
        browser = self.get_browser(cube)
        self.assert_enabled_action(request, browser, 'fact')
        fact = browser.fact(fact_id)
        return Response(fact)


class CubeMembers(CubesView):

    def get(self, request, cube_name, dimension_name):
        cube = self.get_cube(request, cube_name)
        browser = self.get_browser(cube)
        self.assert_enabled_action(request, browser, 'members')

        try:
            dimension = cube.dimension(dimension_name)
        except KeyError:
            message = "Dimension '%s' was not found" % dimension_name
            logging.error(message)
            raise ParseError(detail=message)

        hier_name = request.QUERY_PARAMS.get('hierarchy')
        hierarchy = dimension.hierarchy(hier_name)

        depth = request.QUERY_PARAMS.get('depth', None)
        level = request.QUERY_PARAMS.get('level', None)

        if depth and level:
            message = "Both depth and level provided, use only one (preferably level)"
            logging.error(message)
            raise ParseError(detail=message)
        elif depth:
            try:
                depth = int(depth)
            except ValueError:
                message = "depth should be an integer"
                logging.error(message)
                raise ParseError(detail=message)
        elif level:
            depth = hierarchy.level_index(level) + 1
        else:
            depth = len(hierarchy)

        cell = self.get_cell(request, cube, restrict=True)
        values = browser.members(
            cell,
            dimension,
            depth=depth,
            hierarchy=hierarchy,
            page=request.page,
            page_size=request.page_size
        )

        result = {
            "dimension": dimension.name,
            "hierarchy": hierarchy.name,
            "depth": len(hierarchy) if depth is None else depth,
            "data": values
        }

        return Response(result)
