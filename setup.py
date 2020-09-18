from setuptools import setup

setup(name='tonie_api',
      version='0.1',
      description='Python library to access the API of the toniecloud. NOT associated with Boxine (tonies.de) in any way.',
      url='https://github.com/moritzj29/tonie_api',
      author='Moritz Jung',
      author_email='18733473+moritzj29@users.noreply.github.com',
      license='MIT',
      packages=['tonie_api'],
      install_requires=[
          'oauthlib',
          'requests_oauthlib'
      ],
      zip_safe=False)