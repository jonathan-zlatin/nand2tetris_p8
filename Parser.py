"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    # Parser
    
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly 
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the line’s end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment that is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that, 
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """

    @staticmethod
    def remove_comments(cmd):
        comnt_char = cmd.find("//")
        if comnt_char != -1:
            return cmd[:comnt_char]
        return cmd

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.__input_lines = input_file.read().splitlines()
        self.__input_lines = [Parser.remove_comments(elem) for elem in
                              self.__input_lines]
        self.__input_lines = [elem.split() for elem in self.__input_lines if
                              (elem != "")]
        self.__idx = 0
        self.__size = len(self.__input_lines)

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.__idx < self.__size

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        if self.has_more_commands():
            self.__idx += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        arithmetic_list = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not", "shiftleft", "shiftright"]
        cmd = self.__input_lines[self.__idx][0]
        for act in arithmetic_list:
            if act in cmd:
                return "C_ARITHMETIC"
        if "push" in cmd:
            return "C_PUSH"
        elif "pop" in cmd:
            return "C_POP"
        elif "label" in cmd:
            return "C_LABEL"
        elif "if-goto" in cmd:
            return "C_IF"
        elif "goto" in cmd:
            return "C_GOTO"
        elif "function" in cmd:
            return "C_FUNCTION"
        elif "return" in cmd:
            return "C_RETURN"
        elif "call" in cmd:
            return "C_CALL"

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        cmd = self.__input_lines[self.__idx]
        if self.command_type() == "C_ARITHMETIC":
            return cmd[0]
        return cmd[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        legal_cmd = ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]
        if self.command_type() in legal_cmd:
            return self.__input_lines[self.__idx][2]
        return
