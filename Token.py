#!/usr/bin/env python3


class Token:
    """
    набор слов в кавычках или без,
    сохраняются сами слова и вид кавычек
    """
    def __init__(self, text, quot):
        self.quot = quot
        self.text = text
