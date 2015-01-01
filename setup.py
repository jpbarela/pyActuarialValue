from setuptools import setup

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to "
          "RST")
    read_md = lambda f: open(f, 'r').read()

setup(name='pyActuarialValue',
      version='0.1',
      description='An implementation of the HHS Actuarial Value calculator',
      long_description=read_md('README.md'),
      url='https://github.com/jpbarela/pyActuarialValue',
      author='J.P. Barela',
      author_email='barela@jpbarela.com',
      license='Apache 2.0',
      keywords='actuarial value',
      packages=['av', 'healthplan', 'av.database'],
      package_data={
          'av': ['data/av.db']
      },
      install_requires=[
          'enum34',
          'pypandoc',
          'sqlalchemy'
      ],
      test_suite='nose.collector',
      tests_require=[
          'coverage',
          'nose',
          'rednose'
      ],
      scripts=['bin/av', 'bin/seed_data'],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Financial and Insurance Industry',
          'Intended Audience :: Healthcare Industry',
          'License :: OSI Approved :: Apache Software License',
          'Natural Language :: English'
      ])
