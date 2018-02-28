# -*- coding: utf-8 -*-

import contextlib
import os
import sys
from shutil import rmtree

from invoke import Collection, Exit, task

BASE_FOLDER = os.path.dirname(__file__)


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
    'bytecode': 'True to clean up compiled python files, otherwise False.',
    'builds': 'True to clean up build/packaging artifacts, otherwise False.'})
def clean(ctx, docs=True, bytecode=True, builds=True):
    """Cleans the local copy from compiled artifacts."""
    if builds:
        ctx.run('python setup.py clean')

    if bytecode:
        for root, dirs, files in os.walk(BASE_FOLDER):
            for f in files:
                if f.endswith('.pyc'):
                    os.remove(os.path.join(root, f))
            if '.git' in dirs:
                dirs.remove('.git')

    folders = []

    if docs:
        folders.append('docs/_build/')
        folders.append('dist/')

    if bytecode:
        folders.append('src/roslibpy/__pycache__')

    if builds:
        folders.append('build/')
        folders.append('src/roslibpy.egg-info/')

    for folder in folders:
        rmtree(os.path.join(BASE_FOLDER, folder), ignore_errors=True)

@task(help={
      'rebuild': 'True to clean all previously built docs before starting, otherwise False.',
      'check_links': 'True to check all web links in docs for validity, otherwise False.'})
def docs(ctx, rebuild=True, check_links=False):
    """Builds package's HTML documentation."""
    if rebuild:
        clean(ctx)
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


@task(help={
      'checks': 'True to run all checks before testing, otherwise False.'})
def test(ctx, checks=True):
    """Run all tests."""
    if checks:
        check(ctx)

    ctx.run('pytest --doctest-module')

@task(help={
      'release_type': 'Type of release follows semver rules. Must be one of: major, minor, patch.'})
def release(ctx, release_type):
    """Releases the project in one swift command!"""
    if release_type not in ('patch', 'minor', 'major'):
        raise Exit('The release type parameter is invalid.\nMust be one of: major, minor, patch')

    ctx.run('bumpversion %s --verbose' % release_type)
    ctx.run('invoke docs test')
    ctx.run('python setup.py clean --all sdist bdist_wheel')
    ctx.run('twine register dist/*')
    ctx.run('twine upload --skip-existing dist/*.whl dist/*.gz dist/*.zip')


@contextlib.contextmanager
def chdir(dirname=None):
    current_dir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
        yield
    finally:
        os.chdir(current_dir)
