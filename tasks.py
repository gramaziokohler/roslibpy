# -*- coding: utf-8 -*-

import contextlib
import os
import sys

from invoke import Collection, task


class Log(object):
    def __init__(self, out=sys.stdout, err=sys.stderr):
        self.out = out
        self.err = err

    def flush(self):
        self.out.flush()
        self.err.flush()

    def write(self, message):
        self.flush()
        self.out.write(message + '\n')
        self.out.flush()

    def info(self, message):
        self.write('[INFO] %s' % message)

    def warn(self, message):
        self.write('[WARN] %s' % message)


log = Log()


@task(default=True)
def help(ctx):
    """Lists available tasks and usage."""
    ctx.run('invoke --help')
    ctx.run('invoke --list')
    log.write('Use "invoke -h <taskname>" to get detailed help for a task.')


@task(help={
    'docs': 'True to generate documentation, otherwise False',
    'bytecode': 'True to clean up compiled python files, otherwise False.'})
def clean(ctx, docs=True, bytecode=True):
    """Cleans the local copy from compiled artifacts."""
    patterns = []
    if docs:
        patterns.append('docs/_build')
        patterns.append('dist/')
    if bytecode:
        patterns.append('src/**/*.pyc')
    for pattern in patterns:
        ctx.run('rm -rf %s' % pattern)


@task(clean, help={
      'check_links': 'True to check all web links in docs for validity, otherwise False.'})
def docs(ctx, rebuild=True, check_links=False):
    """Builds package's HTML documentation."""
    ctx.run('sphinx-build -b doctest docs dist/docs')
    ctx.run('sphinx-build -b html docs dist/docs')
    if check_links:
        ctx.run('sphinx-build -b linkcheck docs dist/docs')


@task()
def check(ctx):
    """Check the consistency of documentation, coding style and a few other things."""
    log.write('Checking MANIFEST.in...')
    ctx.run('check-manifest')

    log.write('Checking ReStructuredText formatting...')
    ctx.run('python setup.py check --strict --metadata --restructuredtext')

    log.write('Running flake8 python linter...')
    ctx.run('flake8 src tests setup.py')

    log.write('Checking python imports...')
    ctx.run('isort --check-only --diff --recursive src tests setup.py')


@task(check)
def test(ctx):
    """Run all tests."""
    ctx.run('pytest --doctest-module')


@contextlib.contextmanager
def chdir(dirname=None):
    current_dir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
        yield
    finally:
        os.chdir(current_dir)
