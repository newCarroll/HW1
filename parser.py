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


def wc(words, instream):
    # проверка наличия аргумента: если его нет - считываем из потока
    if len(words) < 2:
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
        filename = words[1]

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


def cat(words, instream):
    # проверка наличия аргумента, если его нет - считываем из потока
    if len(words) < 2:
        stream_value = instream.getvalue()
        instream.close()
        lines = stream_value.split('\n')
        outstream = io.StringIO()
        for line in lines:
            print(line, file=outstream, end='')
            return outstream

    else:
        instream.close()
        filename = words[1]

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


def echo(words, instream):
    instream.close()
    outstream = io.StringIO()
    for word in words[1:]:
            print(word, file=outstream, end=' ')
    print(file=outstream, end='\n')
    return outstream


# в одной строке возможно объявление только одно переменной - первой
# записывает имена и значения переменных в словарь variables
def parse_variables(words):
    eq_index = words[0].find('=')
    var = words[0][:eq_index]
    if words[0] == words[0][:eq_index+1]:
        value = ''
    else:
        value = words[0][eq_index+1:]
    variables[var] = value


# при наличии неидентифицированной команды запускается shell process
def shell_process(words, instream):
    instream.close()
    command = words[0]
    arguments = ''
    for word in words[1:-1]:
        arguments += word + ' '
    if len(words) > 1:
        arguments += words[-1]
    outstream = io.StringIO()
    try:
        if arguments == '':
            output = subprocess.check_output([command], universal_newlines=True)
        else:
            output = subprocess.check_output([command, arguments], universal_newlines=True)
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


# заменяет переменнные в одном токене
def give_value(tokens, token):
    words = token.split()
    for word in words:
        vars = word.split('$')
        for tmp in range(1, len(vars)):
            vars[tmp] = substitution_var(vars[tmp])
        new_command = ''
        for var in vars:
            new_command += var
        tokens.append(new_command)


# разделение команды на токены по кавычкам
def div_by_quotes(tokens, command):
    is_quoting = False
    is_double_quoting = False

    for i, a in enumerate(command):
        if a == '"':
            if not is_quoting:
                if not is_double_quoting:
                    is_double_quoting = True
                    begin_quoting = i
                    tokens += command[:begin_quoting].split()
                else:
                    # закрыли двойные кавычки
                    token = command[begin_quoting + 1: i]
                    give_value(tokens, token)
                    return div_by_quotes(tokens, command[i+1:])
                # при другом варианте ничего не надо делать

        if a == '\'':
            if not is_quoting:
                if not is_double_quoting:
                    is_quoting = True
                    begin_quoting = i
                    tokens += command[:begin_quoting].split()
                # при другом варианте находимся внутри "" - ничего не надо делать
            else:
                if not is_double_quoting:
                    new_command = command[begin_quoting + 1: i]
                    tokens.append(new_command)
                    return div_by_quotes(tokens, command[i + 1:])
                # double_quoting быть не может из условий выше

    if is_quoting or is_double_quoting:
        print('non-closed bracket')
        raise Exception

    give_value(tokens, command)
    return tokens


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
        self.commands_list = text.split('|')

    def parse_pipe(self):
        input_stream = self.Stream()
        for command in self.commands_list:
            try:
                input_stream = self.parse_token(command, input_stream)
            except Exception:
                return
        result = input_stream.getvalue()
        print(result, end='')
        input_stream.close()
        return result

    def parse_token(self, command, input_stream):
        # разделение на токены
        # подстановка переменных
        # words должны быть токенами, напрмиер 'echo $i' - одна команда
        try:
            words = div_by_quotes([], command)
        except Exception:
            raise Exception

        if words[0] not in commands:
            if words[0].find('=') > 0:
                input_stream.close()
                parse_variables(words)
                outstream = io.StringIO()
                return outstream
            else:
                try:
                    return shell_process(words, input_stream)
                except Exception:
                    print("Command or arguments are wrong")
                    raise Exception

        elif words[0] == 'exit':
            exit()

        elif words[0] == 'wc':
            try:
                return wc(words, input_stream)
            except Exception:
                raise Exception

        elif words[0] == 'cat':
            try:
                return cat(words, input_stream)
            except Exception:
                raise Exception

        elif words[0] == 'pwd':
            return pwd(input_stream)

        elif words[0] == 'echo':
            return echo(words, input_stream)


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
