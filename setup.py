#!/usr/bin/env python
from setuptools import setup


setup(name='squeezy',
      version='0.1',
      description='git merge --squash made easy',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
      ],
      keywords='git merge',
      url='https://github.com/dmedvinsky/git-squeezy',
      author='Dmitry Medvinsky',
      author_email='me@dmedvinsky.name',
      license='MIT',
      packages=['squeezy'],
      entry_points={
          'console_scripts': [
              'git-squeezy = squeezy.squeezy:entry_point',
          ],
      })
