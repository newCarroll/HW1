#!/usr/bin/env python3

import Interpreter as itr
import unittest


class TestMethods(unittest.TestCase):

    def test_wc(self):
        interpreter = itr.Interpreter()
        interpreter.set_text('echo 123')
        result = interpreter.parse_pipe()
        self.assertEqual('123 \n', result)

        interpreter = itr.Interpreter()
        interpreter.set_text('echo "Hello"')
        result = interpreter.parse_pipe()
        self.assertEqual('Hello \n', result)

    def test_var(self):
        interpreter = itr.Interpreter()
        interpreter.set_text('i=4')
        interpreter.parse_pipe()
        interpreter.set_text('echo $i')
        result = interpreter.parse_pipe()
        self.assertEqual('4 \n', result)
        interpreter.set_text('echo "$i"')
        result = interpreter.parse_pipe()
        self.assertEqual('4 \n', result)
        interpreter.set_text('echo \'$i\'')
        result = interpreter.parse_pipe()
        self.assertEqual('$i \n', result)

        interpreter.set_text('echo $j')
        result = interpreter.parse_pipe()
        self.assertEqual(' \n', result)

    def test_pipe(self):
        interpreter = itr.Interpreter()
        interpreter.set_text('echo 123 | wc | wc')
        result = interpreter.parse_pipe()
        self.assertEqual('  1   3   9\n', result)


if __name__ == '__main__':
    unittest.main()
