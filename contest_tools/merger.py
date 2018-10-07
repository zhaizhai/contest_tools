import os, sys, re

std_include = re.compile("\#include +<[A-Za-z0-9_\.]+>")


def strip_empty_lines(lines):
    return list(filter((lambda x: len(x) > 0), lines))


class Block(object):
    def __init__(self, ns, block_id):
        self.ns = ns
        self.block_id = block_id
        self.lines = []
        self.deps = []
        # TODO: technically doesn't work for start of string
        self._re = re.compile("[^A-Za-z0-9_]" + self.block_id[2:] + "[^A-Za-z0-9_]")
        self._re_fq = re.compile("[^A-Za-z0-9_]" + self.ns + self.block_id + "[^A-Za-z0-9_]")

    def appears_in(self, text, fully_qualified=True):
        if fully_qualified:
            return (self._re_fq.search(text) is not None)
        else:
            return (self._re.search(text) is not None)

    def fulltext(self):
        return "\n".join(self.lines)

    def add_to_deps(self, cur_deps):
        if self in cur_deps:
            return
        cur_deps.add(self)
        for dep in self.deps:
            dep.add_to_deps(cur_deps)


# TODO: a problem may arise if one namespace is a prefix of another
class IncludeFile(object):
    ns_start = re.compile("namespace +(.+) +\{")
    ns_end = re.compile("\} *// *namespace")
    id_string = re.compile("::[A-Za-z0-9_]+")

    def __init__(self, name, libdir):
        self.name = name
        self.headers = set()
        self.blocks = []

        self.cur_block = None

        with open(f'{libdir}/{name}.cpp', 'r') as inc_file:
            ret = []
            for line in inc_file:
                if std_include.fullmatch(line.strip()) is not None:
                    self.headers.add(line.strip())
                    continue
                if self.process_namespace(line):
                    continue
                if self.process_comment(line):
                    continue
                if self.cur_block is not None:
                    self.cur_block.lines.append(line.rstrip())
            if self.cur_block is not None:
                raise Exception(f"Error including {name}.cpp, hanging block:\n" + self.cur_block.fulltext())

        for b1 in self.blocks:
            for b2 in self.blocks:
                if b1 is b2: continue
                if b2.appears_in(b1.fulltext(), fully_qualified=False):
                    # print(b1.block_id, 'depends on', b2.block_id)
                    b1.deps.append(b2)

    def open_block(self, block_id):
        if self.cur_block is not None:
            self.close_block()
        self.cur_block = Block(self.name, block_id)

    def close_block(self):
        self.cur_block.lines = strip_empty_lines(self.cur_block.lines)
        self.blocks.append(self.cur_block)
        self.cur_block = None

    def process_namespace(self, line):
        line = line.strip()
        m = IncludeFile.ns_start.fullmatch(line)
        if m is not None:
            assert self.name == m.group(1)
            return True
        if IncludeFile.ns_end.fullmatch(line) is not None:
            self.close_block()
            return True
        return False

    def process_comment(self, line):
        if line[:2] != '//':
            return False
        line = line[2:].strip()
        if line[:2] != '::':
            return True

        assert IncludeFile.id_string.fullmatch(line) is not None
        self.open_block(line)
        return True

    def to_string(self, body):
        needed = set()
        for block in self.blocks:
            if block.appears_in(body):
                block.add_to_deps(needed)
        block_text = []
        for block in self.blocks:
            if block in needed:
                print('Adding', (block.ns + block.block_id))
                block_text.append(block.fulltext())
        if len(block_text) == 0:
            return ""
        return f'namespace {self.name} {{\n\n' + ("\n\n".join(block_text)) + "\n\n}"


class Merger(object):
    def __init__(self, filename, libdir):
        self.libdir = libdir
        self.lib_include_re = re.compile(f"\#include +\"{re.escape(libdir)}/(.+)\.cpp\"") # TODO
        self.headers = set()
        self.lines = []

        with open(filename, 'r') as f:
            for line in f:
                if std_include.fullmatch(line.strip()) is not None:
                    self.headers.add(line.strip())
                    continue
                if self.process_lib_include(line):
                    continue
                self.lines.append(line.rstrip())

        text_lines = filter((lambda x: not isinstance(x, IncludeFile)), self.lines)
        self.body = "\n".join(text_lines)

        for i in range(len(self.lines)):
            inc = self.lines[i]
            if not isinstance(inc, IncludeFile):
                continue
            self.headers = self.headers.union(inc.headers)
            self.lines[i] = inc.to_string(self.body)


    def process_lib_include(self, line):
        m = self.lib_include_re.fullmatch(line.strip())
        if m is None:
            return False
        self.lines.append(IncludeFile(m.group(1), self.libdir))
        return True

    def write(self, outfile):
        for h in sorted(self.headers):
            outfile.write(h + '\n')
        for l in self.lines:
            outfile.write(l + '\n')
