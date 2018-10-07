import os, sys, re
import subprocess

RESET = '\x1b[0m'
BRIGHT = '\x1b[1m'
RED = '\x1b[31m'
GREEN = '\x1b[32m'
BLUE = '\x1b[34m'
CYAN = '\x1b[36m'
MAGENTA = '\x1b[35m'
YELLOW = '\x1b[33m'


def print_green_dot():
    print(BRIGHT + GREEN + '.' + RESET, end='')


class TestCase(object):
    def __init__(self, num, input, expected):
        self.num = num
        self.input = input
        self.expected = expected

    def check(self, res):
        for i, l in enumerate(self.expected):
            if i >= len(res) or res[i] != l:
                self.print_fail(res)
                return False
        return True

    def print_error(self, err):
        print('')
        print(BRIGHT + RED + f"Failure on test #{self.num}, with input:" + RESET)
        print('\n'.join(self.input))
        print(BRIGHT + RED + f"Error from your program:" + RESET)
        print(err)

    def print_fail(self, res):
        print('')
        print(BRIGHT + RED + f"Failure on test #{self.num}, with input:" + RESET)
        print('\n'.join(self.input))
        print(BRIGHT + RED + f"Your output:" + RESET)
        print('\n'.join(res))
        print(BRIGHT + RED + 'Expected:' + RESET)
        print('\n'.join(self.expected))


class TestRunner(object):
    def __init__(self, filename):
        self.filename = filename

    def test(self, case):
        run = subprocess.Popen(["./a.out"],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        input_bytes = bytearray("\n".join(case.input), 'ascii')
        res, err = run.communicate(input=input_bytes, timeout=8)
        # if len(err) > 0:
        #     case.print_error(err)
        #     return False
        res = str(res, 'ascii').split('\n')
        res = [l.strip() for l in res]
        res = [l for l in res if len(l) > 0]
        return case.check(res)

def parse_testcases(filename):
    answer_follows = re.compile('====*')
    new_testcase = re.compile('<<<<*')

    ret = []
    cur_in = []
    cur_out = []
    reading = 'in'
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) == 0 and reading == 'in': continue

            if len(line) == 0 and reading == 'out':
                ret.append((cur_in, cur_out))
                cur_in = []
                cur_out = []
                reading = 'in'
                continue

            if answer_follows.fullmatch(line) is not None:
                assert reading == 'in'
                reading = 'out'
                continue

            if reading == 'in':
                cur_in.append(line)
            else:
                cur_out.append(line)

        lines = list(l.strip() for l in f)

    assert reading == 'out'
    if len(cur_in) > 0:
        ret.append((cur_in, cur_out))
    return [TestCase(n + 1, i, o) for n, (i, o) in enumerate(ret)]
