#!/usr/bin/env python

from os.path import dirname, join, abspath
import sys


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
                'example.hello_world',
            ),
            MIDDLEWARE_CLASSES=(
                'django.middleware.common.CommonMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
            ),
            SITE_ID=1,
            TEST_RUNNER='django.test.simple.DjangoTestSuiteRunner',
            TEST_ROOT=join(dirname(__file__), 'django_cubes', 'tests'),
            TEMPLATE_LOADERS=(
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ),
            ROOT_URLCONF='django_cubes.urls',
            SLICER_MODELS_DIR=join(abspath(dirname(__file__)), 'django_cubes', 'tests', 'assets'),
            SLICER_CONFIG_FILE=join(abspath(dirname(__file__)), 'django_cubes', 'tests', 'assets', 'slicer-sql_backend.ini'),
        )

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

    runtests()
