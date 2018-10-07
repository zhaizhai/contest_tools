import argparse
import inspect
import sys, os
import subprocess

from .merger import Merger
from . import test_runner
from .test_runner import TestRunner


def onefile(prog_name, libdir):
    libdir = libdir.rstrip('/')
    if not os.path.isdir(libdir):
        raise Exception(f'Looking for code snippets in {libdir}, but this directory does not exist.')

    try:
        merger = Merger(f'{prog_name}.cpp', libdir)
    except FileNotFoundError:
        print('Could not find ', file=sys.stderr)
        raise
    merger.write(open(f'{prog_name}-submit.cpp', 'w'))


def runtest(prog_name, testnum=None):
    subprocess.run(["g++", f'./{prog_name}.cpp'], check=True)
    cases = test_runner.parse_testcases(f'./{prog_name}.in')
    runner = TestRunner(prog_name)

    for case in cases:
        if testnum is not None and case.num is not testnum:
            continue
        if not runner.test(case):
            break
        test_runner.print_green_dot()
    print('')


def command_runner(cmd_name, cmd_func, arg_types=None):
    argspec = inspect.getargspec(cmd_func)
    defaults = argspec.defaults or []
    num_args = len(argspec.args) - len(defaults)
    arg_names = argspec.args[:num_args]
    kwarg_names = argspec.args[num_args:]

    arg_types = arg_types or {}
    for name in argspec.args:
        if name not in arg_types:
            arg_types[name] = None

    parser = argparse.ArgumentParser(prog=f'contest_tools {cmd_name}')
    for name in arg_names:
        parser.add_argument(name, type=arg_types[name])

    for name, default_val in zip(kwarg_names, defaults):
        parser.add_argument('--' + name, default=default_val,
                            type=arg_types[name])

    def run_command(cmd_args):
        cmd_args = parser.parse_args(cmd_args)
        run_args = [getattr(cmd_args, name) for name in arg_names]
        run_kwargs = dict((k, getattr(cmd_args, k)) for k in kwarg_names)
        return cmd_func(*run_args, **run_kwargs)
    return cmd_name, run_command


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str)
    parser.add_argument('cmd_args', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command_runners = dict([
        command_runner("onefile", onefile),
        command_runner("runtest", runtest, {
            'testnum': int
        }),
    ])
    candidates = [name for name in command_runners if name.startswith(args.command)]

    if len(candidates) == 0:
        print(f'Unrecognized command {args.command}')
        exit(1)

    if len(candidates) > 1:
        print('Ambiguous command, possibilities are:')
        print('\n'.join(candidates))
        exit(1)

    runner = command_runners[candidates[0]]
    runner(args.cmd_args)


if __name__ == '__main__':
    main()
