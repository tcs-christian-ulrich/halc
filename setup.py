from setuptools import setup

setup(name='halc',
      version='0.1',
      description='Hardware Abstraction Layer for Python',
      url='http://github.com/cutec-chris/halc',
      author='Christian Ulrich',
      author_email='github@chris.ullihome.de',
      license='GPLv3',
      packages=['halc'],
      install_requires=[
          'pyudev',
      ],
      zip_safe=False)