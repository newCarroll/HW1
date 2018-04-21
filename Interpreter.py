#!/usr/bin/env python3

import PipeParser as pp
from sys import stdin
import Token as tk


def div_by_quotes(tokens_list, text):
    """
    разделение команды на токены по кавычкам
    возвращает список списков токенов по пайпам
    echo 12 "24" | wc -> [[echo 12, 24], [wc]]
    :param text: разделяемый текст
    :param tokens_list: список уже имеющихся токенов,
    который дополняется
    :return: список списков токенов, а именно
    один список для каждой части пайплайна
    """
    is_quoting = False
    is_double_quoting = False
    begin_text = 0
    begin_quoting = -1

    for i, a in enumerate(text):
        if a == '"':
            if not is_quoting:
                if not is_double_quoting:
                    is_double_quoting = True
                    begin_quoting = i
                    words = text[begin_text:i].split()
                    for word in words:
                        new_token = tk.Token(word, 'NOT_QUOTING')
                        tokens_list[-1].append(new_token)
                else:
                    new_token = tk.Token(text[begin_quoting + 1:i],
                                         'DOUBLE_QUOTING')
                    tokens_list[-1].append(new_token)
                    return div_by_quotes(tokens_list, text[i+1:])
        if a == '\'':
            if not is_double_quoting:
                if not is_quoting:
                    is_quoting = True
                    begin_quoting = i
                    words = text[begin_text:i].split()
                    for word in words:
                        new_token = tk.Token(word, 'NOT_QUOTING')
                        tokens_list[-1].append(new_token)
                else:
                    new_token = tk.Token(text[begin_quoting + 1:i], 'QUOTING')
                    tokens_list[-1].append(new_token)
                    return div_by_quotes(tokens_list, text[i + 1:])
        if a == '|':
            if not is_quoting and not is_double_quoting:
                words = text[:i].split()
                for word in words:
                    new_token = tk.Token(word, 'NOT_QUOTING')
                    if len(tokens_list) == 0:
                        tokens_list.append([])
                    tokens_list[-1].append(new_token)
                begin_text = i + 1
                tokens_list.append([])

    if is_quoting or is_double_quoting:
        print('non-closed bracket')
        raise Exception

    words = text[begin_text:].split()
    for word in words:
        new_token = tk.Token(word, 'NOT_QUOTING')
        tokens_list[-1].append(new_token)
    return tokens_list


class Interpreter(object):

    def __init__(self):
        self.__pipe_parser = pp.PipeParser()

    class Stream(object):
        """
        класс потоков,
        результат работы одной части пайпа
        передается следующей части
        """
        def getvalue(self):
            return stdin.read()

        def close(self):
            pass

    def set_text(self, text):
        """
        делит текст на список списков
        токенов по части пайплайна,
        то есть по "|"
        :param text:
        """
        try:
            self.__pipes_list = div_by_quotes([[]], text)
        except Exception:
            raise Exception

    def parse_pipe(self):
        """
        обрабатывает весь пайплайн;
        результат работы части пайплайна
        передает в следющую часть
        :return результат всего пайплайна
        """
        input_stream = self.Stream()
        for part_pipe in self.__pipes_list:
            try:
                input_stream = self.__pipe_parser.parse(part_pipe, input_stream)
            except Exception:
                return

        result = input_stream.getvalue()
        input_stream.close()
        return result
