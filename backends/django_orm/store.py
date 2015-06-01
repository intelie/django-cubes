# -*- coding: utf-8 -*-
from cubes.stores import Store


__all__ = ['DjangoStore', ]


class DjangoStore(Store):
    """
    An example configuration for this store would look like:

    [store]
    type: django
    class_name: hello_world.IrbdBalance
    """
    default_browser_name = "django"

    __options__ = [
        {
            "name": "class_name",
            "type": "string",
            "description": "Name of the model used for queries"
        },
    ]

    def __init__(self, class_name=None, **options):
        super(DjangoStore, self).__init__(**options)
        self.class_name = class_name
