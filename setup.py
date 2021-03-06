from distutils.core import setup

setup(name="paraworld",
      packages=["conclave"],
      version="1.6.2",
      description="A BDD framework for running parallel and concurrent tests",
      long_description="A BDD framework for writing concurrent and parallel tests",
      author="DasAng",
      author_email="",
      url="https://github.com/DasAng/paraworld",
      license="MIT",
      download_url="http://pypi.python.org/pypi/paraworld",
      keywords=["gherkin", "parallel", "bdd"],
      scripts=[],
      classifiers=["Programming Language :: Python",
                   "Programming Language :: Python :: 3",
                   ],
      platforms = ['any'],
      install_requires=['gherkin-official==22.0.0', 'jinja2==3.0.2','psutil==5.8.0','requests==2.26.0'],
      include_package_data=True
      )