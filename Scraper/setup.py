from setuptools import setup

setup(name='ZoneBowlingStats',
      version='0.0.2',
      description='Zone Bowling Stats Scraper',
      url='http://github.com/parkourben99/ZoneBowlingStats',
      author='Benjamin Ayles',
      author_email='ben@ayles.com.au',
      license='MIT',
      install_requires=[
          'python-dotenv',
          'requests'
      ],
      zip_safe=False)