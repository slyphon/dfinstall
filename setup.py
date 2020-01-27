from setuptools import find_packages, setup
import io
import re
from glob import glob
from os.path import basename, dirname, join, splitext

setup(
  name='dfinstall',
  version='0.1.0',
  license='BSD-3-Clause',
  description="dotfile symlink manager",
  author="Jonathan Simms",
  author_email="slyphon@gmail.com",
  packages=find_packages('src'),
  package_dir={'': 'src'},
  py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
  include_package_data=True,
  zip_safe=False,
  python_requires='>=3.7, <4',
  setup_requires=[
    'pytest',
  ],
)
