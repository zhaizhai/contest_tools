## Installation

```
cd contest_tools
python setup.py
```

## Usage

Run test cases read from `example.in`.
```
cd contest_tools/examples
contest_tools runtest example
contest_tools runtest example --testnum 3 # run only the third test case
```

Automatically include code snippets.
```
cd contest_tools/examples
contest_tools onefile example ./some_lib_dir
cat example-submit.cpp
```
