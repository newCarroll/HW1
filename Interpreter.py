#!/usr/bin/env python3

from sys import getsizeof, stdin, argv
import os
import io
import subprocess
import unittest

# словарь имен переменных и их значений
variables = {}
# имена наличествующих команд
commands = ['wc', 'echo', 'cat', 'pwd', 'exit']


def wc(command, instream):
    # проверка наличия аргумента: если его нет - считываем из потока
    if len(command) < 2:
        stream_value = instream.getvalue()
        instream.close()
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
        print('{:>3} {:>3} {:>3}'.format(count_line, count_word, count_byte), file=outstream, end='\n')
        return outstream

    else:
        instream.close()
        filename = command[1].words

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
                print('{:>3} {:>3} {:>3} {:>6}'.format(count_line, count_word, count_byte, filename), file=outstream, end='\n')
                return outstream


def cat(command, instream):
    # проверка наличия аргумента, если его нет - считываем из потока
    if len(command) < 2:
        stream_value = instream.getvalue()
        instream.close()
        lines = stream_value.split('\n')
        outstream = io.StringIO()
        for line in lines:
            print(line, file=outstream, end='')
            return outstream

    else:
        instream.close()
        filename = command[1].words

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


def pwd(instream):
    cwd = os.getcwd()
    instream.close()
    outstream = io.StringIO()
    print(cwd, file=outstream, end='\n')
    return outstream


def echo(command, instream):
    instream.close()
    outstream = io.StringIO()
    for part_command in command[1:]:
            print(part_command.words, file=outstream, end=' ')
    print(file=outstream, end='\n')
    return outstream


# в одной строке возможно объявление только одно переменной - первой
# записывает имена и значения переменных в словарь variables
def parse_variables(command):
    eq_index = command[0].words.find('=')
    var = command[0].words[:eq_index]
    if command[0].words == command[0].words[:eq_index+1]:
        if command[1]:
            value = ''
    else:
        value = command[0].words[eq_index+1:]
    variables[var] = value


# при наличии неидентифицированной команды запускается shell process
def shell_process(command, instream):
    instream.close()
    command_to_shell = command[0].words
    arguments = ''
    for part_command in command[1:-1]:
        arguments += part_command.words + ' '
    if len(command) > 1:
        arguments += command[-1].words
    outstream = io.StringIO()
    try:
        if arguments == '':
            output = subprocess.check_output([command_to_shell], universal_newlines=True)
        else:
            output = subprocess.check_output([command_to_shell, arguments], universal_newlines=True)
    except subprocess.CalledProcessError:
        raise Exception
    else:
        print(output, file=outstream, end='')
    return outstream


# замена переменных их значениями
def substitution_var(word):
    if word in variables.keys():
        return variables[word]
    return ''


# разделение команды на токены по кавычкам
# текст без кавычек - токен
# фраза в кавычках - целиком 1 токен
def div_by_quotes(commands, text):
    is_quoting = False
    is_double_quoting = False
    begin_text = 0

    for i, a in enumerate(text):
        if a == '"':
            if not is_quoting:
                if not is_double_quoting:
                    is_double_quoting = True
                    begin_quoting = i
                    words = text[begin_text :i].split()
                    for word in words:
                        new_token = Token(word, 'NOT_QUOTING')
                        commands[-1].append(new_token)
                else:
                    new_token = Token(text[begin_quoting + 1:i], 'DOUBLE_QUOTING')
                    commands[-1].append(new_token)
                    return div_by_quotes(commands, text[i+1:])
        if a == '\'':
            if not is_double_quoting:
                if not is_quoting:
                    is_quoting = True
                    begin_quoting = i
                    words = text[begin_text :i].split()
                    for word in words:
                        new_token = Token(word, 'NOT_QUOTING')
                        commands[-1].append(new_token)
                else:
                    new_token = Token(text[begin_quoting + 1:i], 'QUOTING')
                    commands[-1].append(new_token)
                    return div_by_quotes(commands, text[i + 1:])
        if a == '|':
            if not is_quoting and not is_double_quoting:
                words = text[:i].split()
                for word in words:
                    new_token = Token(word, 'NOT_QUOTING')
                    if len(commands) == 0:
                        commands.append([])
                    commands[-1].append(new_token)
                begin_text = i + 1
                commands.append([])

    if is_quoting or is_double_quoting:
        print('non-closed bracket')
        raise Exception

    words = text[begin_text:].split()
    for word in words:
        new_token = Token(word, 'NOT_QUOTING')
        commands[-1].append(new_token)
    return commands


# заменяет переменнные в одном токене
def give_value(text):
    index_b = -1
    new_text = ''
    split_symbols = [' ', '=', '.', ',', '|']

    for i, c in enumerate(text):
        if c == '$':
            index_b = i
        elif c in split_symbols and index_b != -1:
            index_e = i
            value = substitution_var(text[index_b + 1:index_e])
            new_text += value
            new_text += c
            index_b = -1
        elif index_b == -1:
            new_text += c

    if index_b != -1:
        value = substitution_var(text[index_b + 1:])
        new_text += value
    return new_text


# Токен - слово, либо набор слов в кавычках,
# кавычки могут быть одинарные или двойные
class Token(object):

    def __init__(self, text, quot):
        self.quot = quot
        if quot == 'QUOTING':
            self.words = text
        else:
            self.words = give_value(text)


# для каждой вводимой строки пользователя свой интерпретатор
# обрабатывает строку и вызывает нужные команды
class Interpreter(object):

    # класс для потоков
    class Stream(object):

        def getvalue(self):
            return stdin.read()

        def close(self):
            pass

    def __init__(self, text):
        try:
            self.commands_list = div_by_quotes([[]], text)
        except Exception:
            raise Exception

    def parse_pipe(self):
        input_stream = self.Stream()
        for command in self.commands_list:
            try:
                input_stream = self.parse(command, input_stream)
            except Exception:
                return

        result = input_stream.getvalue()
        print(result, end='')
        input_stream.close()
        return result

    def parse(self, command, input_stream):

        if command[0].words not in commands:
            if command[0].words.find('=') > 0 and command[0].quot == 'NOT_QUOTING':
                input_stream.close()
                parse_variables(command)
                outstream = io.StringIO()
                return outstream
            else:
                try:
                    return shell_process(command, input_stream)
                except Exception:
                    print("Command or arguments are wrong")
                    raise Exception

        elif command[0].words == 'exit':
            exit()

        elif command[0].words == 'wc':
            try:
                return wc(command, input_stream)
            except Exception:
                raise Exception

        elif command[0].words == 'cat':
            try:
                return cat(command, input_stream)
            except Exception:
                raise Exception

        elif command[0].words == 'pwd':
            return pwd(input_stream)

        elif command[0].words == 'echo':
            return echo(command, input_stream)


def begin_interpreter():
    result = True
    while result:
        text = input('interpreter> ')
        if not text:
            continue
        interpreter = Interpreter(text)
        interpreter.parse_pipe()


# класс для тестов
class TestMethods(unittest.TestCase):

    def test_wc(self):
        interpreter = Interpreter('echo 123')
        result = interpreter.parse_pipe()
        self.assertEqual('123 \n', result)

        interpreter = Interpreter('echo "Hello"')
        result = interpreter.parse_pipe()
        self.assertEqual('Hello \n', result)

    def test_var(self):
        interpreter = Interpreter('i=4')
        interpreter.parse_pipe()
        interpreter = Interpreter('echo $i')
        result = interpreter.parse_pipe()
        self.assertEqual('4 \n', result)
        interpreter = Interpreter('echo "$i"')
        result = interpreter.parse_pipe()
        self.assertEqual('4 \n', result)
        interpreter = Interpreter('echo \'$i\'')
        result = interpreter.parse_pipe()
        self.assertEqual('$i \n', result)

        interpreter = Interpreter('echo $j')
        result = interpreter.parse_pipe()
        self.assertEqual(' \n', result)

    def test_pipe(self):
        interpreter = Interpreter('echo 123 | wc | wc')
        result = interpreter.parse_pipe()
        self.assertEqual('  1   3  11\n', result)


if __name__ == '__main__':
    if len(argv) > 1:
        if argv[1] == "test":
            del argv[1:]
            unittest.main()
        else:
            print("Enter \'test\' or keep without arguments")
    else:
        begin_interpreter()
