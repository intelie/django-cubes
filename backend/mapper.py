# -*- coding: utf-8 -*-
from django.db.models import get_model

from cubes.mapper import Mapper

__all__ = ['DjangoMapper', ]


class DjangoMapper(Mapper):

    def __init__(self, cube, class_name, mappings=None, **options):
        """
        A django collection mapper for a cube. The mapper creates required
        fields, project and match expressions, and encodes/decodes using
        provided python lambdas.

        Attributes:

        * `cube` - mapped cube
        * `mappings` – dictionary containing mappings

        `mappings` is a dictionary where keys are logical attribute references
        and values are django model attribute references. The keys are mostly in the
        form:

        * ``attribute`` for measures and fact details
        * ``dimension.attribute`` for dimension attributes

        The values might be specified as strings in the form ``field``
        (covering most of the cases) or as a dictionary with keys ``database``,
        ``collection`` and ``field`` for more customized references.
        """
        super(DjangoMapper, self).__init__(cube, **options)

        self.class_name = class_name
        self.mappings = mappings or cube.mappings

    def physical(self, attribute, locale=None):
        """Returns physical reference for attribute. Returned value is backend
        specific. Default implementation returns a value from the mapping
        dictionary.
        """
        return u'{0}.{1}'.format(self.class_name, attribute.name)

    @property
    def reverse_mappings(self):
        return dict((v, k) for k, v in self.mappings.items())
