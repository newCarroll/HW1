#!/usr/bin/env python3

import VariablesParser as vp
import Command
import io


class PipeParser:
    """
    класс, который обрабатывает часть пайплайна
    то есть все между "|", вызывая нужные команды
    """
    def __init__(self):
        self.var_parser = vp.VarParser()
        # имена наличествующих команд
        self.commands = ['wc', 'echo', 'cat', 'pwd', 'exit', 'ls', 'cd']

    def parse(self, command, input_stream):
        """
        :param command: список токенов в части пайпа
        :param input_stream: входящий поток
        :return: поток с результатом данного пайпа
        """
        command = self.var_parser.set_values(command)
        command_name = command[0].text
        if command_name in self.commands:

            if command_name == 'echo':
                new_command = Command.Echo(command[1:], input_stream)
            elif command_name == 'pwd':
                new_command = Command.Pwd(command[1:], input_stream)
            elif command_name == 'exit':
                new_command = Command.Exit(command[1:], input_stream)
            elif command_name == 'wc':
                new_command = Command.Wc(command[1:], input_stream)
            elif command_name == 'ls':
                new_command = Command.Ls(command[1:], input_stream)
            elif command_name == 'cd':
                new_command = Command.Cd(command[1:], input_stream)
            else:
                new_command = Command.Cat(command[1:], input_stream)

            try:
                return new_command.execute()
            except Exception:
                raise Exception

        else:
            if (command[0].text.find('=') > 0
                    and command[0].quot == 'NOT_QUOTING'):

                input_stream.close()
                try:
                    self.var_parser.parse(command)
                except Exception:
                    print(command[1].txt + ' :command  not found')
                    raise Exception
                outstream = io.StringIO()
                return outstream
            else:
                try:
                    command_name = Command.ShellProcess(command, input_stream)
                    return command_name.execute()
                except Exception:
                    print("Command or arguments are wrong")
                    raise Exception
