from distutils.core import setup
from glob import glob
import bugzilla

setup(name='bugzilla',
      version=str(bugzilla.version),
      description='Bugzilla XMLRPC access module',
      author='Will Woods',
      author_email='wwoods@redhat.com',
      url='http://localhost/',
      py_modules=['bugzilla'],
)
