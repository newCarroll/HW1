#!/usr/bin/env python3


class VarParser:
    """
    класс для работы с переменныыми,
    а именно сохранять их значения
    и подставлять
    """

    def __init__(self):
        self.variables = {}

    def parse(self, command):
        """
        в одной строке возможно объявление только одно переменной - первой
        записывает имена и значения переменных в словарь variables
        :param command: список входящих токенов
        """
        eq_index = command[0].text.find('=')
        var = command[0].text[:eq_index]
        if command[0].text == command[0].text[:eq_index+1]:
            if not command[1]:
                value = ''
            else:
                raise Exception
        else:
            value = command[0].text[eq_index+1:]
        self.variables[var] = value

    def set_values(self, tokens):
        """
        :param tokens: список токенов
        :return: список токенов, но переменные в тексте без кавычек
        или в двойных заменены на их значения
        """
        for token in tokens:
            if token.quot == 'QUOTING':
                token.text = token.text
            else:
                token.text = self.give_value(token.text)
        return tokens

    def give_value(self, text):
        """
        :param text: текст из одного токена
        :return: заменяет перменные в тексте их значениямм
        """
        index_b = -1
        new_text = ''
        split_symbols = [' ', '=', '.', ',', '|']

        for i, c in enumerate(text):
            if c == '$':
                index_b = i
            elif c in split_symbols and index_b != -1:
                index_e = i
                value = self.substitution_var(text[index_b + 1:index_e])
                new_text += value
                new_text += c
                index_b = -1
            elif index_b == -1:
                new_text += c

        if index_b != -1:
            value = self.substitution_var(text[index_b + 1:])
            new_text += value
        return new_text

    def substitution_var(self, word):
        """
        выполняет подстановку значения в переменную
        :param word: переменная
        :return: значение
        """
        if word in self.variables.keys():
            return self.variables[word]
        return ''
