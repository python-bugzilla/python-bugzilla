from distutils.core import setup
from glob import glob
import bugzilla.base

setup(name='python-bugzilla',
      version=str(bugzilla.base.version),
      description='Bugzilla XMLRPC access module',
      author='Will Woods',
      author_email='wwoods@redhat.com',
      url='http://wwoods.fedorapeople.org/python-bugzilla/',
      packages = ['bugzilla'],
      scripts=['bin/bugzilla'],
      data_files=[('share/man/man1', ['bugzilla.1'])],
)
