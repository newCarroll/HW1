#!/usr/bin/env python3

import Interpreter as itr


def begin_interpreter():

    interpreter = itr.Interpreter()

    while True:
        text = input('interpreter> ')
        if not text:
            continue

        interpreter.set_text(text)
        result = interpreter.parse_pipe()
        if result:
            print(result, end='')


if __name__ == '__main__':
    begin_interpreter()
