# mypy: ignore-missing-imports
from setuptools import find_packages, setup # type: ignore
import io
import re
from glob import glob
from os.path import basename, dirname, join, splitext

setup(
  name='dfi',
  version='0.1.0',
  license='BSD-3-Clause',
  description="dotfile installer: symlink config files into place",
  author="Jonathan Simms",
  author_email="slyphon@gmail.com",
  packages=find_packages('src'),
  package_dir={'': 'src'},
  py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
  include_package_data=True,
  zip_safe=False,
  python_requires='>=3.6, <4',
  setup_requires=[
    'pipenv',
  ],
  install_requires=[
    "arrow==0.15.5",
    "attrs==19.3.0",
    "cattrs==1.0.0",
    "click==7.0",
    "more-itertools==8.2.0",
    "python-dateutil==2.8.1",
    "python-dotenv==0.10.5",
    "six==1.14.0",
    "typing-extensions==3.7.4.1",
  ],
  entry_points='''
    [console_scripts]
    dfi=dfi.app:main
  '''
)
