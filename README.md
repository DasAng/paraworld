# How to build

To test the build locally create a virtual environment:

```shell
python -m venv paraworld-env
paraworld-env\Scripts\activate.bat
```

If not already installed then install the build package:

```shell
python -m pip install --upgrade build
```

Then run the build command

```shell
python -m build
```

The will create a gz and whl file inside a **dist** folder

# Test locally

To test the build locally create a virtual environment:

*Windows*:

```shell
python -m venv test-env
test-env\Scripts\activate.bat
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