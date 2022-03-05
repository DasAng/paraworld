# Paraworld

**Paraworld** is a BDD framework using the Gherkin language for writing automated tests. The framework is written in Python 3.9.
It is created to allow the ease of writing concurrent and parallel scenarios.

The framework supports the following distinct features:

- [Run scenarios concurrently](docs/version1.1.0/dependency-graph.md#concurrent-scenarios)
- [Run scenarios in parallel](docs/version1.1.0/dependency-graph.md#parallel-scenarios)
- [Run steps concurrently](docs/version1.1.0/dependency-graph.md#concurrent-steps)
- [Apply ordering and dependency for scenarios](docs/version1.1.0/dependency-graph.md#dependency)
- [Timeline visualization](docs/version1.1.0/dependency-graph.md#timeline-visualization)
- [Dependency visualization](docs/version1.1.0/dependency-graph.md#dependency-graph)
- [Report visualization](docs/version1.1.0/dependency-graph.md#report-visualization)

# Table of contents


- [Install](#install)
- [Documentation](#documentation)
- [Development](#development)
  - [virtual environment](#virtual-environment)
  - [build](#build)
  - [test locally](#test-locally)
  - [publish to TestPyPi](#publish-to-testpypi)


# Install

To use the framework install it through pip:

```shell
pip install paraworld
```

# Documentation

Below is the documentation for all the versions.

- [Version 1.1.2](docs/version1.1.2/main.md#paraworld)
- [Version 1.1.1](docs/version1.1.1/main.md#paraworld)
- [Version 1.1.0](docs/version1.1.0/main.md#paraworld)
- [Version 1.0.0](docs/version1.0.0/main.md#paraworld)

See the [changelog](CHANGELOG.md) for changes.

# Development

If you wish to build the **paraworld** or develop it locally the following will guide you through the process.


## virtual environment

If you are not familiar with Python virtual environment then refer to [this](https://docs.python.org/3/library/venv.html) for further reference.

To test the build locally create a virtual environment:

```shell
python -m venv paraworld-env
```

Then you can activate the virtual env:

*Windows*

```shell
paraworld-env\Scripts\activate.bat
```

*Linux*
```shell
source paraworld-env/bin/activate
```

## build

If not already installed then install the build package:

```shell
python -m pip install --upgrade build
```

Build the report first by doing the following:

*Window*:

```shell
cd report
npm run build_window
cd ..
```

*Linux*:
```shell
cd report
npm run build_linux
cd ..
```

Then run the build command

```shell
python -m build
```

This will create a gz and whl file inside the **dist** folder

## test locally

To test the build locally create a virtual environment:

*Windows*:

```shell
python -m venv test-env
test-env\Scripts\activate.bat
```

*Linux*:
```shell
python -m venv test-env
source test-env/bin/activate
```

Then run pip install the **whl** file that is created by the build command:

```shell
pip install <path to paraworld whl file>
```

So if the whl file is in dist and called **paraworld-0.0.1-py3-none-any.whl** then run:

```shell
pip install dist/paraworld-0.0.1-py3-none-any.whl
```

Now lets test the installed package, by running the test file **test_local_build.py**:

```shell
cd test
python test_local_build.py
```

## publish to TestPyPI

Before publishing to PyPI you can upload to TestPyPI for testing the package:

```shell
twine upload --repository testpypi dist/*
``` 

This will upload whatever is in the **dist** folder to TestPyPI.

To test out the newly published package:

```shell
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ paraworld
```