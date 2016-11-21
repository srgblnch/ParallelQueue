# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

__author__ = "Sergi Blanch-Torne"
__email__ = "srgblnchtrn@protonmail.ch"
__copyright__ = "Copyright 2016 Sergi Blanch-Torne"
__license__ = "GPLv3+"
__status__ = "development"

from yamp import version
from setuptools import setup, find_packages

license = ['GPLv3+',
           'License :: OSI Approved :: '
           'GNU General Public License v3 or later (GPLv3+)']

classifiers=['Development Status :: 2 - Pre-Alpha',
             'Intended Audience :: Developers',
             'Intended Audience :: Information Technology',
             'Intended Audience :: Science/Research',
             license[1],
             'Operating System :: POSIX',
             # 'Programming Language :: Cython',
             'Programming Language :: Python',
             'Topic :: Software Development :: Libraries :: '
             'Python Modules',
             ''],

requires = []

recommended = {"psutil": "psutil>=4.4.2"}

setup(name='yamp',
      license=license[0],
      version=version(),
      author="Sergi Blanch-Torn\'e",
      author_email="srgblnchtrn@protonmail.ch",
      classifiers=classifiers,
      packages=find_packages(),
      url="https://github.com/srgblnch/yamp",
      install_requires = requires,
      extras_require = recommended,
      )
