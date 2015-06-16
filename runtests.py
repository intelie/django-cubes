#!/usr/bin/env python

from os.path import dirname, join
import sys
from optparse import OptionParser


def parse_args():
    parser = OptionParser()
    parser.add_option('--postgresql', action='store_true', dest='USE_POSTGRESQL', default=False)
    parser.add_option('--sqlite', action='store_false', dest='USE_POSTGRESQL')
    return parser.parse_args()


def configure_settings(options):
    from django.conf import settings

    # If DJANGO_SETTINGS_MODULE envvar exists the settings will be
    # configured by it. Otherwise it will use the parameters bellow.
    if not settings.configured:
        params = dict(
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=(
                'django.contrib.contenttypes',
                'django.contrib.auth',
                'django.contrib.sessions',
                'django_cubes',
            ),
            MIDDLEWARE_CLASSES=(),
            SITE_ID=1,
            TEST_RUNNER='django.test.simple.DjangoTestSuiteRunner',
            TEST_ROOT=join(dirname(__file__), 'django_cubes', 'tests'),
        )

        if getattr(options, 'USE_POSTGRESQL', False):
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql_psycopg2',
                    'NAME': 'django_cubes_test',
                    'USER': 'postgres',
                }
            }
        else:
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            }

        params.update(DATABASES=DATABASES)
        # Configure Django's settings
        settings.configure(**params)

    return settings


def get_runner(settings):
    '''
    Asks Django for the TestRunner defined in settings or the default one.
    '''
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)
    return TestRunner(verbosity=1, interactive=True, failfast=False)


def runtests(options=None, labels=None):
    import django

    if not labels:
        labels = ['django_cubes']

    settings = configure_settings(options)
    runner = get_runner(settings)
    if django.VERSION >= (1, 7):
        django.setup()
    sys.exit(runner.run_tests(labels))

if __name__ == '__main__':
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename='/dev/null',
        filemode='a',
    )

    options, labels = parse_args()
    runtests(options, labels)
