#!/usr/bin/env python3

from sys import getsizeof
from pathlib import Path
import subprocess
import os
import io


class Exit:
    def __init__(self, arguments, instream):
        instream.close()

    def execute(self):
        exit()


class Cd:
    def __init__(self, arguments, instream):
        self.arguments = arguments
        self.input_stream = instream
        instream.close()

    def execute(self):
        outstream = io.StringIO()
        if len(self.arguments) == 0 and self.input_stream.getvalue():
            return outstream
        elif len(self.arguments) > 1:
            print('cd: too many arguments.')
            raise Exception()
        else:
            new_directory = Path(self.arguments[0].text)
        if len(self.arguments) == 0:
            new_directory = Path.home()
        if new_directory.is_dir():
            os.chdir(new_directory)
        else:
            print('cd: {}: Not a directory.'.format(new_directory))
        return outstream


class Ls:
    def __init__(self, arguments, instream):
        instream.close()
        self.arguments = arguments

    def execute(self):
        outstream = io.StringIO()
        lists_of_files = {}
        current_dir = os.getcwd()

        if len(self.arguments) == 0:
            dirlist = os.listdir(current_dir)
            lists_of_files.update({current_dir: dirlist})
        else:
            text_arguments = []
            for arg in self.arguments:
                text_arguments.append(arg.text)
            for dir in sorted(text_arguments):
                if dir == '~':
                    dir = Path.home()
                try:
                    dirlist = os.listdir(dir)
                except Exception:
                    print('ls: cannot access: {}: '
                          'No such file or directory.'.format(dir),
                          file=outstream, end=os.linesep)

                    return outstream
                lists_of_files.update({dir: dirlist})
        plur = (len(lists_of_files) > 1)
        for (directory, files) in lists_of_files.items():
            if plur:
                print(directory, file=outstream, end=os.linesep)
            for file in files:
                if file[0] != '.':
                    print(file, file=outstream, end=os.linesep)
            if plur:
                print(file=outstream)

        return outstream


class Wc:
    def __init__(self, arguments, instream):
        self.input_stream = instream
        self.arguments = arguments

    def execute(self):
        # проверка наличия аргумента:
        # если его нет - считываем из потока
        if len(self.arguments) == 0:
            stream_value = self.input_stream.getvalue()
            self.input_stream.close()
            lines = stream_value.split('\n')
            count_line = 0
            count_word = 0
            count_byte = 0
            if lines[-1] == '':
                lines = lines[:-1]
            for line in lines:
                count_line += 1
                count_word += len(line.split())
                b = getsizeof(line) - getsizeof('')
                count_byte += b
            outstream = io.StringIO()
            print('{:>3} {:>3} {:>3}'.format(count_line,
                                             count_word, count_byte),
                  file=outstream, end='\n')

            return outstream

        else:
            filename = self.arguments[0].text
            try:
                file = open(filename, 'r')
            except IOError:
                print('wc: ' + filename + ': No such file')
                raise Exception()
            else:
                with file:
                    count_line = 0
                    count_word = 0
                    count_byte = 0
                    for line in file:
                        count_line += 1
                        count_word += len(line.split())
                        b = getsizeof(line) - getsizeof('')
                        count_byte += b
                    outstream = io.StringIO()
                    print('{:>3} {:>3} {:>3} {:>6}'.format(count_line,
                                                           count_word,
                                                           count_byte,
                                                           filename),
                          file=outstream, end='\n')

                    return outstream


class Cat:
    def __init__(self, arguments, instream):
        self.input_stream = instream
        self.arguments = arguments

    def execute(self):
        # проверка наличия аргумента, если его нет - считываем из потока
        if len(self.arguments) == 0:
            stream_value = self.input_stream.getvalue()
            self.input_stream.close()
            lines = stream_value.split('\n')
            outstream = io.StringIO()
            for line in lines:
                print(line, file=outstream, end='')
                return outstream

        else:
            filename = self.arguments[0].text
            try:
                file = open(filename, 'r')
            except IOError:
                print('cat: ' + filename + ': No such file')
                raise Exception()
            else:
                outstream = io.StringIO()
                with file:
                    for line in file:
                        print(line, file=outstream, end='')
                return outstream


class Pwd:
    def __init__(self, arguments, instream):
        instream.close()
        self.arguments = arguments

    def execute(self):
        cwd = os.getcwd()
        outstream = io.StringIO()
        print(cwd, file=outstream, end='\n')
        return outstream


class Echo:
    def __init__(self, arguments, instream):
        instream.close()
        self.arguments = arguments

    def execute(self):
        outstream = io.StringIO()
        for arg in self.arguments:
            print(arg.text, file=outstream, end=' ')
        print(file=outstream, end='\n')
        return outstream


class ShellProcess:
    """
    при наличии неидентифицированной
    команды запускается shell process

    """
    def __init__(self, pipe_part, instream):
        self.command = pipe_part[0].text
        instream.close()
        self.arguments = pipe_part[1:]

    def execute(self):
        shell_arguments = ''
        for arg in self.arguments[:-1]:
            shell_arguments += arg.text + ' '
        if len(self.arguments) > 0:
            shell_arguments += self.arguments[-1].text
        outstream = io.StringIO()
        try:
            if shell_arguments == '':
                output = subprocess.check_output([self.command],
                                                 universal_newlines=True)
            else:
                output = subprocess.check_output([self.command,
                                                  shell_arguments],
                                                 universal_newlines=True)
        except subprocess.CalledProcessError:
            raise Exception
        else:
            print(output, file=outstream, end='')
        return outstream
