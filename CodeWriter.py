"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

STACK = 256

commands_dict = {
    "1_arg":
        "@SP\n"
        "M=M-1\n"
        "A=M\n",

    "2_arguments":
        "// SP--:\n"
        "@SP\n"
        "M=M-1\n"
        "A=M\n"
        "D=M\n"
        "@SP\n"
        "M=M-1\n"
        "A=M\n",

    "advance":
        "// SP++:\n"
        "@SP\n"
        "M=M+1\n",

    "add": "M=D+M\n",
    "sub": "M=M-D\n",
    "and": "M=D&M\n",
    "or": "M=D|M\n",
    "neg": "M=-M\n",
    "not": "M=!M\n",
    "shiftleft": "M=M<<\n",
    "shiftright": "M=M>>\n"
}

stack_dict = {
    "push_D_2_Stack":
        "//now we push constant:\n"
        "@SP\n"
        "A=M\n"
        "M=D\n",
    "advance":
        "// SP++:\n"
        "@SP\n"
        "M=M+1\n",
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT",
    "temp": "R5"
}


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def check_eq(self):
        asm = "// we check if y == x\n"
        asm += "@SP   // SP-- (x)\n"
        asm += "M=M-1\n"
        asm += "A=M\n"
        asm += "D=M // D = SP[TOP] D=x\n"

        asm += "@xIsNegative" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "// SP = x\n"
        asm += "D;JLT\n"

        asm += "// x is positive, lets check y:\n"

        asm += "@SP   // SP-- (y)\n"
        asm += "M=M-1\n"
        asm += "A=M\n"
        asm += "D=M // D = SP[TOP] D=y\n"

        asm += "@yIsNegative" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "D;JLT\n"

        asm += "// if you got here - they both non Negatives: (D=y, SP=y)\n"

        asm += "@SP   // SP++ (x)\n"
        asm += "M=M+1\n"
        asm += "A=M\n"
        asm += "D=D-M // D = y-x\n"

        asm += "@true" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "D;JEQ\n"

        asm += "// x != y:\n"
        asm += "D=0\n"
        asm += "@end" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "0;JMP\n"

        asm += "(yIsNegative" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + ") // (SP = y)\n"
        asm += "// x is not negative and y is negative - they are not equal\n"
        asm += "D=0\n"

        asm += "@SP\n"
        asm += "M=M+1 // (SP = x)\n"

        asm += "@end" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "0;JMP\n"

        asm += "(xIsNegative" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + ") // SP = x\n"
        asm += "// we know that x is negative. lets check if y is negative:\n"

        asm += "@SP   // SP-- (SP = y)\n"
        asm += "M=M-1\n"

        asm += "A=M\n"
        asm += "D=M // now D is y\n"

        asm += "@boothNegative" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "D;JLT\n"

        asm += "// y >= 0  and x < 0  so x!=y\n"
        asm += "D=0\n"

        asm += "@SP // SP++ (SP = x)\n"
        asm += "M=M+1\n"

        asm += "@end" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "0;JMP\n"

        asm += "(boothNegative" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + ") // (SP=y) \n"

        asm += "@SP   // (y)\n"
        asm += "A=M\n"
        asm += "D=M // now D is y\n"

        asm += "@SP // SP++(x)\n"
        asm += "M=M+1\n"
        asm += "A=M\n"
        asm += "D=D-M // y-x (M=x)\n"

        asm += "@true" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "D;JEQ\n"

        asm += "D=0 // if you got here x != y\n"
        asm += "@end" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "0;JMP\n"

        asm += "(true" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + ")\n"
        asm += "D=-1\n"

        asm += "(end" + str(self.__inner_func_name) + "." + str(
            self.__inner_func_counter) + ") // change y into D  (SP = X)\n"

        asm += "@SP // SP-- (x->y)\n"
        asm += "M=M-1\n"
        asm += "A=M\n"
        asm += "M=D // y = D\n"
        return asm

    def check_lt(self):
        asm = "// we check if y > x\n"
        asm += "@SP   // SP-- (x)\n"
        asm += "M=M-1\n"
        asm += "A=M\n"
        asm += "D=M // D = SP[TOP] D=x\n"

        asm += "@xIsNegative" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "// SP = x\n"
        asm += "D;JLT\n"

        asm += "// x is positive, lets check y:\n"

        asm += "@SP   // SP-- (y)\n"
        asm += "M=M-1\n"
        asm += "A=M\n"
        asm += "D=M // D = SP[TOP] D=y\n"

        asm += "@yIsNegative" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "D;JLT\n"

        asm += "// if you got here - they both non Negatives: (D=y, SP=y)\n"

        asm += "@SP   // SP++ (x)\n"
        asm += "M=M+1\n"
        asm += "A=M\n"
        asm += "D=D-M // D = y-x\n"

        asm += "@true" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "D;JLT\n"

        asm += "// x <= y:\n"
        asm += "D=0\n"
        asm += "@end" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "0;JMP\n"

        asm += "(yIsNegative" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + ") // (SP = y)\n"
        asm += "// x is not negative and y is negative - x>y\n"
        asm += "D=-1\n"

        asm += "@SP\n"
        asm += "M=M+1 // (SP = x)\n"

        asm += "@end" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "0;JMP\n"

        asm += "(xIsNegative" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + ") // SP = x\n"
        asm += "// we know that x is negative. lets check if y is negative:\n"

        asm += "@SP   // SP-- (SP = y)\n"
        asm += "M=M-1\n"

        asm += "A=M\n"
        asm += "D=M // now D is y\n"

        asm += "@boothNegative" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "D;JLT\n"

        asm += "// y >= 0 > x  so x<y\n"
        asm += "D=0\n"

        asm += "@SP // SP++ (SP = x)\n"
        asm += "M=M+1\n"

        asm += "@end" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "0;JMP\n"

        asm += "(boothNegative" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + ") // (SP=y) \n"

        asm += "@SP   // (y)\n"
        asm += "A=M\n"
        asm += "D=M // now D is y\n"

        asm += "@SP // SP++(x)\n"
        asm += "M=M+1\n"
        asm += "A=M\n"
        asm += "D=D-M // y-x (M=x)\n"

        asm += "@true" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "D;JLT\n"

        asm += "D=0 // if you got here x < y\n"
        asm += "@end" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "0;JMP\n"

        asm += "(true" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + ")\n"
        asm += "D=-1\n"

        asm += "(end" + str(self.__inner_func_name) + "." + str(
            self.__inner_func_counter) + ") // change y into D  (SP = X)\n"

        asm += "@SP // SP-- (x->y)\n"
        asm += "M=M-1\n"
        asm += "A=M\n"
        asm += "M=D // y = D\n"
        return asm

    def check_gt(self):
        asm = "// we check if y > x\n"
        asm += "@SP   // SP-- (x)\n"
        asm += "M=M-1\n"
        asm += "A=M\n"
        asm += "D=M // D = SP[TOP] D=x\n"

        asm += "@xIsNegative" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "// SP = x\n"
        asm += "D;JLT\n"

        asm += "// x is positive, lets check y:\n"

        asm += "@SP   // SP-- (y)\n"
        asm += "M=M-1\n"
        asm += "A=M\n"
        asm += "D=M // D = SP[TOP] D=y\n"

        asm += "@yIsNegative" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "D;JLT\n"

        asm += "// if you got here - they both non Negatives: (D=y, SP=y)\n"

        asm += "@SP   // SP++ (x)\n"
        asm += "M=M+1\n"
        asm += "A=M\n"
        asm += "D=D-M // D = y-x\n"

        asm += "@true" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "D;JGT\n"

        asm += "// x >= y:\n"
        asm += "D=0\n"
        asm += "@end" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "0;JMP\n"

        asm += "(yIsNegative" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + ") // (SP = y)\n"
        asm += "// x is not negative and y is negative - x>y\n"
        asm += "D=0\n"

        asm += "@SP\n"
        asm += "M=M+1 // (SP = x)\n"

        asm += "@end" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "0;JMP\n"

        asm += "(xIsNegative" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + ") // SP = x\n"
        asm += "// we know that x is negative. lets check if y is negative:\n"

        asm += "@SP   // SP-- (SP = y)\n"
        asm += "M=M-1\n"

        asm += "A=M\n"
        asm += "D=M // now D is y\n"

        asm += "@boothNegative" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "D;JLT\n"

        asm += "// y >= 0  and x < 0  so x<y\n"
        asm += "D=-1\n"

        asm += "@SP // SP++ (SP = x)\n"
        asm += "M=M+1\n"

        asm += "@end" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "0;JMP\n"

        asm += "(boothNegative" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + ") // (SP=y) \n"

        asm += "@SP   // (y)\n"
        asm += "A=M\n"
        asm += "D=M // now D is y\n"

        asm += "@SP // SP++(x)\n"
        asm += "M=M+1\n"
        asm += "A=M\n"
        asm += "D=D-M // y-x (M=x)\n"

        asm += "@true" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "D;JGT\n"

        asm += "D=0 // if you got here x > y\n"
        asm += "@end" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "0;JMP\n"

        asm += "(true" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + ")\n"
        asm += "D=-1\n"

        asm += "(end" + str(self.__inner_func_name) + "." + str(
            self.__inner_func_counter) + ") // change y into D  (SP = X)\n"

        asm += "@SP // SP-- (x->y)\n"
        asm += "M=M-1\n"
        asm += "A=M\n"
        asm += "M=D // y = D\n"
        return asm

    @staticmethod
    def get_segment_val(index):
        return "@" + str(index) + "\n" + "D=A\n"

    def push_segment_static(self, indx: int) -> str:
        asm = "//we push from: " + str(self.__inner_name) + "." + str(indx) + "\n"
        asm += "@" + str(self.__inner_name) + "." + str(indx) + "\n"
        asm += "D=M\n"
        asm += "@SP\n"
        asm += "A=M\n"
        asm += "M=D\n"
        return asm

    def pop_segment_static(self, indx: int) -> str:
        asm = "//we pop into: " + str(self.__inner_name) + "." + str(indx) + "\n"
        asm += "@SP\n"
        asm += "M=M-1\n"
        asm += "A=M\n"
        asm += "D=M\n"
        asm += "@" + str(self.__inner_name) + "." + str(indx) + "// the address we will charge to" + "\n"
        asm += "M=D \n"
        return asm

    @staticmethod
    def push_segment(segment: str, indx: int, temp: str) -> str:
        asm = "//we push from: " + str(segment) + " in ind " + str(indx) + "\n"
        asm += "@" + str(segment) + "\n"
        asm += "D=" + temp + "\n"
        asm += "@" + str(indx) + "\n"
        asm += "A=A+D\n"
        asm += "D=M\n"
        asm += "@SP\n"
        asm += "A=M\n"
        asm += "M=D\n"
        return asm

    def pop_segment(self, segment: str, indx: int, temp: str) -> str:
        asm = "//we pop into: " + str(segment) + " in ind " + str(indx) + "\n"
        asm += "@" + str(segment) + "\n"
        asm += "D=" + temp + "\n"
        asm += "@" + str(indx) + "\n"
        asm += "D=A+D\n"
        asm += "@pop_t_" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "M=D\n"
        asm += "@SP\n"
        asm += "M=M-1\n"
        asm += "A=M\n"
        asm += "D=M\n"
        asm += "@pop_t_" + str(self.__inner_func_name) + "." + str(self.__inner_func_counter) + "\n"
        asm += "A=M\n"
        asm += "M=D \n"
        return asm

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.__output_stream = output_stream
        self.__inner_func_counter: int = 0
        self.__inner_name: str = ""
        self.__inner_func_name: str = ""

    def bootstrap(self):
        init_cmd: str = "@256 //init SP = 256\n"
        init_cmd += "D=A\n"
        init_cmd += "@SP\n"
        init_cmd += "M=D\n"
        self.__output_stream.write(init_cmd)
        self.write_call("Sys.init", 0)

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
        self.__inner_name = str(filename)

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        # Your code goes here!
        cmd_asm = "\n//now we do " + command + " command\n"
        unary_list = ["neg", "not", "shiftleft", "shiftright"]
        equal_list = ["eq", "lt", "gt"]
        if command in unary_list:
            cmd_asm += commands_dict["1_arg"]
            cmd_asm += commands_dict[command]
        elif command in equal_list:
            if command == "eq":
                cmd_asm += self.check_eq()
            elif command == "gt":
                cmd_asm += self.check_gt()
            else:
                cmd_asm += self.check_lt()
        else:
            cmd_asm += commands_dict["2_arguments"]
            cmd_asm += commands_dict[command]
        cmd_asm += commands_dict["advance"]
        self.__output_stream.write(cmd_asm)

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.

        stage2_lst = ["argument", "this", "that", "local"]
        cmd_asm = ""
        if command == "C_PUSH":
            if segment == "constant":
                cmd_asm = self.get_segment_val(index) + "//we push constant " + str(index) + "\n"
                cmd_asm += stack_dict["push_D_2_Stack"] + stack_dict["advance"]
            elif segment in stage2_lst:
                cmd_asm = self.push_segment(stack_dict[segment], index, "M") + stack_dict["advance"]
            elif segment == "temp":
                cmd_asm = self.push_segment(stack_dict[segment], index, "A") + stack_dict["advance"]
            elif segment == "pointer":
                cmd_asm = self.push_segment("THIS", index, "A") + stack_dict["advance"]
            else:
                cmd_asm = self.push_segment_static(index) + stack_dict["advance"]

        elif command == "C_POP":
            if segment in stage2_lst:
                cmd_asm = self.pop_segment(stack_dict[segment], index, "M")
            elif segment == "temp":
                cmd_asm = self.pop_segment(stack_dict[segment], index, "A")
            elif segment == "pointer":
                cmd_asm = self.pop_segment("THIS", index, "A")
            else:
                cmd_asm = self.pop_segment_static(index)
        self.__output_stream.write(cmd_asm)

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command.
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        cmd: str = "\n//now we put label: " + label + "\n" \
                   + "(" + label + ")\n\n"
        self.__output_stream.write(cmd)

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        cmd: str = "// now we do unconditional jump to " + label + "\n" + \
                   "@" + label + "\n" + \
                   "0;JMP\n"
        self.__output_stream.write(cmd)

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        cmd: str = "// now we do conditional jump to " + \
                   label + "\n" + \
                   "@SP\n" + \
                   "M=M-1\n" + \
                   "A=M\n" + \
                   "D=M\n" + \
                   "@" + label + "\n" + \
                   "D;JNE\n"
        self.__output_stream.write(cmd)

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command.
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        self.__inner_func_name = function_name
        n_vars = int(n_vars)
        cmd = "(" + function_name + ") // we makes a new function\n"
        self.__output_stream.write(cmd)
        # push to the stack n_vars
        while n_vars > 0:
            self.write_push_pop("C_PUSH", "constant", 0)
            n_vars -= 1

    @staticmethod
    def save_current_state(arg: str) -> str:
        cmd = "@" + arg + " //we save " + arg + "\n"
        cmd += "D=M\n"
        cmd += "@SP\n"
        cmd += "A=M\n"
        cmd += "M=D\n"
        cmd += "@SP\n"
        cmd += "M=M+1\n\n"
        return cmd

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command.
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        self.__inner_func_name = function_name
        cmd = "// now we do write a call " + function_name + "\n"

        cmd += "// we already have n_vars arguments in the stack\n"
        cmd += "// now we start to push the status variables\n\n"
        cmd += "@" + function_name + "$ReturnAddress." + str(self.__inner_func_counter) + "\n"
        cmd += "D=A // We push the return address to the stack  \n"

        cmd += "@SP\n"
        cmd += "A=M\n"
        cmd += "M=D\n"  # we push to SP the return address.
        cmd += "@SP\n"
        cmd += "M=M+1\n\n"

        cmd += "//lets push all the variables:\n"
        cmd += self.save_current_state("LCL")
        cmd += self.save_current_state("ARG")
        cmd += self.save_current_state("THIS")
        cmd += self.save_current_state("THAT")
        # charge ARG to ARG = SP-5-n_args
        cmd += "@SP\n"
        cmd += "D=M\n"
        cmd += "@5\n"
        cmd += "D=D-A\n"
        cmd += "@" + str(n_args) + "\n"
        cmd += "D=D-A\n"
        cmd += "@ARG\n"
        cmd += "M=D\n"  # ARG = SP-5-n_args

        cmd += "@SP\n"
        cmd += "D=M\n"
        cmd += "@LCL\n"
        cmd += "M=D\n\n"  # LCL = SP
        cmd += "// now write go-to and than label:\n"

        self.__output_stream.write(cmd)
        self.write_goto(function_name)
        self.write_label(function_name + "$ReturnAddress." + str(self.__inner_func_counter))
        self.__inner_func_counter += 1

    def write_return(self) -> None:

        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address

        cmd = "\n//now we do return\n"
        cmd += "//frame = LCL - 5\n"
        cmd += "@LCL\n"
        cmd += "D=M\n"
        cmd += "@5\n"
        cmd += "D=D-A\n"  # D = LCL -5
        cmd += "@frame  //frame = LCL - 5\n"
        cmd += "M=D\n"  # finish frame = LCL -5

        cmd += "A=D\n"
        cmd += "D=M\n"

        cmd += "// ReturnAddress = *(frame-5)\n"
        cmd += "@temp." + self.__inner_func_name + "$ReturnAddress." + str(
            self.__inner_func_counter) + "\n"
        cmd += "M=D\n"

        cmd += "// *ARG = pop()  \n"
        cmd += "@SP\n"
        cmd += "M=M-1\n"
        cmd += "A=M\n"
        cmd += "D=M\n"  # D= SP.TOP\n"
        cmd += "@ARG\n"
        cmd += "A=M\n"
        cmd += "M=D //*ARG = SP.TOP\n"

        cmd += "// SP = ARG + 1\n"
        cmd += "@ARG\n"
        cmd += "D=M+1\n"
        cmd += "@SP //SP = ARG + 1\n"
        cmd += "M=D\n"

        cmd += "//THAT = *(frame-1)\n"
        cmd += "@frame // This is 'frame' \n"
        cmd += "D=M\n"
        cmd += "@4\n"
        cmd += "D=D+A\n"  # D = frame -1
        cmd += "@frame\n"  # frame = LCL -1
        cmd += "M=D\n"
        cmd += "A=D\n"
        cmd += "D=M // save *(frame -1)\n"
        cmd += "@THAT\n"
        cmd += "M=D\n"
        cmd += "\n"

        cmd += "//THIS = *(frame-2)\n"
        cmd += "@frame\n"
        cmd += "M=M-1\n"  # frame = LCL -2
        cmd += "A=M\n"
        cmd += "D=M // save *(frame -2)\n"
        cmd += "@THIS\n"
        cmd += "M=D\n"

        cmd += "//ARG = *(frame-3)\n"
        cmd += "@frame\n"
        cmd += "M=M-1\n"  # frame = LCL -3
        cmd += "A=M\n"
        cmd += "D=M // save *(frame -3)\n"
        cmd += "@ARG\n"
        cmd += "M=D\n"

        cmd += "//LCL = *(frame-4)\n"
        cmd += "@frame\n"
        cmd += "M=M-1\n"  # frame = LCL -4
        cmd += "A=M\n"
        cmd += "D=M // save *(frame -4)\n"
        cmd += "@LCL\n"
        cmd += "M=D\n"

        cmd += "//go-to: temp " + self.__inner_func_name + "$ReturnAddress\n"
        cmd += "@temp." + self.__inner_func_name + "$ReturnAddress." + str(
            self.__inner_func_counter) + "\n"
        cmd += "A=M\n"
        cmd += "0;JMP\n"
        self.__output_stream.write(cmd)
