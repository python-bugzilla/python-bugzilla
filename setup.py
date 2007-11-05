from distutils.core import setup
from glob import glob
import bugzilla

setup(name='python-bugzilla',
      version=str(bugzilla.version),
      description='Bugzilla XMLRPC access module',
      author='Will Woods',
      author_email='wwoods@redhat.com',
      url='http://wwoods.fedorapeople.org/python-bugzilla/',
      py_modules=['bugzilla'],
      scripts=['bugzilla'],
)
