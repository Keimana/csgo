import main
import re

class DEDOSSemantic:
    def __init__(self, Terminals, Sequence):
        self.Terminals = Terminals
        self.position = 0
        self.key = []
        self.value = []
        self.Sequence = Sequence
        self.currentSequence = None
        self.c1 = '\0'
        self.c2 = len(self.value) - 1
        self.tool = {'neg': False, 'pos': True}
        self.Output = []
        self.GlobalVar = {}
        self.GlobalDatatype = {}
        self.FunctionVarParam = {}
        self.FuncVarSeq = {}
        self.FuncVariable = {}
        self.FuncVariableDatatype = {}
        self.FuncSequence = []
        self.CurrentFuncSequence = {}
        self.FuncPosition = 0
        self.c11 = '\0'
        self.c22 = len(self.value) - 1
        self.UnivVar = []
        self.GlobalArray = []
        self.Funchatray = []

    def keyval_fix(self):
        for d in self.Terminals:
            for key, value in d.items():
                self.key.append(key)
                self.value.append(value)
        self.currentSequence = self.Sequence[self.position]
        ckeys = list(self.currentSequence.keys())
        cvalues = list(self.currentSequence.values())
        self.c1 = ckeys[0]
        self.c2 = cvalues[0]

    def line_ctr(self, current):
        try:
            linectr = 1
            for _ in range(current):
                if self.value[_] == '"\\n"':
                    linectr += 1
            return linectr
        except:
            self.Output.append("|||Semantic Error: Line Counter not working")

    def next(self):
        self.position += 1
        if self.position >= len(self.Sequence):
            self.c1 = '\0'
            self.c2 = len(self.value)-1
        else:
            self.currentSequence = self.Sequence[self.position]
            ckeys = list(self.currentSequence.keys())
            cvalues = list(self.currentSequence.values())
            self.c1 = ckeys[0]
            self.c2 = cvalues[0]

    def prev(self):
        self.position -= 1
        if self.position < 0:
            self.c1 = '\0'
            self.c2 = len(self.value)-1
        else:
            self.currentSequence = self.Sequence[self.position]
            ckeys = list(self.currentSequence.keys())
            cvalues = list(self.currentSequence.values())
            self.c1 = ckeys[0]
            self.c2 = cvalues[0]

    def output_statement(self):
        output = ""
        try:
            while self.c1 != '<output statement->':
                if self.c1 == '<parameter+>':
                    output = self.parameter()  # Get the output from self.parameter
                if self.c1 == '\0':
                    break
                self.next()
            self.Output.append(output)
        except:
            start = self.c2
            while self.c1 != '<output statement->':
                self.next()
            end = self.c2
            plant = "".join(self.value[start:end])
            self.Output.append(f"|||Semantic Error: in {plant}: Line {self.line_ctr(self.c2)}")

    def parameter(self):
        try:
            start = self.c2 + 1
            while self.c1 != '<parameter->':  # Getting the parameter values
                self.next()
            if '<parameter->' == self.c1:
                end = self.c2
            param_values = self.value[start:end]  # Storing the parameter values
            if param_values == []:  # if no parameter, return empty string
                return ''
            param_str = "".join(param_values)  # make the parameter into string
            param_orig = param_str  # Save original text (e.g. it might include quotes or #x)
            
            # Do your normal variable replacement
            param_str = self.replace_variables(param_str, self.GlobalVar)
            if len(param_str) == 3 and param_str.count("\'") == 2:
                param_str = param_str.replace("\'", "\"")
            if '-' in param_str:  # preserve '-' for negative numbers
                param_str = str(param_str.replace('-', '-'))
            param_str = self.replace_variables(param_str, self.GlobalVar)
            param_str = param_str.replace("\n", "\\n").replace('True', 'pos').replace('False', 'neg').replace('-', '-')
            
            # === NEW GLOBAL VARIABLE CHECK ===
            # For each variable in GlobalVar that appears in the original parameter text,
            # check if that variable’s value is a string (i.e. declared with strike).
            # If so, and if the arithmetic operators %, /, or a binary minus appear in the expression,
            # then report a semantic error.

            for var in self.GlobalVar:
                if var in param_orig:
                    # Here we assume that variables declared with strike are stored as strings.
                    if isinstance(self.GlobalVar[var], str):
                        # Check if an arithmetic operator is present in the evaluated parameter expression.
                        if "%" in param_str or "/" in param_str or re.search(r"\s-\s", param_str):
                            self.Output.append(
                                f"|||Semantic Error: operator used on strike type variable '{var}' is not allowed: Line {self.line_ctr(self.c2)}"
                            )
                            return ""
            # === END NEW GLOBAL VARIABLE CHECK ===
            
            try:
                try:
                    param_tuple = eval(param_str.replace("-", "-"), None, self.tool)  # Evaluate the parameter string
                except:
                    printerr = []
                    parama = eval(param_str.replace("-", "-"), None, self.tool)
                    for item in parama:
                        item = str(item)
                        try:
                            a = eval(item, None, self.tool)
                            printerr.append(str(a))
                        except:
                            if item.count('#') == 1:
                                self.Output.append(
                                    f"|||Semantic Error: Undeclared Variable: Line {self.line_ctr(self.c2)}"
                                )
                            try:
                                a = eval(item.replace("-", "-"), None, self.tool)
                            except Exception as e:
                                a = str(e)
                                b = a.replace('int', 'inst').replace('str', 'strike').replace('float', 'flank')
                                if a == "unsupported operand type(s) for %: 'str' and 'int'":
                                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c2)}")
                                elif a == "unsupported operand type(s) for /: 'str' and 'int'":
                                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c2)}")
                                elif a == "unsupported operand type(s) for -: 'str' and 'int'":
                                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c2)}")
                                elif a == "unsupported operand type(s) for +: 'int' and 'str'":
                                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c2)}")
                                elif a in ['can only concatenate str (not "int") to str', 'can only concatenate str (not "float") to str']:
                                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c2)}")
                                elif a == "unsupported operand type(s) for +: 'float' and 'str'":
                                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c2)}")
                                elif a == 'can only concatenate list (not "int") to list':
                                    self.Output.append(
                                        f"|||Semantic Error: Whole arrays cannot be used in math expressions: Line {self.line_ctr(self.c2)}"
                                    )
                                elif "unmatched ']'" in a or "list index out of range" in a:
                                    self.Output.append(f"|||Semantic Error: Array Index range exceeded: Line {self.line_ctr(self.c2)}")
                                else:
                                    if item.count('#') >= 1:
                                        self.Output.append(
                                            f"|||Semantic Error: Undeclared Variable: Line {self.line_ctr(self.c2)}"
                                        )
                                    else:
                                        item = '\"' + item.replace('"', '') + '\"'
                                        a = eval(item.replace("-", "-"), None, self.tool)
                                printerr.append(str(a))
                    param_str = '\"' + "".join(printerr) + '\"'
                    param_tuple = eval(param_str.replace("\n", "\\n").replace("\t", "\\t"), None, self.tool)
            except Exception as e:
                a = str(e)
                b = a.replace('int', 'inst').replace('str', 'strike').replace('float', 'flank')
                if a == "unsupported operand type(s) for %: 'str' and 'int'":
                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c2)}")
                elif a == "unsupported operand type(s) for /: 'str' and 'int'":
                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c2)}")
                elif a == "unsupported operand type(s) for -: 'str' and 'int'":
                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c2)}")
                elif a == "unsupported operand type(s) for +: 'int' and 'str'":
                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c2)}")
                elif a in ['can only concatenate str (not "int") to str', 'can only concatenate str (not "float") to str']:
                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c2)}")
                elif a == "unsupported operand type(s) for +: 'float' and 'str'":
                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c2)}")
                elif "unmatched ']'" in a or "list index out of range" in a:
                    self.Output.append(f"|||Semantic Error: Array Index range exceeded: Line {self.line_ctr(self.c2)}")
                elif a == 'can only concatenate list (not "int") to list':
                    self.Output.append(f"|||Semantic Error: Whole arrays cannot be used in math expressions: Line {self.line_ctr(self.c2)}")
                else:
                    if param_str.count('#') >= 1:
                        self.Output.append(f"|||Semantic Error: Undeclared Variable: Line {self.line_ctr(self.c2)}")
                    else:
                        param_str = '\"' + "".join(param_str).replace('"','') + '\"'
                        param_tuple = eval(param_str.replace("\n", "\\n").replace("\t", "\\t"), None, self.tool)
            if isinstance(param_tuple, tuple):
                param_str = "".join(str(item) for item in param_tuple)
            else:
                param_str = str(param_tuple)
            param_fixed = param_str.replace('True', 'pos').replace('False', 'neg').replace('-', '-')
            return param_fixed
        except Exception as e:
            a = str(e)
            if "unmatched ']'" in a or "list index out of range" in a:
                self.Output.append(f"|||Semantic Error: Array Index range exceeded: Line {self.line_ctr(self.c2)}")
            else:
                self.Output.append(f"|||Semantic Error: Undeclared Variable: Line {self.line_ctr(self.c2)}")

    def replace_variables(self, string, variable_dict):
        for key, value in sorted(variable_dict.items(), reverse=True):
            string = string.replace(key, str(value))
        return string

    def condition(self):
        try:
            start = self.c2  # get the conditionand evaluate if true or false
            end = 0
            self.next()
            while '<condition->' != self.c1:
                self.next()
            if '<condition->' == self.c1:
                end = self.c2

            cond_exp = " ".join(self.value[start:end + 1]).replace('"\\n"', "").replace("-", "-")
            cond_exp = self.replace_variables(cond_exp, self.GlobalVar)
            try:
                if "False" == (str(eval(str(cond_exp), None, self.tool))):  # return neg or pos instead of False or True
                    result = "neg"
                else:
                    result = "pos"
                return result
            except Exception as e:
                a = str(e)
                b = a.replace('int', 'inst').replace('str', 'strike').replace('float', 'flank')
                error_list = ["unsupported operand type(s) for +: 'int' and 'str'",
                              'can only concatenate str (not "int") to str',
                              'can only concatenate str (not "float") to str',
                              "unsupported operand type(s) for +: 'float' and 'str'",
                              "'<' not supported between instances of 'int' and 'str'",
                              "'<' not supported between instances of 'float' and 'str'",
                              "'>=' not supported between instances of 'int' and 'str'",
                              "'>=' not supported between instances of 'float' and 'str'",
                              "'<=' not supported between instances of 'int' and 'str'",
                              "'<=' not supported between instances of 'float' and 'str'",
                              "'>' not supported between instances of 'int' and 'str'",
                              "'>' not supported between instances of 'float' and 'str'"]

                if a in error_list:
                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c2)}")
                elif "unexpected EOF while parsing" in a:
                    self.Output.append(
                        f"|||Semantic Error: strike cannot be operated with other data types: Line {self.line_ctr(self.c2)}")
                else:
                    self.Output.append(f"|||Semantic Error: Undeclared Variable in {cond_exp}: Line {self.line_ctr(self.c2)}")
        except:
            self.Output.append(f"|||Semantic Error: in condition: Line {self.line_ctr(self.c2)}")

    def fixer_condition(self):
        if self.c1 == '<condition statement+>':
            self.next()
        while self.c1 != '<condition statement->':
            if self.c1 == '<condition statement+>':
                self.fixer_condition()
            self.next()

    def condition_statement(self):
        try:
            while self.c1 != '<condition+>':  # condition for if statement.
                self.next()
            cond_result = self.condition()
            if cond_result == "pos":
                while self.c1 != '<if with body->':
                    if self.c1 == '<output statement+>':
                        self.output_statement()
                    elif self.c1 == '<condition statement+>':
                        self.condition_statement()
                    elif self.c1 in ['<watch loop+>', '<force loop+>']:
                        self.loop_statement()
                    elif self.c1 == '<initialization statement+>':
                        self.initialization_statement()
                    elif self.c1 == '<pass+>':
                        pass
                    elif self.c1 == '<function call statement+>':
                        self.function_call_statement()
                    self.next()
                while self.c1 != '<condition statement->':
                    self.next()
            else:  # for elib and elsa
                while self.c1 not in ['<condition statement->', '<elif with body+>', '<else with body+>']:
                    if self.c1 == '<condition statement+>':
                        self.fixer_condition()
                    self.next()
                ctr = 0
                while self.c1 != '<condition statement->' and self.c1 != '<else with body+>':
                    if self.c1 != '<elif with body+>':
                        while self.c1 != '<condition+>':
                            self.next()
                        cond_result = self.condition()
                        if cond_result == "pos" and ctr == 0:
                            while self.c1 != '<elif with body->':
                                ctr = 1
                                if self.c1 == '<output statement+>':
                                    self.output_statement()
                                elif self.c1 == '<condition statement+>':
                                    self.condition_statement()
                                elif self.c1 in ['<force loop+>', '<watch loop+>']:
                                    self.loop_statement()
                                elif self.c1 == '<initialization statement+>':
                                    self.initialization_statement()
                                elif self.c1 == '<pass+>':
                                    pass
                                elif self.c1 == '<function call statement+>':
                                    self.function_call_statement()
                                self.next()
                        else:
                            while self.c1 != '<elif with body->':
                                self.next()
                    self.next()
                if self.c1 == '<else with body+>' and ctr == 0:
                    if cond_result == "neg":
                        while self.c1 != '<condition statement->':
                            if self.c1 == '<output statement+>':
                                self.output_statement()
                            elif self.c1 == '<condition statement+>':
                                self.condition_statement()
                            elif self.c1 in ['<force loop+>', '<watch loop+>']:
                                self.loop_statement()
                            elif self.c1 == '<initialization statement+>':
                                self.initialization_statement()
                            elif self.c1 == '<pass+>':
                                pass
                            elif self.c1 == '<function call statement+>':
                                self.function_call_statement()
                            self.next()
                else:
                    while self.c1 != '<condition statement->':
                        self.next()
        except:
            self.Output.append(f"|||Semantic Error: in condition statement: Line {self.line_ctr(self.c2)}")

    def fixer_loop_condition(self):
        if self.c1 == '<loop condition+>':
            self.next()
        while self.c1 != '<loop condition->':
            if self.c1 == '<loop condition+>':
                self.fixer_loop_condition()
            self.next()

    def loop_condition(self):
        try:
            while self.c1 != '<condition+>':  # skip the structure to condition
                self.next()
            cond_result = self.condition()  # get result of condition if neg or pos
            if cond_result == "pos":
                while self.c1 != '<loop if->':  # run the loop if body if cond_result is pos
                    if self.c1 == '<output statement+>':
                        self.output_statement()
                    elif self.c1 == '<loop condition+>':
                        a = self.loop_condition()
                        if a == "__STOP__":
                            while self.c1 != '<loop body->':
                                self.next()
                            return "__STOP__"
                    elif self.c1 in ['<force loop+>', '<watch loop+>']:
                        self.loop_statement()
                    elif self.c1 == '<initialization statement+>':
                        self.initialization_statement()
                    elif self.c1 == '<pass>':
                        pass
                    elif self.c1 == '<continue>':
                        continue
                    elif self.c1 == '<function call statement+>':
                        self.function_call_statement()
                    elif self.c1 == '<break>':
                        while self.c1 != '<loop body->':
                            self.next()
                        return "__STOP__"
                    self.next()
                while self.c1 != '<loop condition->' and self.c1 != '<loop body->':
                    self.next() #after executing the loop if body then skip to end of condition

            else:  # if "loop if" is neg then go to loop elib or loop elsa
                while self.c1 not in ['<loop condition->', '<loop elif+>', '<loop else+>']:
                    if self.c1 == '<loop condition+>':
                        self.fixer_loop_condition()
                    self.next()
                ctr = 0  # for checking if it run a condition body once

                while self.c1 != '<loop condition->' and self.c1 != '<loop else+>':
                    if self.c1 != '<loop elif+>':
                        while self.c1 != '<condition+>':
                            self.next()
                        cond_result = self.condition()
                        if cond_result == "pos" and ctr == 0: # if condition is true in elib then run its body and check if there is already body run before this
                            while self.c1 != '<loop elif->':
                                ctr = 1
                                if self.c1 == '<output statement+>':
                                    self.output_statement()
                                elif self.c1 == '<loop condition+>':
                                    a = self.loop_condition()
                                    if a == "__STOP__":
                                        while self.c1 != '<loop body->':
                                            self.next()
                                        return "__STOP__"
                                elif self.c1 in ['<force loop+>', '<watch loop+>']:
                                    self.loop_statement()
                                elif self.c1 == '<initialization statement+>':
                                    self.initialization_statement()
                                elif self.c1 == '<pass>':
                                    pass
                                elif self.c1 == '<continue>':
                                    continue
                                elif self.c1 == '<function call statement+>':
                                    self.function_call_statement()
                                elif self.c1 == '<break>':
                                    while self.c1 != '<loop body->':
                                        self.next()
                                    return "__STOP__"
                                self.next()
                        else:
                            while self.c1 != '<loop elif->':  # if loop if and loop elif is error then go loop else
                                self.next()
                    self.next()

                if self.c1 == '<loop else+>' and ctr == 0: # if loop if and loop elib is false then run loop else, also check if a condition body is already ran
                    if cond_result == "neg":
                        while self.c1 != '<loop condition->':
                            if self.c1 == '<output statement+>':
                                self.output_statement()
                            elif self.c1 == '<loop condition+>':
                                a = self.loop_condition()
                                if a == "__STOP__":
                                    while self.c1 != '<loop body->':
                                        self.next()
                                    return "__STOP__"
                            elif self.c1 in ['<force loop+>', '<watch loop+>']:
                                self.loop_statement()
                            elif self.c1 == '<initialization statement+>':
                                self.initialization_statement()
                            elif self.c1 == '<pass>':
                                pass
                            elif self.c1 == '<continue>':
                                continue
                            elif self.c1 == '<function call statement+>':
                                self.function_call_statement()
                            elif self.c1 == '<break>':
                                while self.c1 != '<loop body->':
                                    self.next()
                                return "__STOP__"
                            self.next()
                else:
                    while self.c1 != '<loop condition->':
                        self.next()
        except:
            self.Output.append(f"|||Semantic Error: in loop condition statement: Line {self.line_ctr(self.c2)}")

    def loop_statement(self):
        try:
            if self.c1 == '<force loop+>':
                self.next()
                id1 = str(self.value[self.c2])
                id ={id1 : 0}
                self.GlobalVar.update(id)
                self.GlobalDatatype.update({id1: "inst"})
                self.next()
                start = self.c2 + 1
                while self.c1 != '<perim->':
                    self.next()
                end = self.c2
                h1 = "".join(self.value[start:end]).replace("(", '').replace("-", "-")
                self.next()
                startpos_loop = self.position #this is the variable in which they will go
                h1 = self.replace_variables(h1, self.GlobalVar)  # replace the id in param_str with value
                h1 = h1.replace("\n", "\\n")
                try:
                    result = eval(h1, None, self.tool) #it will return the range parameter, either 1 or tuple
                except:
                    self.Output.append(f"|||Semantic Error: range parameter \"range({h1})\": Line {self.line_ctr(self.c2)}")

                if isinstance(result, int):  # Checking if the result is an integer
                    if result <= 0:
                        while self.c1 != '<force loop->':
                            self.next()
                    else:
                        for _ in range(result): #for i in range(){print(a)}   startpos_loop = 1
                            if self.c1 == '<force loop->':
                                break
                            if _ > 0: #it will go to startpos_loop after the 2nd iteration of the loop
                                id = {id1: _}
                                self.GlobalVar.update(id)
                                self.GlobalDatatype.update({id1: "inst"})
                                self.position = startpos_loop
                                self.currentSequence = self.Sequence[self.position]
                                ckeys = list(self.currentSequence.keys())
                                cvalues = list(self.currentSequence.values())
                                self.c1 = ckeys[0]
                                self.c2 = cvalues[0]

                            while self.c1 != '<force loop->':  # execute the force loop body
                                if self.c1 == '<output statement+>':
                                    self.output_statement()
                                elif self.c1 == '<loop condition+>':
                                    a = self.loop_condition()
                                    if a == "__STOP__":
                                        while self.c1 != '<loop body->':
                                            self.next()
                                        break
                                elif self.c1 in ['<force loop+>', '<watch loop+>']:
                                    self.loop_statement()
                                elif self.c1 == '<initialization statement+>':
                                    self.initialization_statement()
                                elif self.c1 == '<pass>':
                                    pass
                                elif self.c1 == '<continue>':
                                    continue
                                elif self.c1 == '<function call statement+>':
                                    self.function_call_statement()
                                elif self.c1 == '<break>':
                                    while self.c1 != '<loop body->':
                                        self.next()
                                    break
                                self.next()
                            self.next()
                        self.prev()
                else:
                    if len(result) == 1:
                        stop = result[0]
                        if stop <= 0:
                            while self.c1 != '<force loop->':
                                self.next()
                        else:
                            for _ in range(stop):
                                if self.c1 == '<force loop->':
                                    break
                                if _ > 0:
                                    id = {id1: _}
                                    self.GlobalVar.update(id)
                                    self.GlobalDatatype.update({id1: "inst"})
                                    self.position = startpos_loop
                                    self.currentSequence = self.Sequence[self.position]
                                    ckeys = list(self.currentSequence.keys())
                                    cvalues = list(self.currentSequence.values())
                                    self.c1 = ckeys[0]
                                    self.c2 = cvalues[0]

                                while self.c1 != '<force loop->':
                                    if self.c1 == '<output statement+>':
                                        self.output_statement()
                                    elif self.c1 == '<loop condition+>':
                                        a = self.loop_condition()
                                        if a == "__STOP__":
                                            while self.c1 != '<loop body->':
                                                self.next()
                                            break
                                    elif self.c1 in ['<force loop+>', '<watch loop+>']:
                                        self.loop_statement()
                                    elif self.c1 == '<initialization statement+>':
                                        self.initialization_statement()
                                    elif self.c1 == '<pass>':
                                        pass
                                    elif self.c1 == '<continue>':
                                        continue
                                    elif self.c1 == '<function call statement+>':
                                        self.function_call_statement()
                                    elif self.c1 == '<break>':
                                        while self.c1 != '<loop body->':
                                            self.next()
                                        break
                                    self.next()
                                self.next()
                            self.prev()
                    elif len(result) == 2:
                        start, stop = result
                        self.GlobalVar[id1] = start
                        if start >= stop:
                            while self.c1 != '<force loop->':
                                self.next()
                        else:
                            for _ in range(start, stop):
                                if self.c1 == '<force loop->':
                                    break
                                if _ > start:
                                    id = {id1: self.GlobalVar[id1] + 1}
                                    self.GlobalVar.update(id)
                                    self.GlobalDatatype.update({id1: "inst"})
                                    self.position = startpos_loop
                                    self.currentSequence = self.Sequence[self.position]
                                    ckeys = list(self.currentSequence.keys())
                                    cvalues = list(self.currentSequence.values())
                                    self.c1 = ckeys[0]
                                    self.c2 = cvalues[0]

                                while self.c1 != '<force loop->':
                                    if self.c1 == '<output statement+>':
                                        self.output_statement()
                                    elif self.c1 == '<loop condition+>':
                                        a = self.loop_condition()
                                        if a == "__STOP__":
                                            while self.c1 != '<loop body->':
                                                self.next()
                                            break
                                    elif self.c1 in ['<force loop+>', '<watch loop+>']:
                                        self.loop_statement()
                                    elif self.c1 == '<initialization statement+>':
                                        self.initialization_statement()
                                    elif self.c1 == '<pass>':
                                        pass
                                    elif self.c1 == '<continue>':
                                        continue
                                    elif self.c1 == '<function call statement+>':
                                        self.function_call_statement()
                                    elif self.c1 == '<break>':
                                        while self.c1 != '<loop body->':
                                            self.next()
                                        break
                                    self.next()
                                self.next()
                            self.prev()
                    elif len(result) == 3:
                        start, stop, step = result
                        print('try', start, stop, step)
                        self.GlobalVar[id1]= start
                        if step == 0:
                            self.Output.append(f"|||Semantic Error: Increment should not be {step}: Line {self.line_ctr(self.c2)}")
                        elif start < stop and step > 0:
                            for _ in range(start, stop, step):
                                if self.c1 == '<force loop->':
                                    break
                                if _ > start:
                                    id = {id1: self.GlobalVar[id1] + step}
                                    self.GlobalVar.update(id)
                                    self.GlobalDatatype.update({id1: "inst"})
                                    self.position = startpos_loop
                                    self.currentSequence = self.Sequence[self.position]
                                    ckeys = list(self.currentSequence.keys())
                                    cvalues = list(self.currentSequence.values())
                                    self.c1 = ckeys[0]
                                    self.c2 = cvalues[0]

                                while self.c1 != '<force loop->':
                                    if self.c1 == '<output statement+>':
                                        self.output_statement()
                                    elif self.c1 == '<loop condition+>':
                                        a = self.loop_condition()
                                        if a == "__STOP__":
                                            while self.c1 != '<loop body->':
                                                self.next()
                                            break
                                    elif self.c1 in ['<force loop+>', '<watch loop+>']:
                                        self.loop_statement()
                                    elif self.c1 == '<initialization statement+>':
                                        self.initialization_statement()
                                    elif self.c1 == '<pass>':
                                        pass
                                    elif self.c1 == '<continue>':
                                        continue
                                    elif self.c1 == '<function call statement+>':
                                        self.function_call_statement()
                                    elif self.c1 == '<break>':
                                        while self.c1 != '<loop body->':
                                            self.next()
                                        break
                                    self.next()
                                self.next()
                            self.prev()
                        elif start > stop and step < 0:
                            for _ in range(start, stop, step):
                                if self.c1 == '<force loop->':
                                    break
                                if _ < start:
                                    id = {id1: self.GlobalVar[id1] + step}
                                    self.GlobalVar.update(id)
                                    self.GlobalDatatype.update({id1: "inst"})
                                    self.position = startpos_loop
                                    self.currentSequence = self.Sequence[self.position]
                                    ckeys = list(self.currentSequence.keys())
                                    cvalues = list(self.currentSequence.values())
                                    self.c1 = ckeys[0]
                                    self.c2 = cvalues[0]

                                while self.c1 != '<force loop->':
                                    if self.c1 == '<output statement+>':
                                        self.output_statement()
                                    elif self.c1 == '<loop condition+>':
                                        a = self.loop_condition()
                                        if a == "__STOP__":
                                            while self.c1 != '<loop body->':
                                                self.next()
                                            break
                                    elif self.c1 in ['<force loop+>', '<watch loop+>']:
                                        self.loop_statement()
                                    elif self.c1 == '<initialization statement+>':
                                        self.initialization_statement()
                                    elif self.c1 == '<pass>':
                                        pass
                                    elif self.c1 == '<continue>':
                                        continue
                                    elif self.c1 == '<function call statement+>':
                                        self.function_call_statement()
                                    elif self.c1 == '<break>':
                                        while self.c1 != '<loop body->':
                                            self.next()
                                        break
                                    self.next()
                                self.next()
                            self.prev()
                        else:
                            self.Output.append(f"|||Semantic Error: in force Loop: Line {self.line_ctr(self.c2)}")
                    else:
                        self.Output.append(f"|||Semantic Error: in force Loop: Line {self.line_ctr(self.c2)}")
                del self.GlobalVar[id1]
                del self.GlobalDatatype[id1]

            elif self.c1 == '<watch loop+>': # if loop statement is a watch loop then go here
                self.next()
                startpos_loop = self.position
                loop_ctr = 0
                cond_result = self.condition()
                breaker = ""
                if cond_result == "pos":
                    while cond_result == "pos" and breaker == "":
                        if loop_ctr > 0:
                            self.position = startpos_loop
                            self.currentSequence = self.Sequence[self.position]
                            ckeys = list(self.currentSequence.keys())
                            cvalues = list(self.currentSequence.values())
                            self.c1 = ckeys[0]
                            self.c2 = cvalues[0]
                            cond_result = self.condition()
                            if cond_result == "neg":
                                while self.c1 != '<watch loop->':
                                    self.next()
                                break
                        while self.c1 != '<watch loop->':
                            if self.c1 == '<output statement+>':
                                self.output_statement()
                            elif self.c1 == '<loop condition+>':
                                a = self.loop_condition()
                                if a == "__STOP__":
                                    while self.c1 != '<loop body->':
                                        self.next()
                                    breaker = "__STOP__"
                                    break
                            elif self.c1 in ['<force loop+>', '<watch loop+>']:
                                self.loop_statement()
                            elif self.c1 == '<initialization statement+>':
                                self.initialization_statement()
                            elif self.c1 == '<pass>':
                                pass
                            elif self.c1 == '<continue>':
                                continue
                            elif self.c1 == '<function call statement+>':
                                self.function_call_statement()
                            elif self.c1 == '<break>':
                                while self.c1 != '<loop body->':
                                    self.next()
                                breaker = "__STOP__"
                                break
                            self.next()
                        loop_ctr += 1
                        self.next()
                elif cond_result == "neg":  # if result is neg then skip loop statement
                    while self.c1 != '<watch loop->':
                        self.next()
                else:
                    self.Output.append(f"|||Semantic Error: in watch Loop: Line {self.line_ctr(self.c2)}")
        except:
            self.Output.append(f"|||Semantic Error: in loop statement: Line {self.line_ctr(self.c2)}")

    def declaration(self):
        try:
            ctr = 0
            value = []
            valuetype = ""
            operator = ""
            datatype = ""
            declared_id = ""
            idtype = "not array"
            inputctr = 0
            # getting all the structure of declaration : <declaration> <id> <operator> <allowed value>
            while self.c1 != '<declaration->':
                if self.c1 == '<data type>' and ctr < 2: # inst #a = 2
                    datatype = self.value[self.c2]
                    ctr += 1
                elif self.c1 == '<id or array+>':
                    start = self.position
                    self.next()
                    while self.c1 != '<id or array->':
                        if self.c1 == '<id or array+>':
                            while self.c1 != '<id or array->':
                                self.next()
                        self.next()
                    end = self.position + 1
                    id_sequence = self.Sequence[start:end]

                    if self.Sequence[start]['<id or array+>'] == self.Sequence[end - 1][
                        '<id or array->']:  # if sequence is only one
                        declared_id = self.value[self.Sequence[start]['<id or array+>']]
                    else: # if sequence is many
                        declared_id = self.value[self.Sequence[start]['<id or array+>']:self.Sequence[end-1]['<id or array->']]
                        declared_id.append(self.value[self.c2])
                        declared_id = "".join(declared_id).replace('"\\n"', "")
                elif self.c1 == '<assignment operator>':
                    operator = self.value[self.c2]
                elif self.c1 == '<allowed value+>':
                    start = self.position
                    while self.c1 != '<allowed value->':
                        self.next()
                    end = self.position + 1
                    valuesequence = self.Sequence[start:end]
                    if self.Sequence[start]['<allowed value+>'] == self.Sequence[end - 1]['<allowed value->']: # if sequence is only one
                        value = self.value[self.Sequence[start]['<allowed value+>']]
                    else:  # if sequence is many
                        value = self.value[
                                self.Sequence[start]['<allowed value+>']: self.Sequence[end - 1]['<allowed value->']]
                        value.append(self.value[self.c2])
                        print(value)
                        value = [item for item in value if item != '"\\n"']
                        value1 = "".join(value).replace("-", "-")
                        print(value1, datatype)
                # check if id is array or not
                    if any('<index+>' in d for d in id_sequence):
                        idtype = "array"
                    else:
                        pass

                    if idtype == "array": #if id is array
                        valuetype = "array"
                        value1 = "".join(value)
                        variables = [key for key in self.GlobalVar.keys() if key in value1]
                        for variable in variables:
                            value1 = value1.replace(variable, str(self.GlobalVar[variable]))
                        try:
                            if datatype == "inst" or datatype == "flank":
                                value1 = eval(value1.replace("-", "-"), None, self.tool)
                            else:
                                value1 = eval(value1, None, self.tool)
                        except:
                            self.Output.append(f"|||Semantic Error: value \"{value1}\": Line {self.line_ctr(self.c2)}")
                        if type(value1) == list:
                            if datatype == "inst":
                                if all(isinstance(value, int) and not isinstance(value, bool) for value in value1):
                                    pass
                                else:
                                    self.Output.append(f"|||Semantic Error: Not all value in array are inst \"{''.join(value)}\": Line {self.line_ctr(self.c2)}")
                            elif datatype == "flank":
                                if all(isinstance(value, float) and not isinstance(value, bool) for value in value1):
                                    pass
                                else:
                                    self.Output.append(f"|||Semantic Error: Not all value in array are flank \"{''.join(value)}\": Line {self.line_ctr(self.c2)}")
                            elif datatype == "tool":
                                if all(isinstance(value, bool) for value in value1):
                                    pass
                                else:
                                    self.Output.append(f"|||Semantic Error: Not all value in array are tool \"{''.join(value)}\": Line {self.line_ctr(self.c2)}")
                            elif datatype == "chat":
                                if all(isinstance(value, str) and len(value) == 1 for value in value1):
                                    pass
                                else:
                                    self.Output.append(f"|||Semantic Error: Not all value in array are chat \"{''.join(value)}\": Line {self.line_ctr(self.c2)}")
                            elif datatype == "strike":
                                if all(isinstance(value, str) for value in value1):
                                    pass
                                else:
                                    self.Output.append(f"|||Semantic Error: Not all value in array are strike \"{''.join(value)}\": Line {self.line_ctr(self.c2)}")
                        start_index = declared_id.find('[')
                        end_index = declared_id.find(']')
                        array_length = declared_id[start_index + 1:end_index]
                        try:
                            array_length = int(self.replace_variables(array_length, self.GlobalVar)) #add try except here para if di sya int
                        except:
                            self.Output.append(f"|||Semantic Error: Index is not inst \"{array_length}\": Line {self.line_ctr(self.c2)}")
                        declared_id = declared_id.split('[')[0]
                        if array_length != len(value1): #try except para pag sa inst #a[3] = 23
                            self.Output.append(f"|||Semantic Error: Index ({array_length}) is not the same length as the value ({len(value1)}): Line {self.line_ctr(self.c2)}")
                        else:
                            if declared_id not in self.GlobalArray:
                                self.GlobalArray.append(declared_id)

                    elif idtype == "not array":
                        #if id is not array then do this...
                        if any('<input+>' in d for d in valuesequence):
                            valuetype = "input"
                        elif any('<id>' in d for d in valuesequence): # if initialize an id
                            valuetype = "hasid"
                        elif any('<chatlit>' in d for d in valuesequence): # if initialize chat
                            valuetype = "chat"
                        elif any('<tool value>' in d for d in valuesequence): # if initialize a tool
                            valuetype = "tool"
                        elif any('<math expression+>' in d for d in valuesequence): #if initialize a inst flank or strike
                            valuetype = "inst flank strike"
                self.next() # for while self.c1 != '<declaration->':

            # evaluating the value gathered
            if valuetype == "input": # inst #a = info(....)
                inputctr = 1
                value = "".join(value).replace('"\\n"', '')
                desc_display = value[4:-1]#.replace("info", "")
                variables = [key for key in self.GlobalVar.keys() if key in desc_display]
                for variable in variables:
                    desc_display = desc_display.replace(variable, str(self.GlobalVar[variable]))
                try:
                    try:
                        desc_display = desc_display.replace("True", "pos").replace("False", "neg")
                        desc_display = eval(desc_display)
                    except:
                        desc_display = '\"' + str(desc_display).replace('"', '').replace("True", "pos").replace(
                            "False", "neg") + '\"'
                        desc_display = eval(desc_display)
                except:
                    self.Output.append(f"|||Semantic Error: info parameter invalid \"{desc_display}\": Line {self.line_ctr(self.c2)}")
                try:
                    value = eval(main.inputter(desc_display), None, self.tool)
                    if datatype == "strike" or datatype == "chat":
                        value = str(value)
                except:
                    self.Output.append(f"|||Runtime Error: user input: Line {self.line_ctr(self.c2)}")
                valuetype = datatype
                if valuetype == "inst" or valuetype == "flank":
                    value2 = str(value).replace('-', '-')
                else:
                    value2 = value
                self.Output.append(f"{desc_display} {value2} \n")

            elif valuetype != "" and valuetype != "hasid":  # inst #a and for evaluating array
                if len(value) > 1 and type(value) == list:
                    value1 = [item for item in value if item != '"\\n"']
                    value = "".join(value1)
                if '-' in value:
                    value = str(value.replace('-', '-'))
                try: 
                    value = eval(value, None, self.tool)
                except:
                    value = "".join(value).replace('-', '-')
                    value = self.replace_variables(value, self.GlobalVar)
                    value = eval(str(value), None, self.tool)

            elif valuetype == "hasid" and datatype in ["inst", "flank","tool"]:  # inst #a = #b
                if len(value) > 1 and type(value) == list:
                    value1 = [item for item in value if item != '"\\n"']
                    value = "".join(value1)
                if '-' in value:
                    value = str(value.replace('-', '-'))
                try:
                    valuestr = self.replace_variables(value, self.GlobalVar)
                    value = eval(valuestr, None, self.tool)
                except:
                    value = "".join(value)
                    valuestr = self.replace_variables(value, self.GlobalVar)
                    value = eval(valuestr, None, self.tool)
                if value == "True":
                    value = 'pos'
                elif value == "False":
                    value = 'neg'

            elif valuetype == "hasid" and datatype == "strike":  # strike #b = #a
                if len(value) > 1 and type(value) == list:
                    value1 = [item for item in value if item != '"\\n"']
                    value = "".join(value1)
                if '-' in value:
                    value = str(value.replace('-', '-'))
                valuestr = self.replace_variables(str(value), self.GlobalVar)
                value = eval(valuestr, None, self.tool)

            elif valuetype == "hasid" and datatype == "chat":  # chat #c = #d
                if len(value) > 1 and type(value) == list:
                    value1 = [item for item in value if item != '"\\n"']
                    value = "".join(value1)
                if '-' in value:
                    value = str(value.replace('-', '-'))
                valuestr = self.replace_variables(str(value), self.GlobalVar)
                value = eval(valuestr, None, self.tool)
                if value != 1:
                    self.Output.append(f"|||Semantic Error: Data type mismatch \"{datatype} {declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}\": Line {self.line_ctr(self.c2)}")

            # matching the datatype to value if not error.
            if datatype == "chat":
                if ((valuetype == datatype or valuetype == "hasid") and (repr(value).count("'") == 2 and (len(repr(value)) == 3 or len(repr(value)) == 2))) or inputctr == 1:
                    if inputctr == 1 and len(str(value)) != 1:
                        print("X",inputctr == 1 ,"X",value != 1, value)
                        self.Output.append(
                            f"|||Runtime Error: Data type mismatch \"{datatype} {declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                    self.GlobalVar.update({declared_id: f"\"{value}\""})
                    self.GlobalDatatype.update({declared_id: "chat"})
                elif valuetype == "array":
                    self.GlobalVar.update({declared_id: value})
                    self.GlobalDatatype.update({declared_id: "chat"})
                elif datatype != "" and operator == "" and value == []:
                    self.GlobalVar.update({declared_id: ""})
                    self.GlobalDatatype.update({declared_id: "chat"})
                else:
                    self.Output.append(f"|||Semantic Error: Data type mismatch \"{datatype} {declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}\": Line {self.line_ctr(self.c2)}")
            elif datatype == "tool":
                if type(value) == list:
                    value = ['pos' if item else 'neg' for item in value]
                if value == "True":
                    value = 'pos'
                elif value == "False":
                    value = 'neg'
                if (valuetype == datatype or valuetype == "hasid") and value in ['neg', 'pos']:
                    self.GlobalVar.update({declared_id: value})
                    self.GlobalDatatype.update({declared_id: "tool"})
                elif (valuetype == datatype or valuetype == "array"):
                    self.GlobalVar.update({declared_id: value})
                    self.GlobalDatatype.update({declared_id: "tool"})
                elif datatype != "" and operator == "" and value == []:
                    self.GlobalVar.update({declared_id: ""})
                    self.GlobalDatatype.update({declared_id: "tool"})
                else:
                    if inputctr == 1:
                        self.Output.append(f"|||Runtime Error: Data type mismatch \"{datatype} {declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                    else:
                        self.Output.append(f"|||Semantic Error: Data type mismatch \"{datatype} {declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}\": Line {self.line_ctr(self.c2)}")
            elif datatype in ["inst", "flank", "strike"]:
                if datatype == "inst":
                    try:
                        if value - int(value) != 0:
                            if inputctr == 1:
                                self.Output.append(
                                    f"|||Runtime Error: Data type mismatch \"{datatype} {declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                            else:
                                self.Output.append(
                                    f"|||Semantic Error: Data type mismatch \"{datatype} {declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                        else:
                            value = int(value)
                    except:
                        pass
                math_type = type(value)
                if math_type == int == type(value) and datatype == "inst" or (
                        datatype == "inst" and valuetype == "hasid") or (valuetype == "array" and datatype == "inst"):
                    self.GlobalVar.update({declared_id: value})
                    self.GlobalDatatype.update({declared_id: "inst"})
                elif math_type == float == type(value) and datatype == "flank" or (
                        datatype == "flank" and valuetype == "hasid") or (valuetype == "array" and datatype == "flank"):
                    self.GlobalVar.update({declared_id: value})
                    self.GlobalDatatype.update({declared_id: "flank"})
                elif math_type == str == type(value) and datatype == "strike" or (
                        datatype == "strike" and valuetype == "hasid"):
                    self.GlobalVar.update({declared_id: f'\"{value}\"'})
                    self.GlobalDatatype.update({declared_id: "strike"})
                elif valuetype == "array" and datatype == "strike":
                    self.GlobalVar.update({declared_id: value})
                    self.GlobalDatatype.update({declared_id: "strike"})
                elif datatype != "" and operator == "" and value == []:
                    self.GlobalVar.update({declared_id: value})
                    self.GlobalDatatype.update({declared_id: datatype})
                else:
                    if inputctr == 1:
                        self.Output.append(
                            f"|||Runtime Error: Data type mismatch \"{datatype} {declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                    else:
                        self.Output.append(
                            f"|||Semantic Error: Data type mismatch \"{datatype} {declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
        except Exception as e:
            print(e)
            self.Output.append(f"|||Semantic Error: in declaration: Line {self.line_ctr(self.c2)}")

    def function(self):
        try:
            self.next()
            id = self.value[self.c2]  # get id
            self.next()
            startparam = self.c2  # get function parameter
            if self.c1 == '<function parameter+>':
                while self.c1 != '<function parameter->':
                    self.next()
                end = self.c2 + 1
                a = "".join(self.value[startparam:end])
                keys = [key.strip() for key in a.split(",")]
                param_ctr = {key: None for key in keys}
            else:
                param_ctr = []
            while self.c1 != '<function body+>':
                self.next()
            startpos = self.position
            while self.c1 != '<function body->':
                self.next()
            end_pos = self.position
            self.FunctionVarParam.update({id: param_ctr})
            self.FuncVarSeq.update({id: [startpos, end_pos]})
        except:
            self.Output.append(f"|||Semantic Error: in function: Line {self.line_ctr(self.c2)}")

    def initialization_statement(self):
        try:
            function_call = 0
            inputter = 0
            value = None
            idtype = "not array"
            # getting all the structure of initialization : <id> <operator> <allowed value>
            while '<initialization statement->' != self.c1:
                if self.c1 == '<id or array+>':
                    start = self.position
                    self.next()
                    while self.c1 != '<id or array->':
                        if self.c1 == '<id or array+>':
                            while self.c1 != '<id or array->':
                                self.next()
                        self.next()
                    end = self.position + 1
                    id_sequence = self.Sequence[start:end]
                    if self.Sequence[start]['<id or array+>'] == self.Sequence[end - 1][
                        '<id or array->']:  # if sequence is only one
                        declared_id = self.value[self.Sequence[start]['<id or array+>']]
                    else: # if sequence is many
                        declared_id = self.value[self.Sequence[start]['<id or array+>']:self.Sequence[end-1]['<id or array->']]
                        declared_id.append(self.value[self.c2])
                        declared_id = "".join(declared_id)
                elif self.c1 == '<assignment operator>':
                    operator = self.value[self.c2]
                elif self.c1 == '<allowed value+>':
                    start1 = self.position
                    start = self.c2
                    while self.c1 != '<allowed value->':
                        self.next()
                    end1 = self.position + 1
                    end = self.c2
                    valuesequence = self.Sequence[start1:end1]
                    if self.Sequence[start1]['<allowed value+>'] == self.Sequence[end1 - 1][
                        '<allowed value->']:  # if sequence is only one
                        value = self.value[self.Sequence[start1]['<allowed value+>']]
                    else:  # if sequence is many
                        value = self.value[
                                self.Sequence[start1]['<allowed value+>']: self.Sequence[end1 - 1]['<allowed value->']]
                        value.append(self.value[self.c2])
                        value = [item for item in value if item != '"\\n"']
                        value1 = "".join(value)
                # check if id is array or not
                    if any('<index+>' in d for d in id_sequence):
                        idtype = "array"
                    else:
                        pass
                self.next()  # for while self.c1 != '<declaration->':

            if idtype == "array":  # add later
                for item in valuesequence:
                    if '<function call statement+>' in item:
                        function_call = 1
                    if '<input+>' in item:
                        inputter = 1
                if function_call == 1 and inputter != 1:
                    value = self.function_call_statement()
                elif inputter == 1 and function_call != 1:
                    value = "".join(self.value[start:end+1]).replace('"\\n"', '')
                    desc_display = value[4:-1]#.replace("info", "")
                    variables = [key for key in self.GlobalVar.keys() if key in desc_display]
                    for variable in variables:
                        desc_display = desc_display.replace(variable, str(self.GlobalVar[variable]))
                    try:
                        try:
                            desc_display = desc_display.replace("True", "pos").replace("False", "neg")
                            desc_display = eval(desc_display)
                        except:
                            desc_display = '\"' + str(desc_display).replace('"', '').replace("True", "pos").replace(
                                "False", "neg") + '\"'
                            desc_display = eval(desc_display)
                    except:
                        self.Output.append(f"|||Semantic Error: info parameter invalid\"{desc_display}\": Line {self.line_ctr(self.c2)}")
                    try:
                        value = eval(main.inputter(desc_display), None, self.tool)
                    except:
                        self.Output.append(f"|||Runtime Error: user input: Line {self.line_ctr(self.c2)}")
                    if self.GlobalDatatype[declared_id[:declared_id.find('[')]] == "inst" or self.GlobalDatatype[declared_id[:declared_id.find('[')]] == "flank":
                        value2 = str(value).replace('-', '-')
                    else:
                        value2 = value
                    self.Output.append(f"{desc_display} {value2} \n")
                elif self.value[start] == self.value[end] and function_call != 1 and inputter != 1:
                    value = "".join(self.value[start])
                elif self.value[start] != self.value[end] and function_call != 1 and inputter != 1:
                    value = "".join(self.value[start:end]).replace('"\\n"', "").replace("-", "-")
                    variables = [key for key in self.GlobalVar.keys() if key in value]
                    for variable in variables:
                        value = value.replace(variable, str(self.GlobalVar[variable]))
                    value = eval(value , None, self.tool)

                if str(value) == "True":
                    value = "pos"
                elif str(value) == "False":
                    value = "neg"
                if declared_id.count('[') == 2 and declared_id.count(']') == 2:
                    self.Output.append(f"|||Semantic Error: Array as index is not allowed: Line {self.line_ctr(self.c2)}")
                else:
                    start_index = declared_id.find('[')
                    end_index = declared_id.find(']')
                    array_length = declared_id[start_index + 1:end_index]
                try:
                    array_length = int(
                        self.replace_variables(array_length, self.GlobalVar))  # add try except here para if di sya int
                    print(array_length, "ASEDAS")
                except:
                    print(type(array_length), self.GlobalVar)
                    self.Output.append(f"|||Semantic Error: Index is not inst \"{array_length}\": Line {self.line_ctr(self.c2)}")
                declared_id = declared_id.split('[')[0]
                if declared_id in self.GlobalVar and declared_id in self.GlobalArray:
                    if self.GlobalDatatype[declared_id] == "flank":
                        if str(value).replace('True', 'pos').replace('False', 'neg') in ['pos', 'neg']:
                            if inputter == 1:
                                self.Output.append(
                                    f"|||Runtime Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                            else:
                                self.Output.append(
                                    f"|||Semantic Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                        elif operator == "=":
                            self.GlobalVar[declared_id][array_length] = float(value)
                        elif operator == "+=":
                            self.GlobalVar[declared_id][array_length] = self.GlobalVar[declared_id][array_length] + float(value)
                        elif operator == "-=":
                            self.GlobalVar[declared_id][array_length] = self.GlobalVar[declared_id][array_length] - float(value)
                        elif operator == "*=":
                            self.GlobalVar[declared_id][array_length] = self.GlobalVar[declared_id][array_length] * float(value)
                        elif operator == "/=":
                            self.GlobalVar[declared_id][array_length] = self.GlobalVar[declared_id][array_length] / float(value)
                        elif operator == "%=":
                            self.GlobalVar[declared_id][array_length] = self.GlobalVar[declared_id][array_length] % float(value)
                    elif self.GlobalDatatype[declared_id] == "inst":
                        if str(value).replace('True', 'pos').replace('False', 'neg') in ['pos', 'neg']:
                            if inputter == 1:
                                self.Output.append(
                                    f"|||Runtime Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                            else:
                                self.Output.append(
                                    f"|||Semantic Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                        elif operator == "=":
                            self.GlobalVar[declared_id][array_length] = int(value)
                        elif operator == "+=":
                            self.GlobalVar[declared_id][array_length] = self.GlobalVar[declared_id][array_length] + int(value)
                        elif operator == "-=":
                            self.GlobalVar[declared_id][array_length] = self.GlobalVar[declared_id][array_length] - int(value)
                        elif operator == "*=":
                            self.GlobalVar[declared_id][array_length] = self.GlobalVar[declared_id][array_length] * int(value)
                        elif operator == "/=":
                            self.GlobalVar[declared_id][array_length] = self.GlobalVar[declared_id][array_length] / int(value)
                        elif operator == "%=":
                            self.GlobalVar[declared_id][array_length] = self.GlobalVar[declared_id][array_length] % int(value)
                    elif self.GlobalDatatype[declared_id] == "strike":
                        if operator == "=":
                            self.GlobalVar[declared_id][array_length] = str(value)
                        elif operator == "+=":
                            # aa = str(value)
                            aa = value
                            self.GlobalVar[declared_id][array_length] = self.GlobalVar[declared_id][array_length].replace("\"", "") + aa
                            self.GlobalVar[declared_id][array_length] = "\"" + self.GlobalVar[declared_id][array_length].replace("\"", "").replace("\n",
                                                                                                       "\\n") + "\""
                            if self.GlobalVar[declared_id][array_length].count("\'") > 2 and '+' not in self.GlobalVar[declared_id][array_length] and '-' not in \
                                    self.GlobalVar[declared_id][array_length] and '*' not in self.GlobalVar[declared_id][array_length] and '/' not in self.GlobalVar[declared_id] and '%' not in self.GlobalVar[declared_id][array_length]:
                                self.GlobalVar[declared_id][array_length] = self.GlobalVar[declared_id][array_length].replace("\"", "")
                        elif operator in ["-=", "*=", "/=", "%="]:
                            self.Output.append(
                                f"|||Semantic Error: Operator not allowed in strike values \"{declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}\": Line {self.line_ctr(self.c2)}")
                    elif self.GlobalDatatype[declared_id] == "chat":
                        if operator == "=":
                            if len(str(value)) != 1:
                                if inputter == 1:
                                    self.Output.append(
                                        f"|||Runtime Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                                else:
                                    self.Output.append(
                                        f"|||Semantic Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                            self.GlobalVar[declared_id][array_length] =  str(value)
                        elif operator in ["+=", "-=", "*=", "/=", "%="]:
                            self.Output.append(
                                f"|||Semantic Error: Operator not allowed in chat values \"{declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}\": Line {self.line_ctr(self.c2)}")
                    elif self.GlobalDatatype[declared_id] == "tool":
                        if str(value).replace('True', 'pos').replace('False', 'neg') not in ['pos', 'neg']:
                            if inputter == 1:
                                self.Output.append(
                                    f"|||Runtime Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                            else:
                                self.Output.append(
                                    f"|||Semantic Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                        if operator == "=":
                            self.GlobalVar[declared_id][array_length] = value
                        elif operator in ["+=", "-=", "*=", "/=", "%="]:
                            self.Output.append(
                                f"|||Semantic Error: Operator not allowed in tool values \"{declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}\": Line {self.line_ctr(self.c2)}")
                else:
                    self.Output.append(f"|||Semantic Error: Undeclared Variable in {declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}: Line {self.line_ctr(self.c2)}")

            elif idtype == "not array":
                # if id is not array then do this...
                for item in valuesequence:
                    if '<function call statement+>' in item:
                        function_call = 1
                    if '<input+>' in item:
                        inputter = 1
                if function_call == 1 and inputter != 1:
                    value = self.function_call_statement()
                elif inputter == 1 and function_call != 1:
                    value = "".join(self.value[start:end+1]).replace('"\\n"', '')
                    desc_display = value[4:-1]#.replace("info", "")
                    variables = [key for key in self.GlobalVar.keys() if key in desc_display]
                    for variable in variables:
                        desc_display = desc_display.replace(variable, str(self.GlobalVar[variable]))
                    try:
                        try:
                            desc_display = desc_display.replace("True", "pos").replace("False", "neg")
                            desc_display = eval(desc_display)
                        except:
                            desc_display = '\"' + str(desc_display).replace('"', '').replace("True", "pos").replace(
                                "False", "neg") + '\"'
                            desc_display = eval(desc_display)
                    except:
                        self.Output.append(f"|||Semantic Error: info parameter invalid \"{desc_display}\": Line {self.line_ctr(self.c2)}")
                    try:
                        value = eval(main.inputter(desc_display), None, self.tool)
                    except:
                        self.Output.append(f"|||Runtime Error: user input: Line {self.line_ctr(self.c2)}")
                    if self.GlobalDatatype[declared_id] == "inst" or self.GlobalDatatype[
                        declared_id] == "flank":
                        value2 = str(value).replace('-', '-')
                    else:
                        value2 = value
                    self.Output.append(f"{desc_display} {value2} \n")
                elif self.value[start] == self.value[end] and function_call != 1 and inputter != 1:
                    value = "".join(self.value[start])
                elif self.value[start] != self.value[end] and function_call != 1 and inputter != 1:
                    value = "".join(self.value[start:end]).replace('"\\n"', "").replace("-", "-")
                    variables = [key for key in self.GlobalVar.keys() if key in value]
                    for variable in variables:
                        value = value.replace(variable, str(self.GlobalVar[variable]))
                    value = eval(value , None, self.tool)
                #changing value from the declaration
                if declared_id in self.GlobalVar:
                    if self.GlobalDatatype[declared_id] == "flank":
                        if str(value).replace('True','pos').replace('False','neg') in ['pos', 'neg']:
                            if inputter == 1:
                                self.Output.append(
                                    f"|||Runtime Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                            else:
                                self.Output.append(
                                    f"|||Semantic Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                        elif operator == "=":
                            self.GlobalVar[declared_id] = float(value)
                        elif operator == "+=":
                            self.GlobalVar[declared_id] = self.GlobalVar[declared_id] + float(value)
                        elif operator == "-=":
                            self.GlobalVar[declared_id] = self.GlobalVar[declared_id] - float(value)
                        elif operator == "*=":
                            self.GlobalVar[declared_id] = self.GlobalVar[declared_id] * float(value)
                        elif operator == "/=":
                            self.GlobalVar[declared_id] = self.GlobalVar[declared_id] / float(value)
                        elif operator == "%=":
                            self.GlobalVar[declared_id] = self.GlobalVar[declared_id] % float(value)
                    elif self.GlobalDatatype[declared_id] == "inst":
                        if str(value).replace('True', 'pos').replace('False', 'neg') in ['pos', 'neg']:
                            if inputter == 1:
                                self.Output.append(
                                    f"|||Runtime Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                            else:
                                self.Output.append(
                                    f"|||Semantic Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                        elif operator == "=":
                            self.GlobalVar[declared_id] = int(value)
                        elif operator == "+=":
                            self.GlobalVar[declared_id] = self.GlobalVar[declared_id] + int(value)
                        elif operator == "-=":
                            self.GlobalVar[declared_id] = self.GlobalVar[declared_id] - int(value)
                        elif operator == "*=":
                            self.GlobalVar[declared_id] = self.GlobalVar[declared_id] * int(value)
                        elif operator == "/=":
                            self.GlobalVar[declared_id] = self.GlobalVar[declared_id] / int(value)
                        elif operator == "%=":
                            self.GlobalVar[declared_id] = self.GlobalVar[declared_id] % int(value)
                    elif self.GlobalDatatype[declared_id] == "strike":
                        if operator == "=":
                            self.GlobalVar[declared_id] = "\"" + str(value) + "\""
                        elif operator == "+=":
                            #aa = str(value)
                            aa = value
                            self.GlobalVar[declared_id] = self.GlobalVar[declared_id].replace("\"", "") + aa
                            self.GlobalVar[declared_id] = "\"" + self.GlobalVar[declared_id].replace("\"", "\'").replace("\n", "\\n") + "\""
                            if self.GlobalVar[declared_id].count("\'") > 2 and '+' not in self.GlobalVar[declared_id] and '-' not in \
                                    self.GlobalVar[declared_id] and '*' not in self.GlobalVar[declared_id] and '/' not in self.GlobalVar[declared_id] and '%' not in self.GlobalVar[declared_id]:
                                self.GlobalVar[declared_id] = self.GlobalVar[declared_id].replace("\"", "")
                        elif operator in ["-=", "*=", "/=", "%="]:
                            self.Output.append(
                                f"|||Semantic Error: Operator not allowed in strike values \"{declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}\": Line {self.line_ctr(self.c2)}")
                    elif self.GlobalDatatype[declared_id] == "chat":
                        if operator == "=":
                            if len(str(value)) != 1:
                                if inputter == 1:
                                    self.Output.append(
                                        f"|||Runtime Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                                else:
                                    self.Output.append(
                                        f"|||Semantic Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                            self.GlobalVar[declared_id] = str(value)
                        elif operator in ["+=", "-=", "*=", "/=", "%="]:
                            self.Output.append(
                                f"|||Semantic Error: Operator not allowed in chat values \"{declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}\": Line {self.line_ctr(self.c2)}")
                    elif self.GlobalDatatype[declared_id] == "tool":
                        if str(value).replace('True', 'pos').replace('False', 'neg') not in ['pos', 'neg']:
                            if inputter == 1:
                                self.Output.append(
                                    f"|||Runtime Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                            else:
                                self.Output.append(
                                    f"|||Semantic Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c2)}")
                        if operator == "=":
                            self.GlobalVar[declared_id] = value
                        elif operator in ["+=", "-=", "*=", "/=", "%="]:
                            self.Output.append(
                                f"|||Semantic Error: Operator not allowed in tool values \"{declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}\": Line {self.line_ctr(self.c2)}")
                else:
                    self.Output.append(
                        f"|||Semantic Error: Undeclared Variable in {declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}: Line {self.line_ctr(self.c2)}")
        except Exception as e:
            print(e)
            self.Output.append(f"|||Semantic Error: in initialization: Line {self.line_ctr(self.c2)}")

    def function_call_statement(self):
        try:
            self.FuncVariable = dict(self.GlobalVar)
            self.FuncVariableDatatype = dict(self.GlobalDatatype)
            if self.c1 == '<allowed value->' or self.c1 == '<initialization statement->': # getting the parameter in function call
                while self.c1 != '<allowed value+>':
                    self.prev()
                while self.c1 != '<allowed value->':
                    if self.c1 == '<id>':
                        var = self.value[self.c2]
                    elif self.c1 == '<parameter+>':
                        start = self.c2 + 1
                        while self.c1 != '<parameter->':
                            self.next()
                        end = self.c2
                        param1 = "".join([item for item in list(self.value[start:end])]).replace("-", "-")
                        param1 = [elem.strip() for elem in param1.split(',')]

                        try:
                            for i, elem in enumerate(param1):  # Use enumerate to access both the index and the element
                                if elem.startswith('#'):
                                    pass
                                else:
                                    param1[i] = str(
                                        eval(elem, None, self.tool))  # Evaluate the element and replace it in param1
                            param = param1
                        except:
                            param = []
                        while self.c1 != '<function call statement->':  # skipping to the end of function call
                            self.next()

                        if var in self.FunctionVarParam:  # declare the parameters in FunctionVarParam
                            if len(param) != len(self.FunctionVarParam[var]):
                                try:
                                    checker = eval(",".join(param))
                                    print(checker, "2@@")
                                    self.Output.append(
                                        f"|||Semantic Error: Length of parameter ({len(checker)}) not equal to function ({len(self.FunctionVarParam[var])}) in line {self.line_ctr(self.c2)}")
                                except Exception as e:
                                    a = str(e)
                                    print(a, "@#")
                                    b = a.replace('int', 'inst').replace('str', 'strike').replace('float', 'flank')
                                    error_list = ["unsupported operand type(s) for +: 'int' and 'str'",
                                                  'can only concatenate str (not "int") to str',
                                                  'can only concatenate str (not "float") to str',
                                                  "unsupported operand type(s) for +: 'float' and 'str'",
                                                  "'<' not supported between instances of 'int' and 'str'",
                                                  "'<' not supported between instances of 'float' and 'str'",
                                                  "'>=' not supported between instances of 'int' and 'str'",
                                                  "'>=' not supported between instances of 'float' and 'str'",
                                                  "'<=' not supported between instances of 'int' and 'str'",
                                                  "'<=' not supported between instances of 'float' and 'str'",
                                                  "'>' not supported between instances of 'int' and 'str'",
                                                  "'>' not supported between instances of 'float' and 'str'"]

                                    if a in error_list:
                                        self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c22)}")
                                    elif "unexpected EOF while parsing" in a:
                                        self.Output.append(
                                            f"|||Semantic Error: strike cannot be operated with other data types: Line {self.line_ctr(self.c2)}")
                                    elif "invalid syntax (<string>" in a:
                                        self.Output.append(
                                            f"|||Semantic Error: Invalid expression: Line {self.line_ctr(self.c22)}")
                                    elif "has no len()" in a:
                                        self.Output.append(
                                            f"|||Semantic Error: Length of parameter ({len(param)}) not equal to function ({len(self.FunctionVarParam[var])}) in line {self.line_ctr(self.c2)}")
                                    else:
                                        self.Output.append(
                                            f"|||Semantic Error: Undeclared Variable : Line {self.line_ctr(self.c22)}")

                                while self.c1 == '<allowed value->':
                                    self.next()
                                break
                            elif len(param) == 0 and len(self.FunctionVarParam[var]) == 0:
                                pass
                            else:
                                for idx, (subkey, _) in enumerate(self.FunctionVarParam[var].items()):
                                    if idx < len(param):
                                        self.FunctionVarParam[var][subkey] = param[idx]
                                if var in self.FunctionVarParam:
                                    for key, value in self.FunctionVarParam[var].items():
                                        variables = [key for key in self.FuncVariable.keys() if key in value]
                                        for variable in variables:
                                            value = value.replace(variable, str(self.FuncVariable[variable]))
                                        self.FuncVariable[key] = value
                                        if "#" in value and "\"" not in value:  # for function parameter that are id
                                            dtype = self.FuncVariableDatatype[value]
                                            self.FuncVariableDatatype.update({key: dtype})
                                        else:  # for function parameter that are inst, flank, strike, chat, tool
                                            pass
                                            if value == "neg" or value == "pos":
                                                self.FuncVariableDatatype.update({key: "tool"})
                                            elif "\'" in (value).replace("\"", "") and len((value).replace("\"", "")) == 3:
                                                self.FuncVariableDatatype.update({key: "chat"})
                                            else:
                                                try:
                                                    self.FuncVariableDatatype.update({key: "inst"})
                                                except:
                                                    try:
                                                        self.FuncVariableDatatype.update({key: "float"})
                                                    except:
                                                        self.FuncVariableDatatype.update({key: "strike"})

                            # start of function body
                            self.FuncSequence = self.Sequence[
                                                self.FuncVarSeq[var][0]:self.FuncVarSeq[var][1] + 1]
                            self.CurrentFuncSequence = self.FuncSequence[self.FuncPosition]
                            ckeys = list(self.CurrentFuncSequence.keys())
                            cvalues = list(self.CurrentFuncSequence.values())
                            self.c11 = ckeys[0]
                            self.c22 = cvalues[0]
                            # executing the function body
                            while self.c11 != '<function body->':  # and self.c11 != '<function body->':
                                if self.c11 == '<globe+>':
                                    self.func_globe()
                                elif self.c11 == '<declaration+>':
                                    self.func_declaration()
                                elif self.c11 == '<output statement+>':
                                    self.func_output()
                                elif self.c11 == '<function condition+>':
                                    a = self.func_condition_statement()
                                    if a != "None":
                                        result = a
                                        break
                                elif self.c11 in ['<function force loop+>', '<function watch loop+>']:
                                    a = self.func_loop()
                                    if a != "None":
                                        result = a
                                        break
                                elif self.c11 == '<initialization statement+>':
                                    self.func_initialization()  # punta sa self.func_initialization kasi need iadd sa self.FuncVar hindi sa globalvar unless globe
                                elif self.c11 == '<return+>':
                                    start_return = self.c22
                                    while self.c11 != '<return->':
                                        self.funcnext()
                                    end_return = self.c22 + 1
                                    back = "".join(self.value[start_return:end_return]).replace("back", "").replace(
                                        '"\\n"', '')
                                    variables = [key for key in self.FuncVariable.keys() if key in back]
                                    for variable in variables:
                                        if str(self.FuncVariable[variable]).startswith('#'):
                                            back = back.replace(variable,
                                                                  self.replace_variables(variable, self.FuncVariable))
                                        else:
                                            back = back.replace(variable, str(self.FuncVariable[variable]))
                                    if len(back) == 3 and back.count("(") == 1 and back.count(")") == 1:
                                        back = back.replace("(", "\"").replace(")", "\"")
                                    try:
                                        result = eval(back, None, self.tool)
                                    except:
                                        self.Output.append(f"|||Semantic Error: expression in \"back{back}\": Line {self.line_ctr(self.c22)}")
                                    break
                                self.funcnext()
                            while self.c11 != '<function body->':
                                self.funcnext()
                    self.next()
                # return to default self.FuncSequence
                self.FuncVariable = {}
                self.FuncVariableDatatype = {}
                self.FuncPosition = 0
                self.FuncSequence = []
                self.CurrentFuncSequence = None
                self.c11 = '\0'
                self.c22 = '\0'
                return result
            elif self.c1 == '<function call statement+>':
                while self.c1 != '<function call statement->':
                    if self.c1 == '<id>':
                        var = self.value[self.c2]
                    elif self.c1 == '<parameter+>':
                        start = self.c2 + 1
                        while self.c1 != '<parameter->':
                            self.next()
                        end = self.c2
                        param1 = "".join([item for item in list(self.value[start:end])]).replace("-", "-")
                        param1 = [elem.strip() for elem in param1.split(',')]
                        try:
                            for i, elem in enumerate(param1):  # Use enumerate to access both the index and the element
                                if elem.startswith('#'):
                                    pass
                                else:
                                    param1[i] = str(eval(elem, None, self.tool))  # Evaluate the element and replace it in param1
                            param = param1
                        except:
                            param = []
                        while self.c1 != '<function call statement->':  # skipping to the end of function call
                            self.next()
                        if var in self.FunctionVarParam: #declare the parameters in FunctionVarParam
                            if len(param) != len(self.FunctionVarParam[var]):
                                try:
                                    checker = eval(",".join(param))
                                    print(checker, "1@@")
                                    self.Output.append(
                                        f"|||Semantic Error: Length of parameter ({len(checker)}) not equal to function ({len(self.FunctionVarParam[var])}) in line {self.line_ctr(self.c2)}")
                                except Exception as e:
                                    a = str(e)
                                    print(a,"@#")
                                    b = a.replace('int', 'inst').replace('str', 'strike').replace('float', 'flank')
                                    error_list = ["unsupported operand type(s) for +: 'int' and 'str'",
                                                  'can only concatenate str (not "int") to str',
                                                  'can only concatenate str (not "float") to str',
                                                  "unsupported operand type(s) for +: 'float' and 'str'",
                                                  "'<' not supported between instances of 'int' and 'str'",
                                                  "'<' not supported between instances of 'float' and 'str'",
                                                  "'>=' not supported between instances of 'int' and 'str'",
                                                  "'>=' not supported between instances of 'float' and 'str'",
                                                  "'<=' not supported between instances of 'int' and 'str'",
                                                  "'<=' not supported between instances of 'float' and 'str'",
                                                  "'>' not supported between instances of 'int' and 'str'",
                                                  "'>' not supported between instances of 'float' and 'str'"]

                                    if a in error_list:
                                        self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c22)}")
                                    elif "unexpected EOF while parsing" in a:
                                        self.Output.append(f"|||Semantic Error: strike cannot be operated with other data types: Line {self.line_ctr(self.c2)}")
                                    elif "invalid syntax (<string>" in a:
                                        self.Output.append(
                                            f"|||Semantic Error: Invalid expression: Line {self.line_ctr(self.c22)}")
                                    elif "has no len()" in a:
                                        self.Output.append(
                                            f"|||Semantic Error: Length of parameter ({len(param)}) not equal to function ({len(self.FunctionVarParam[var])}) in line {self.line_ctr(self.c2)}")
                                    else:
                                        self.Output.append(
                                            f"|||Semantic Error: Undeclared Variable : Line {self.line_ctr(self.c22)}")
                                while self.c1 == '<allowed value->':
                                    self.next()
                                break
                            elif len(param) == 0 and len(self.FunctionVarParam[var]) == 0:
                                pass
                            else:
                                for idx, (subkey, _) in enumerate(self.FunctionVarParam[var].items()):
                                    if idx < len(param):
                                        self.FunctionVarParam[var][subkey] = param[idx]
                                if var in self.FunctionVarParam:
                                    for key, value in self.FunctionVarParam[var].items():
                                        variables = [key for key in self.FuncVariable.keys() if key in value]
                                        for variable in variables:
                                            value = value.replace(variable, str(self.FuncVariable[variable]))
                                        self.FuncVariable[key] = value
                                        if "#" in value and "\"" not in value: # for function parameter that are id
                                            dtype = self.FuncVariableDatatype[value]
                                            self.FuncVariableDatatype.update({key: dtype})
                                        else: #for function parameter that are inst, flank, strike, chat, tool
                                            pass
                                            if value == "neg" or value == "pos":
                                                self.FuncVariableDatatype.update({key: "tool"})
                                            elif "\'" in (value).replace("\"", "") and len((value).replace("\"", "")) == 3:
                                                self.FuncVariableDatatype.update({key: "chat"})
                                            else:
                                                try:
                                                    self.FuncVariableDatatype.update({key: "inst"})
                                                except:
                                                    try:
                                                        self.FuncVariableDatatype.update({key: "float"})
                                                    except:
                                                        self.FuncVariableDatatype.update({key: "strike"})
                            # start of function body
                            self.FuncSequence = self.Sequence[
                                                self.FuncVarSeq[var][0]:self.FuncVarSeq[var][1] + 1]
                            self.CurrentFuncSequence = self.FuncSequence[self.FuncPosition]
                            ckeys = list(self.CurrentFuncSequence.keys())
                            cvalues = list(self.CurrentFuncSequence.values())
                            self.c11 = ckeys[0]
                            self.c22 = cvalues[0]
                            # executing the function body
                            while self.c11 != '<function body->':  # and self.c11 != '<function body->':
                                if self.c11 == '<globe+>':
                                    self.func_globe()
                                elif self.c11 == '<declaration+>':
                                    self.func_declaration()
                                elif self.c11 == '<output statement+>':
                                    self.func_output()  # punta sa self.func_output kasi incase mag output ng nasa self.FuncVar
                                elif self.c11 == '<function condition+>':
                                    a = self.func_condition_statement()
                                    if a != "None":
                                        self.Output.append(f"|||Semantic Error: Return is not possible in non-void functions in Line {self.line_ctr(self.c22)}")
                                        break
                                elif self.c11 in ['<function force loop+>',
                                                  '<function watch loop+>']:
                                    a = self.func_loop()
                                    if a != "None":
                                        self.Output.append(f"|||Semantic Error: Return is not possible in non-void functions in Line {self.line_ctr(self.c22)}")
                                        break
                                elif self.c11 == '<initialization statement+>':
                                    self.func_initialization()  # punta sa self.func_initialization kasi need iadd sa self.FuncVar hindi sa globalvar unless globe
                                elif self.c11 == '<return+>':
                                    self.Output.append(
                                        f"|||Semantic Error: Return is not possible in non-void functions in Line {self.line_ctr(self.c22)}")
                                    break
                                self.funcnext()
                            while self.c11 != '<function body->':
                                self.funcnext()
                        else:
                            self.Output.append(f"|||Semantic Error: No function called : Line {self.line_ctr(self.c22)}")
                    if self.c1 == '<function call statement->':
                        break
                    if self.c1 == '\0':
                        break
                    self.next()
                # return to default self.FuncSequence
                self.FuncVariable = {}
                self.FuncVariableDatatype = {}
                self.FuncPosition = 0
                self.FuncSequence = []
                self.CurrentFuncSequence = None
                self.c11 = '\0'
                self.c22 = '\0'
        except:
            self.Output.append(f"|||Semantic Error: No function called: Line {self.line_ctr(self.c2)}")

    def funcnext(self):
        self.FuncPosition += 1
        if self.FuncPosition >= len(self.FuncSequence):  # Check if the end of the sequence is reached
            self.c11 = '\0'
            self.c22 = 0
        else:
            self.CurrentFuncSequence = self.FuncSequence[self.FuncPosition]
            ckeys = list(self.CurrentFuncSequence.keys())
            cvalues = list(self.CurrentFuncSequence.values())
            self.c11 = ckeys[0]
            self.c22 = cvalues[0]

    def funcprev(self):
        self.FuncPosition -= 1
        if self.FuncPosition < 0:  # Check if the end of the sequence is reached
            self.c11 = '\0'
            self.c22 = 0
        else:
            self.CurrentFuncSequence = self.FuncSequence[self.FuncPosition]
            ckeys = list(self.CurrentFuncSequence.keys())
            cvalues = list(self.CurrentFuncSequence.values())
            self.c11 = ckeys[0]
            self.c22 = cvalues[0]

    def func_output(self):
        try:
            output = ""
            while self.c11 != '<output statement->':
                if self.c11 == '<parameter+>':
                    output = self.func_output_parameter()  # Get the output from self.parameter
                if self.c11 == '\0':
                    break
                self.funcnext()
            self.Output.append(output)
        except:
            start = self.c22
            while self.c11 != '<output statement->':
                self.funcnext()
            end = self.c22
            plant = "".join(self.value[start:end])
            self.Output.append(f"|||Semantic Error: in {plant}: Line {self.line_ctr(self.c22)}")

    def func_output_parameter(self):
        try:
            start = self.c22 + 1
            end = 0
            while self.c11 != '<parameter->':  # Getting the parameter values
                self.funcnext()
            if '<parameter->' == self.c11:
                end = self.c22
            param_values = self.value[start:end]  # Storing the parameter values

            if param_values == []:  # if no parameter return Null string
                return ''
            param_str = "".join(param_values)  # make the parameter into string
            param_orig =param_str
            param_str = (self.replace_variables(param_str, self.FuncVariable)).replace("\n", "\\n")  # .replace("\'", "\"")
            if len(param_str) == 3 and param_str.count("\'") == 2:
                param_str = param_str.replace("\'", "\"")
            if '-' in param_str:  # make _ to - for negative numbers
                param_str = str(param_str.replace('-', '-'))
            param_str = self.replace_variables(param_str, self.FuncVariable)  # replace the id in param_str with value
            param_str = param_str.replace("\n", "\\n")
            try:
                try:
                    param_tuple = eval(param_str.replace("-", "-"), None, self.tool)  # Try to evaluate the param_str
                except:
                    printerr = []
                    parama = eval(param_str.replace("-","-"), None, self.tool)
                    for item in parama:
                        item = str(item)
                        try:
                            a = eval(item, None, self.tool)
                            printerr.append(str(a))
                        except:
                            if item.count('#') == 1:
                                self.Output.append(
                                    f"|||Semantic Error: Undeclared Variable: Line {self.line_ctr(self.c22)}")
                            try:
                                a = eval(item.replace("-","-"), None, self.tool)
                            except Exception as e:
                                a = str(e)
                                b = a.replace('int', 'inst').replace('str', 'strike').replace('float', 'flank')
                                if a == "unsupported operand type(s) for +: 'int' and 'str'":
                                    # self.Output.append(f"|||Semantic Error: parameter in \"plant({param_orig})\" {b}: Line {self.line_ctr(self.c2)}")
                                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c22)}")
                                elif a == 'can only concatenate str (not "int") to str' or a == 'can only concatenate str (not "float") to str':
                                    # self.Output.append(f"|||Semantic Error: parameter in plant({param_orig}) {b}: Line {self.line_ctr(self.c2)}")
                                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c22)}")
                                elif a == "unsupported operand type(s) for +: 'float' and 'str'":
                                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c22)}")
                                elif a == 'can only concatenate list (not "int") to list':
                                    self.Output.append(
                                        f"|||Semantic Error: Whole arrays cannot be used in math expressions: Line {self.line_ctr(self.c22)}")
                                elif "unmatched ']'" in a or "list index out of range" in a:
                                    self.Output.append(f"|||Semantic Error: Array Index range exceeded: Line {self.line_ctr(self.c22)}")
                                item = '\"' + item.replace('"', '') + '\"'
                                a = eval(item.replace("-","-"), None, self.tool)
                            printerr.append(str(a))
                        param_str = '\"' + "".join(printerr) + '\"'
                        param_tuple = eval(param_str.replace("\n", "\\n").replace("\t", "\\t"), None,
                                           self.tool)  # Try to evaluate the param_str
            except Exception as e:
                a = str(e)
                b = a.replace('int', 'inst').replace('str', 'strike').replace('float', 'flank')
                if a == "unsupported operand type(s) for +: 'int' and 'str'":
                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c22)}")
                elif a == 'can only concatenate str (not "int") to str' or a == 'can only concatenate str (not "float") to str':
                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c22)}")
                elif a == "unsupported operand type(s) for +: 'float' and 'str'":
                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c22)}")
                elif "unexpected EOF while parsing" in a:
                    self.Output.append(
                        f"|||Semantic Error: strike cannot be operated with other data types: Line {self.line_ctr(self.c22)}")
                elif "unmatched ']'" in a or "list index out of range" in a:
                    self.Output.append(f"|||Semantic Error: Array Index range exceeded: Line {self.line_ctr(self.c22)}")
                elif a == 'can only concatenate list (not "int") to list':
                    self.Output.append(f"|||Semantic Error: Whole arrays cannot be used in math expressions: Line {self.line_ctr(self.c22)}")
                else:
                    if param_str.count('#') >= 1:
                        self.Output.append(
                            f"|||Semantic Error: Undeclared Variable: Line {self.line_ctr(self.c22)}")
                    else:
                        param_str = '\"' + "".join(param_str).replace('"', '') + '\"'
                        param_tuple = eval(param_str.replace("\n", "\\n").replace("\t", "\\t"), None, self.tool)
            if isinstance(param_tuple, tuple):  # Check if param_tuple is a single item
                param_str = "".join(str(item) for item in param_tuple)
            else:
                param_str = str(param_tuple)  # if not tuple convert to string directly

            param_fixed = param_str.replace('True', 'pos').replace('False', 'neg').replace('-', '-')
            return param_fixed
        except Exception as e:
            print(e)
            a = str(e)
            if "unmatched ']'" in a or "list index out of range" in a:
                self.Output.append(f"|||Semantic Error: Array Index range exceeded: Line {self.line_ctr(self.c22)}")
            else:
                self.Output.append(f"|||Semantic Error: Undeclared Variable: Line {self.line_ctr(self.c22)}")

    def func_declaration(self):
        try:
            ctr = 0
            value = []
            valuetype = ""
            operator = ""
            datatype = ""
            declared_id = ""
            idtype = "not array"
            inputctr = 0
            # getting all the structure of declaration : <declaration> <id> <operator> <allowed value>
            while self.c11 != '<declaration->':
                if self.c11 == '<data type>' and ctr < 2:
                    datatype = self.value[self.c22]
                    ctr += 1
                elif self.c11 == '<id or array+>':
                    start = self.FuncPosition
                    self.funcnext()
                    while self.c11 != '<id or array->':
                        if self.c11 == '<id or array+>':
                            while self.c11 != '<id or array->':
                                self.funcnext()
                        self.funcnext()
                    end = self.FuncPosition + 1
                    id_sequence = self.FuncSequence[start:end]

                    if self.FuncSequence[start]['<id or array+>'] == self.FuncSequence[end - 1][
                        '<id or array->']:  # if sequence is only one
                        declared_id = self.value[self.FuncSequence[start]['<id or array+>']]
                    else:  # if sequence is many
                        declared_id = self.value[
                                      self.FuncSequence[start]['<id or array+>']:self.FuncSequence[end - 1]['<id or array->']]
                        declared_id.append(self.value[self.c22])
                        declared_id = "".join(declared_id).replace('"\\n"', "")
                elif self.c11 == '<assignment operator>':
                    operator = self.value[self.c22]
                elif self.c11 == '<allowed value+>':
                    start = self.FuncPosition
                    while self.c11 != '<allowed value->':
                        self.funcnext()
                    end = self.FuncPosition + 1
                    valuesequence = self.FuncSequence[start:end]
                    if self.FuncSequence[start]['<allowed value+>'] == self.FuncSequence[end - 1][
                        '<allowed value->']:  # if sequence is only one
                        value = self.value[self.FuncSequence[start]['<allowed value+>']]
                    else:  # if sequence is many
                        value = self.value[
                                self.FuncSequence[start]['<allowed value+>']: self.FuncSequence[end - 1]['<allowed value->']]
                        value.append(self.value[self.c22])
                        value = [item for item in value if item != '"\\n"']
                        value1 = "".join(value)

                    # check if id is array or not
                    if any('<index+>' in d for d in id_sequence):
                        idtype = "array"
                    else:
                        pass

                    if idtype == "array": #if id is array
                        valuetype = "array"
                        value1 = "".join(value)
                        variables = [key for key in self.FuncVariable.keys() if key in value1]
                        for variable in variables:
                            value1 = value1.replace(variable, str(self.FuncVariable[variable]))
                        try:
                            if datatype == "inst" or datatype == "flank":
                                value1 = eval(value1.replace("-", "-"), None, self.tool)
                            else:
                                value1 = eval(value1, None, self.tool)
                        except:
                            self.Output.append(f"|||Semantic Error: value \"{value1}\": Line {self.line_ctr(self.c22)}")
                        if type(value1) == list:
                            if datatype == "inst":
                                if all(isinstance(value, int) and not isinstance(value, bool) for value in value1):
                                    pass
                                else:
                                    self.Output.append(f"|||Semantic Error: Not all value in array are inst \"{''.join(value)}\": Line {self.line_ctr(self.c22)}")
                            elif datatype == "flank":
                                if all(isinstance(value, float) and not isinstance(value, bool) for value in value1):
                                    pass
                                else:
                                    self.Output.append(f"|||Semantic Error: Not all value in array are flank \"{''.join(value)}\": Line {self.line_ctr(self.c22)}")
                            elif datatype == "tool":
                                if all(isinstance(value, bool) for value in value1):
                                    pass
                                else:
                                    self.Output.append(f"|||Semantic Error: Not all value in array are tool \"{''.join(value)}\": Line {self.line_ctr(self.c22)}")
                            elif datatype == "chat":
                                if all(isinstance(value, str) and len(value) == 1 for value in value1):
                                    pass
                                else:
                                    self.Output.append(f"|||Semantic Error: Not all value in array are chat \"{''.join(value)}\": Line {self.line_ctr(self.c22)}")
                            elif datatype == "strike":
                                if all(isinstance(value, str) for value in value1):
                                    pass
                                else:
                                    self.Output.append(f"|||Semantic Error: Not all value in array are strike \"{''.join(value)}\": Line {self.line_ctr(self.c22)}")
                        start_index = declared_id.find('[')
                        end_index = declared_id.find(']')
                        array_length = declared_id[start_index + 1:end_index]
                        try:
                            array_length = int(self.replace_variables(array_length, self.FuncVariable)) #add try except here para if di sya int
                        except:
                            self.Output.append(f"|||Semantic Error: Index is not inst \"{array_length}\": Line {self.line_ctr(self.c22)}")
                        declared_id = declared_id.split('[')[0]
                        if array_length != len(value1): #try except para pag sa inst #a[3] = 23
                            self.Output.append(f"|||Semantic Error: Index ({array_length}) is not the same length as the value ({len(value1)}): Line {self.line_ctr(self.c22)}")
                        else:
                            if declared_id not in self.Funchatray:
                                self.Funchatray.append(declared_id)

                    elif idtype == "not array":
                        # if id is not array then do this...
                        if any('<input+>' in d for d in valuesequence):
                            valuetype = "input"
                        elif any('<id>' in d for d in valuesequence):  # if initialize an id
                            valuetype = "hasid"
                        elif any('<chatlit>' in d for d in valuesequence):  # if initialize chat
                            valuetype = "chat"
                        elif any('<tool value>' in d for d in valuesequence):  # if initialize a tool
                            valuetype = "tool"
                        elif any('<math expression+>' in d for d in valuesequence):  # if initialize a inst flank or strike
                            valuetype = "inst flank strike"
                self.funcnext()  # for while self.c1 != '<declaration->':

            # evaluating the value gathered
            if valuetype == "input":  # inst #a = info(....)
                inputctr = 1
                value = "".join(value).replace('"\\n"', '')
                desc_display = value[4:-1]#.replace("info", "")
                variables = [key for key in self.FuncVariable.keys() if key in desc_display]
                for variable in variables:
                    desc_display = desc_display.replace(variable, str(self.FuncVariable[variable]))
                try:
                    try:
                        desc_display = desc_display.replace("True", "pos").replace("False", "neg")
                        desc_display = eval(desc_display)
                    except:
                        desc_display = '\"' + str(desc_display).replace('"', '').replace("True", "pos").replace(
                            "False", "neg") + '\"'
                        desc_display = eval(desc_display)
                except:
                    self.Output.append(f"|||Semantic Error: expression in \"{desc_display}\": Line {self.line_ctr(self.c22)}")
                try:
                    value = eval(main.inputter(desc_display), None, self.tool)
                    if datatype == "strike"  or datatype == "chat":
                        value = str(value)
                except:
                    self.Output.append(f"|||Semantic Error: user input: Line {self.line_ctr(self.c22)}")
                valuetype = datatype
                if valuetype == "inst" or valuetype == "flank":
                    value2 = str(value).replace('-','-')
                else:
                    value2 = value
                self.Output.append(f"{desc_display} {value2} \n")

            elif valuetype != "" and valuetype != "hasid":  # inst #a and for evaluating array
                if len(value) > 1 and type(value) == list:
                    value1 = [item for item in value if item != '"\\n"']
                    value = "".join(value1)
                if '-' in value:
                    value = str(value.replace('-', '-'))
                try:
                    value = eval(value, None, self.tool)
                except:
                    value = "".join(value).replace('-', '-')
                    value = self.replace_variables(value, self.FuncVariable)
                    value = eval(str(value), None, self.tool)

            elif valuetype == "hasid" and datatype in ["inst", "flank", "tool"]:  # inst #a = #b
                if len(value) > 1 and type(value) == list:
                    value1 = [item for item in value if item != '"\\n"']
                    value = "".join(value1)
                if '-' in value:
                    value = str(value.replace('-', '-'))
                try:
                    valuestr = self.replace_variables(value, self.FuncVariable)
                    value = eval(valuestr, None, self.tool)
                except:
                    value = "".join(value)
                    valuestr = self.replace_variables(value, self.FuncVariable)
                    value = eval(valuestr, None, self.tool)
                if value == "True":
                    value = 'pos'
                elif value == "False":
                    value = 'neg'

            elif valuetype == "hasid" and datatype == "strike":  # strike #b = #a
                if len(value) > 1 and type(value) == list:
                    value1 = [item for item in value if item != '"\\n"']
                    value = "".join(value1)
                if '-' in value:
                    value = str(value.replace('-', '-'))
                valuestr = self.replace_variables(str(value), self.FuncVariable)
                value = eval(valuestr, None, self.tool)

            elif valuetype == "hasid" and datatype == "chat":  # chat #c = #d
                if len(value) > 1 and type(value) == list:
                    value1 = [item for item in value if item != '"\\n"']
                    value = "".join(value1)
                if '-' in value:
                    value = str(value.replace('-', '-'))
                valuestr = self.replace_variables(str(value), self.FuncVariable)
                value = eval(valuestr, None, self.tool)
                if value != 1:
                    self.Output.append(f"|||Semantic Error: Data type mismatch \"{datatype} {declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")

            # matching the datatype to value if not error.
            if datatype == "chat":
                if ((valuetype == datatype or valuetype == "hasid") and (repr(value).count("'") == 2 and (
                        len(repr(value)) == 3 or len(repr(value)) == 2))) or inputctr == 1:
                    if inputctr == 1 and len(str(value)) != 1:
                        self.Output.append(
                            f"|||Runtime Error: Data type mismatch \"{datatype} {declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                    self.FuncVariable.update({declared_id: f"\"{value}\""})
                    self.FuncVariableDatatype.update({declared_id: "chat"})
                elif valuetype == "array":
                    self.FuncVariable.update({declared_id: value})
                    self.FuncVariableDatatype.update({declared_id: "chat"})
                elif datatype != "" and operator == "" and value == []:
                    self.FuncVariable.update({declared_id: ""})
                    self.FuncVariableDatatype.update({declared_id: "chat"})
                else:
                    self.Output.append(f"|||Semantic Error: Data type mismatch \"{datatype} {declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}\": Line {self.line_ctr(self.c22)}")
            elif datatype == "tool":
                if type(value) == list:
                    value = ['pos' if item else 'neg' for item in value]
                if value == "True":
                    value = 'pos'
                elif value == "False":
                    value = 'neg'
                if (valuetype == datatype or valuetype == "hasid") and value in ['neg', 'pos']:
                    self.FuncVariable.update({declared_id: value})
                    self.FuncVariableDatatype.update({declared_id: "tool"})
                elif (valuetype == datatype or valuetype == "array"):
                    self.FuncVariable.update({declared_id: value})
                    self.FuncVariableDatatype.update({declared_id: "tool"})
                elif datatype != "" and operator == "" and value == []:
                    self.FuncVariable.update({declared_id: ""})
                    self.FuncVariableDatatype.update({declared_id: "tool"})
                else:
                    if inputctr == 1:
                        self.Output.append(
                            f"|||Runtime Error: Data type mismatch \"{datatype} {declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                    else:
                        self.Output.append(
                            f"|||Semantic Error: Data type mismatch \"{datatype} {declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
            elif datatype in ["inst", "flank", "strike"]:
                if datatype == "inst":
                    try:
                        if value - int(value) != 0:
                            if inputctr == 1:
                                self.Output.append(
                                    f"|||Runtime Error: Data type mismatch \"{datatype} {declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                            else:
                                self.Output.append(
                                    f"|||Semantic Error: Data type mismatch \"{datatype} {declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                        else:
                                value = int(value)
                    except:
                        pass
                math_type = type(value)
                if math_type == int == type(value) and datatype == "inst" or (
                        datatype == "inst" and valuetype == "hasid") or (valuetype == "array" and datatype == "inst"):
                    self.FuncVariable.update({declared_id: value})
                    self.FuncVariableDatatype.update({declared_id: "inst"})
                elif math_type == float == type(value) and datatype == "flank" or (
                        datatype == "flank" and valuetype == "hasid") or (valuetype == "array" and datatype == "flank"):
                    self.FuncVariable.update({declared_id: value})
                    self.FuncVariableDatatype.update({declared_id: "flank"})
                elif math_type == str == type(value) and datatype == "strike" or (
                        datatype == "strike" and valuetype == "hasid"):
                    self.FuncVariable.update({declared_id: f'\"{value}\"'})
                    self.FuncVariableDatatype.update({declared_id: "strike"})
                elif valuetype == "array" and datatype == "strike":
                    self.FuncVariable.update({declared_id: value})
                    self.FuncVariableDatatype.update({declared_id: "strike"})
                elif datatype != "" and operator == "" and value == []:
                    self.FuncVariable.update({declared_id: value})
                    self.FuncVariableDatatype.update({declared_id: datatype})
                else:
                    if inputctr == 1:
                        self.Output.append(
                            f"|||Runtime Error: Data type mismatch \"{datatype} {declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                    else:
                        self.Output.append(
                            f"|||Semantic Error: Data type mismatch \"{datatype} {declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
        except:
            self.Output.append(f"|||Semantic Error in function declaration: Line {self.line_ctr(self.c22)}")

    def func_initialization(self):
        try:
            function_call = 0
            inputter = 0
            value = None
            idtype = "not array"
            # getting all the structure of initialization : <id> <operator> <allowed value>
            while '<initialization statement->' != self.c11:
                if self.c11 == '<id or array+>':
                    start = self.FuncPosition
                    self.funcnext()
                    while self.c11 != '<id or array->':
                        if self.c11 == '<id or array+>':
                            while self.c11 != '<id or array->':
                                self.funcnext()
                        self.funcnext()
                    end = self.FuncPosition + 1
                    id_sequence = self.FuncSequence[start:end]
                    if self.FuncSequence[start]['<id or array+>'] == self.FuncSequence[end - 1][
                        '<id or array->']:  # if sequence is only one
                        declared_id = self.value[self.FuncSequence[start]['<id or array+>']]
                    else:  # if sequence is many
                        declared_id = self.value[
                                      self.FuncSequence[start]['<id or array+>']:self.FuncSequence[end - 1]['<id or array->']]
                        declared_id.append(self.value[self.c22])
                        declared_id = "".join(declared_id)
                elif self.c11 == '<assignment operator>':
                    operator = self.value[self.c22]
                elif self.c11 == '<allowed value+>':
                    start1 = self.FuncPosition
                    start = self.c22
                    while self.c11 != '<allowed value->':
                        self.funcnext()
                    end1 = self.FuncPosition + 1
                    end = self.c22
                    valuesequence = self.FuncSequence[start1:end1]
                    if self.FuncSequence[start1]['<allowed value+>'] == self.FuncSequence[end1 - 1][
                        '<allowed value->']:  # if sequence is only one
                        value = self.value[self.FuncSequence[start1]['<allowed value+>']]
                    else:  # if sequence is many
                        value = self.value[
                                self.FuncSequence[start1]['<allowed value+>']: self.FuncSequence[end1 - 1]['<allowed value->']]
                        value.append(self.value[self.c22])
                        value = [item for item in value if item != '"\\n"']
                        value1 = "".join(value)

                # check if id is array or not
                    if any('<index+>' in d for d in id_sequence):
                        idtype = "array"
                    else:
                        pass
                self.funcnext()  # for while self.c1 != '<declaration->':

            if idtype == "array":  # add later
                for item in valuesequence:
                    if '<function call statement+>' in item:
                        function_call = 1
                    if '<input+>' in item:
                        inputter = 1
                if function_call == 1 and inputter != 1:
                    self.Output.append(f"|||Semantic Error: function call is not allowed inside functions: Line {self.line_ctr(self.c22)}")
                elif inputter == 1 and function_call != 1:
                    value = "".join(self.value[start:end + 1]).replace('"\\n"', '')
                    desc_display = value[4:-1]#.replace("info", "")
                    variables = [key for key in self.FuncVariable.keys() if key in desc_display]
                    for variable in variables:
                        desc_display = desc_display.replace(variable, str(self.FuncVariable[variable]))
                    try:
                        desc_display = eval(desc_display)
                    except:
                        self.Output.append(f"|||Semantic Error: expression in \"{desc_display}\": Line {self.line_ctr(self.c22)}")
                    try:
                        value = eval(main.inputter(desc_display), None, self.tool)
                    except:
                        self.Output.append(f"|||Runtime Error: user input: Line {self.line_ctr(self.c22)}")
                    if self.FuncVariableDatatype[declared_id[:declared_id.find('[')]] == "inst" or self.FuncVariableDatatype[
                        declared_id[:declared_id.find('[')]] == "flank":
                        value2 = str(value).replace('-', '-')
                    else:
                        value2 = value
                    self.Output.append(f"{desc_display} {value2} \n")
                elif self.value[start] == self.value[end] and function_call != 1 and inputter != 1:
                    value = "".join(self.value[start])
                elif self.value[start] != self.value[end] and function_call != 1 and inputter != 1:
                    value = "".join(self.value[start:end]).replace('"\\n"', "").replace("-", "-")
                    variables = [key for key in self.FuncVariable.keys() if key in value]
                    for variable in variables:
                        value = value.replace(variable, str(self.FuncVariable[variable]))
                    value = eval(value, None, self.tool)

                if str(value) == "True":
                    value = "pos"
                elif str(value) == "False":
                    value = "neg"
                if declared_id.count('[') == 2 and declared_id.count(']') == 2:
                    self.Output.append(f"|||Semantic Error: Array as index is not allowed: Line {self.line_ctr(self.c22)}")
                else:
                    start_index = declared_id.find('[')
                    end_index = declared_id.find(']')
                    array_length = declared_id[start_index + 1:end_index]
                try:
                    array_length = int(
                        self.replace_variables(array_length,
                                               self.FuncVariable))  # add try except here para if di sya int
                except:
                    self.Output.append(f"|||Semantic Error: Index is not inst \"{array_length}\": Line {self.line_ctr(self.c22)}")
                declared_id = declared_id.split('[')[0]
                if declared_id in self.FuncVariable and declared_id in self.Funchatray:
                    if self.FuncVariableDatatype[declared_id] == "flank":
                        if str(value).replace('True', 'pos').replace('False', 'neg') in ['pos', 'neg']:
                            if inputter == 1:
                                self.Output.append(
                                    f"|||Runtime Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                            else:
                                self.Output.append(
                                    f"|||Semantic Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                        elif operator == "=":
                            self.FuncVariable[declared_id][array_length] = float(value)
                        elif operator == "+=":
                            self.FuncVariable[declared_id][array_length] = self.FuncVariable[declared_id][
                                                                            array_length] + float(value)
                        elif operator == "-=":
                            self.FuncVariable[declared_id][array_length] = self.FuncVariable[declared_id][
                                                                            array_length] - float(value)
                        elif operator == "*=":
                            self.FuncVariable[declared_id][array_length] = self.FuncVariable[declared_id][
                                                                            array_length] * float(value)
                        elif operator == "/=":
                            self.FuncVariable[declared_id][array_length] = self.FuncVariable[declared_id][
                                                                            array_length] / float(value)
                        elif operator == "%=":
                            self.FuncVariable[declared_id][array_length] = self.FuncVariable[declared_id][
                                                                            array_length] % float(value)
                    elif self.FuncVariableDatatype[declared_id] == "inst":
                        if str(value).replace('True', 'pos').replace('False', 'neg') in ['pos', 'neg']:
                            if inputter == 1:
                                self.Output.append(
                                    f"|||Runtime Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                            else:
                                self.Output.append(
                                    f"|||Semantic Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                        elif operator == "=":
                            self.FuncVariable[declared_id][array_length] = int(value)
                        elif operator == "+=":
                            self.FuncVariable[declared_id][array_length] = self.FuncVariable[declared_id][
                                                                            array_length] + int(value)
                        elif operator == "-=":
                            self.FuncVariable[declared_id][array_length] = self.FuncVariable[declared_id][
                                                                            array_length] - int(value)
                        elif operator == "*=":
                            self.FuncVariable[declared_id][array_length] = self.FuncVariable[declared_id][
                                                                            array_length] * int(value)
                        elif operator == "/=":
                            self.FuncVariable[declared_id][array_length] = self.FuncVariable[declared_id][
                                                                            array_length] / int(value)
                        elif operator == "%=":
                            self.FuncVariable[declared_id][array_length] = self.FuncVariable[declared_id][
                                                                            array_length] % int(value)
                    elif self.FuncVariableDatatype[declared_id] == "strike":
                        if operator == "=":
                            self.FuncVariable[declared_id][array_length] = str(value)
                        elif operator == "+=":
                            # aa = str(value)
                            aa = value
                            self.FuncVariable[declared_id][array_length] = self.FuncVariable[declared_id][
                                                                            array_length].replace("\"", "") + aa
                            self.FuncVariable[declared_id][array_length] = "\"" + self.FuncVariable[declared_id][
                                array_length].replace("\"", "").replace("\n",
                                                                        "\\n") + "\""
                            if self.FuncVariable[declared_id][array_length].count("\'") > 2 and '+' not in \
                                    self.FuncVariable[declared_id][array_length] and '-' not in \
                                    self.FuncVariable[declared_id][array_length] and '*' not in \
                                    self.FuncVariable[declared_id][array_length] and '/' not in self.FuncVariable[
                                declared_id] and '%' not in self.FuncVariable[declared_id][array_length]:
                                self.FuncVariable[declared_id][array_length] = self.FuncVariable[declared_id][
                                    array_length].replace("\"", "")
                        elif operator in ["-=", "*=", "/=", "%="]:
                            self.Output.append(
                                f"|||Semantic Error: Operator not allowed in strike values \"{declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}\": Line {self.line_ctr(self.c22)}")
                    elif self.FuncVariableDatatype[declared_id] == "chat":
                        if operator == "=":
                            if len(str(value)) != 1:
                                if inputter == 1:
                                    self.Output.append(
                                        f"|||Runtime Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                                else:
                                    self.Output.append(
                                        f"|||Semantic Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                            self.FuncVariable[declared_id][array_length] = str(value)
                        elif operator in ["+=", "-=", "*=", "/=", "%="]:
                            self.Output.append(
                                f"|||Semantic Error: Operator not allowed in chat values \"{declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}\": Line {self.line_ctr(self.c22)}")
                    elif self.FuncVariableDatatype[declared_id] == "tool":
                        if str(value).replace('True', 'pos').replace('False', 'neg') not in ['pos', 'neg']:
                            if inputter == 1:
                                self.Output.append(
                                    f"|||Runtime Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                            else:
                                self.Output.append(
                                    f"|||Semantic Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                        if operator == "=":
                            self.FuncVariable[declared_id][array_length] = value
                        elif operator in ["+=", "-=", "*=", "/=", "%="]:
                            self.Output.append(f"|||Semantic Error: Operator not allowed in tool values \"{declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}\": Line {self.line_ctr(self.c2)}")
                else:
                    self.Output.append(f"|||Semantic Error: Undeclared Variable in {declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}: Line {self.line_ctr(self.c22)}")

            elif idtype == "not array":
                # if id is not array then do this...
                for item in valuesequence:
                    if '<function call statement+>' in item:
                        function_call = 1
                    if '<input+>' in item:
                        inputter = 1
                if function_call == 1 and inputter != 1:
                    self.Output.append(f"|||Semantic Error: function call is not allowed inside functions: Line {self.line_ctr(self.c22)}")
                elif inputter == 1 and function_call != 1:
                    value = "".join(self.value[start:end+1]).replace('"\\n"', '')
                    desc_display = value[4:-1]#.replace("info", "")
                    variables = [key for key in self.FuncVariable.keys() if key in desc_display]
                    for variable in variables:
                        desc_display = desc_display.replace(variable, str(self.FuncVariable[variable]))
                    try:
                        try:
                            desc_display = desc_display.replace("True", "pos").replace("False", "neg")
                            desc_display = eval(desc_display)
                        except:
                            desc_display = '\"' + str(desc_display).replace('"', '').replace("True", "pos").replace(
                                "False", "neg") + '\"'
                            desc_display = eval(desc_display)
                    except:
                        self.Output.append(f"|||Semantic Error: info parameter invalid \"{desc_display}\": Line {self.line_ctr(self.c22)}")
                    try:
                        value = eval(main.inputter(desc_display), None, self.tool)
                    except:
                        self.Output.append(f"|||Runtime Error: user input: Line {self.line_ctr(self.c22)}")
                    if self.FuncVariableDatatype[declared_id] == "inst" or self.FuncVariableDatatype[
                        declared_id] == "flank":
                        value2 = str(value).replace('-', '-')
                    else:
                        value2 = value
                    self.Output.append(f"{desc_display} {value2} \n")
                elif self.value[start] == self.value[end] and function_call != 1 and inputter != 1:
                    value = "".join(self.value[start])
                elif self.value[start] != self.value[end] and function_call != 1 and inputter != 1:
                    value = "".join(self.value[start:end]).replace('"\\n"', "").replace("-", "-")
                    variables = [key for key in self.FuncVariable.keys() if key in value]
                    for variable in variables:
                        value = value.replace(variable, str(self.FuncVariable[variable]))
                    value = eval(value , None, self.tool)

                #changing value from the declaration
                if declared_id in self.FuncVariable:
                    if self.FuncVariableDatatype[declared_id] == "flank":
                        if str(value).replace('True','pos').replace('False','neg') in ['pos', 'neg']:
                            if inputter == 1:
                                self.Output.append(
                                    f"|||Runtime Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                            else:
                                self.Output.append(
                                    f"|||Semantic Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                        elif operator == "=":
                            self.FuncVariable[declared_id] = float(value)
                        elif operator == "+=":
                            self.FuncVariable[declared_id] = self.FuncVariable[declared_id] + float(value)
                        elif operator == "-=":
                            self.FuncVariable[declared_id] = self.FuncVariable[declared_id] - float(value)
                        elif operator == "*=":
                            self.FuncVariable[declared_id] = self.FuncVariable[declared_id] * float(value)
                        elif operator == "/=":
                            self.FuncVariable[declared_id] = self.FuncVariable[declared_id] / float(value)
                        elif operator == "%=":
                            self.FuncVariable[declared_id] = self.FuncVariable[declared_id] % float(value)
                    elif self.FuncVariableDatatype[declared_id] == "inst":
                        if str(value).replace('True', 'pos').replace('False', 'neg') in ['pos', 'neg']:
                            if inputter == 1:
                                self.Output.append(
                                    f"|||Runtime Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                            else:
                                self.Output.append(
                                    f"|||Semantic Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                        elif operator == "=":
                            self.FuncVariable[declared_id] = int(value)
                        elif operator == "+=":
                            self.FuncVariable[declared_id] = self.FuncVariable[declared_id] + int(value)
                        elif operator == "-=":
                            self.FuncVariable[declared_id] = self.FuncVariable[declared_id] - int(value)
                        elif operator == "*=":
                            self.FuncVariable[declared_id] = self.FuncVariable[declared_id] * int(value)
                        elif operator == "/=":
                            self.FuncVariable[declared_id] = self.FuncVariable[declared_id] / int(value)
                        elif operator == "%=":
                            self.FuncVariable[declared_id] = self.FuncVariable[declared_id] % int(value)
                    elif self.FuncVariableDatatype[declared_id] == "strike":
                        if operator == "=":
                            self.FuncVariable[declared_id] = "\"" + str(value) + "\""
                        elif operator == "+=":
                            # aa = str(value)
                            aa = value
                            self.FuncVariable[declared_id] = self.FuncVariable[declared_id].replace("\"", "") + aa
                            self.FuncVariable[declared_id] = "\"" + self.FuncVariable[declared_id].replace("\"", "\'").replace("\n", "\\n") + "\""
                            if self.FuncVariable[declared_id].count("\'") > 2 and '+' not in self.FuncVariable[declared_id] and '-' not in \
                                    self.FuncVariable[declared_id] and '*' not in self.FuncVariable[declared_id] and '/' not in self.FuncVariable[declared_id] and '%' not in self.FuncVariable[declared_id]:
                                self.FuncVariable[declared_id] = self.FuncVariable[declared_id].replace("\"", "")
                        elif operator in ["-=", "*=", "/=", "%="]:
                            self.Output.append(
                                f"|||Semantic Error: Operator not allowed in strike values \"{declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}\": Line {self.line_ctr(self.c22)}")
                    elif self.FuncVariableDatatype[declared_id] == "chat":
                        if operator == "=":
                            if len(str(value)) != 1:
                                if inputter == 1:
                                    self.Output.append(
                                        f"|||Runtime Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                                else:
                                    self.Output.append(
                                        f"|||Semantic Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                            self.FuncVariable[declared_id] = str(value)
                        elif operator in ["+=", "-=", "*=", "/=", "%="]:
                            self.Output.append(
                                f"|||Semantic Error: Operator not allowed in chat values \"{declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}\": Line {self.line_ctr(self.c22)}")
                    elif self.FuncVariableDatatype[declared_id] == "tool":
                        if str(value).replace('True', 'pos').replace('False', 'neg') not in ['pos', 'neg']:
                            if inputter == 1:
                                self.Output.append(
                                    f"|||Runtime Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                            else:
                                self.Output.append(
                                    f"|||Semantic Error: Data type mismatch \"{declared_id} {operator} {str(value).replace('True', 'pos').replace('False', 'neg')}\": Line {self.line_ctr(self.c22)}")
                        if operator == "=":
                            self.FuncVariable[declared_id] = value
                        elif operator in ["+=", "-=", "*=", "/=", "%="]:
                            self.Output.append(
                                f"|||Semantic Error: Operator not allowed in tool values \"{declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}\": Line {self.line_ctr(self.c22)}")
                else:
                    self.Output.append(
                        f"|||Semantic Error: Undeclared Variable in {declared_id} {operator} {str(value).replace('True','pos').replace('False','neg')}: Line {self.line_ctr(self.c22)}")

            if declared_id in self.UnivVar:
                self.GlobalVar[declared_id] = self.FuncVariable[declared_id]
        except:
            self.Output.append(f"|||Semantic Error: in function initialization: Line {self.line_ctr(self.c22)}")

    def func_loop(self):
        try:
            back = "None"
            a = "None"
            if self.c11 == '<function force loop+>':  # if loop statement is a for loop then go here
                self.funcnext()
                id1 = str(self.value[self.c22])  # later
                id = {id1: 0}  
                self.FuncVariable.update(id)
                self.FuncVariableDatatype.update({id1: "inst"})
                self.funcnext()
                start = self.c22 + 1  
                while self.c11 != '<perim->':
                    self.funcnext()
                end = self.c22
                h1 = "".join(self.value[start:end]).replace("(", '').replace("-", "-")
                self.funcnext()
                startpos_loop = self.FuncPosition  # this is the variable in which they will go
                h1 = self.replace_variables(h1, self.FuncVariable)  # replace the id in param_str with value
                h1 = h1.replace("\n", "\\n")
                try:
                    result = eval(h1, None, self.tool)  # it will return the range parameter, either 1 or tuple
                except:
                    self.Output.append(f"|||Semantic Error: range parameter \"range({h1})\": Line {self.line_ctr(self.c22)}")

                if isinstance(result, int):  # Checking if the result is an integer
                    if result <= 0:
                        while self.c11 != '<function force loop->':
                            self.funcnext()
                    else:
                        for _ in range(result):
                            if self.c11 == '<function force loop->':
                                break
                            if _ > 0:  # it will go to startpos_loop after the 2nd iteration of the loop
                                id = {id1: _}
                                self.FuncVariable.update(id)
                                self.FuncVariableDatatype.update({id1: "inst"})
                                self.FuncPosition = startpos_loop
                                self.CurrentFuncSequence = self.FuncSequence[self.FuncPosition]
                                ckeys = list(self.CurrentFuncSequence.keys())
                                cvalues = list(self.CurrentFuncSequence.values())
                                self.c11 = ckeys[0]
                                self.c22 = cvalues[0]

                            while self.c11 != '<function force loop->':  # execute the force loop body
                                if self.c11 == '<output statement+>':
                                    self.func_output()
                                elif self.c11 == '<function loop condition+>':
                                    a = self.func_loop_condition()
                                    if a == "__STOP__":
                                        while self.c11 != '<function loop body->':
                                            self.funcnext()
                                        break
                                    elif a != "None" and a != "__STOP__":
                                        back = a
                                        while self.c11 != '<function loop body->':
                                            self.funcnext()
                                        break
                                elif self.c11 in ['<function force loop+>', '<function watch loop+>']:
                                    a = self.func_loop()
                                    if a == "__STOP__":
                                        while self.c11 != '<function loop body->':
                                            self.funcnext()
                                        break
                                    elif a != "None" and a != "__STOP__":
                                        back = a
                                        while self.c11 != '<function loop body->':
                                            self.funcnext()
                                        break
                                elif self.c11 == '<initialization statement+>':
                                    self.func_initialization()
                                elif self.c11 == '<pass>':
                                    pass
                                elif self.c11 == '<continue>':
                                    continue
                                elif self.c11 == '<break>':
                                    while self.c11 != '<function loop body->':
                                        self.funcnext()
                                    break
                                elif self.c11 == '<function call+>':
                                    pass
                                elif self.c11 == '<return+>':
                                    start_return = self.c22
                                    while self.c11 != '<return->':
                                        self.funcnext()
                                    end_return = self.c22 + 1
                                    back = "".join(self.value[start_return:end_return]).replace("back", "").replace(
                                        '"\\n"', '')
                                    variables = [key for key in self.FuncVariable.keys() if key in back]
                                    for variable in variables:
                                        back = back.replace(variable, str(self.FuncVariable[variable]))
                                    try:
                                        back = eval(back, None, self.tool)
                                    except:
                                        self.Output.append(
                                            f"|||Semantic Error: expression in \"back{back}\": Line {self.line_ctr(self.c22)}")
                                    while self.c11 != '<function loop body->':
                                        self.funcnext()
                                    break
                                self.funcnext()
                            self.funcnext()
                        self.funcprev()
                else:  # Checking the length of the result tuple
                    if len(result) == 1:
                        stop = result[0]
                        if stop <= 0:
                            while self.c11 != '<function force loop->':
                                self.funcnext()
                        else:
                            for _ in range(stop):
                                if self.c11 == '<function force loop->':
                                    break
                                if _ > 0:
                                    id = {id1: _}
                                    self.FuncVariable.update(id)
                                    self.FuncVariableDatatype.update({id1: "inst"})
                                    self.FuncPosition = startpos_loop
                                    self.CurrentFuncSequence = self.FuncSequence[self.FuncPosition]
                                    ckeys = list(self.CurrentFuncSequence.keys())
                                    cvalues = list(self.CurrentFuncSequence.values())
                                    self.c11 = ckeys[0]
                                    self.c22 = cvalues[0]

                                while self.c11 != '<function force loop->':  # execute the force loop body
                                    if self.c11 == '<output statement+>':
                                        self.func_output()
                                    elif self.c11 == '<function loop condition+>':
                                        a = self.func_loop_condition()
                                        if a == "__STOP__":
                                            while self.c11 != '<function loop body->':
                                                self.funcnext()
                                            break
                                        elif a != "None" and a != "__STOP__":
                                            back = a
                                            while self.c11 != '<function loop body->':
                                                self.funcnext()
                                            break
                                    elif self.c11 in ['<function force loop+>', '<function watch loop+>']:
                                        a = self.func_loop()
                                        if a == "__STOP__":
                                            while self.c11 != '<function loop body->':
                                                self.funcnext()
                                            break
                                        elif a != "None" and a != "__STOP__":
                                            back = a
                                            while self.c11 != '<function loop body->':
                                                self.funcnext()
                                            break
                                    elif self.c11 == '<initialization statement+>':
                                        self.func_initialization()
                                    elif self.c11 == '<pass>':
                                        pass
                                    elif self.c11 == '<continue>':
                                        continue
                                    elif self.c11 == '<break>':
                                        while self.c11 != '<function loop body->':
                                            self.funcnext()
                                        break
                                    elif self.c11 == '<function call+>':
                                        pass
                                    elif self.c11 == '<return+>':
                                        start_return = self.c22
                                        while self.c11 != '<return->':
                                            self.funcnext()
                                        end_return = self.c22 + 1
                                        back = "".join(self.value[start_return:end_return]).replace("back", "").replace(
                                            '"\\n"', '')
                                        variables = [key for key in self.FuncVariable.keys() if key in back]
                                        for variable in variables:
                                            back = back.replace(variable, str(self.FuncVariable[variable]))
                                        try:
                                            back = eval(back, None, self.tool)
                                        except:
                                            self.Output.append(
                                                f"|||Semantic Error: expression in \"back{back}\": Line {self.line_ctr(self.c22)}")
                                        while self.c11 != '<function loop body->':
                                            self.funcnext()
                                        break
                                    self.funcnext()
                                self.funcnext()
                            self.funcprev()
                    elif len(result) == 2:
                        start, stop = result
                        self.FuncVariable[id1] = start
                        if start >= stop:
                            while self.c11 != '<function force loop->':
                                self.funcnext()
                        else:
                            for _ in range(start, stop):
                                if self.c11 == '<function force loop->':
                                    break
                                if _ > start:
                                    id = {id1: self.FuncVariable[id1] + 1}
                                    self.FuncVariable.update(id)
                                    self.FuncVariableDatatype.update({id1: "inst"})
                                    self.FuncPosition = startpos_loop
                                    self.CurrentFuncSequence = self.FuncSequence[self.FuncPosition]
                                    ckeys = list(self.CurrentFuncSequence.keys())
                                    cvalues = list(self.CurrentFuncSequence.values())
                                    self.c11 = ckeys[0]
                                    self.c22 = cvalues[0]

                                while self.c11 != '<function force loop->':  # execute the force loop body
                                    if self.c11 == '<output statement+>':
                                        self.func_output()
                                    elif self.c11 == '<function loop condition+>':
                                        a = self.func_loop_condition()
                                        if a == "__STOP__":
                                            while self.c11 != '<function loop body->':
                                                self.funcnext()
                                            break
                                        elif a != "None" and a != "__STOP__":
                                            back = a
                                            while self.c11 != '<function loop body->':
                                                self.funcnext()
                                            break
                                    elif self.c11 in ['<function force loop+>', '<function watch loop+>']:
                                        a = self.func_loop()
                                        if a == "__STOP__":
                                            while self.c11 != '<function loop body->':
                                                self.funcnext()
                                            break
                                        elif a != "None" and a != "__STOP__":
                                            back = a
                                            while self.c11 != '<function loop body->':
                                                self.funcnext()
                                            break
                                    elif self.c11 == '<initialization statement+>':
                                        self.func_initialization()
                                    elif self.c11 == '<pass>':
                                        pass
                                    elif self.c11 == '<continue>':
                                        continue
                                    elif self.c11 == '<break>':
                                        while self.c11 != '<function loop body->':
                                            self.funcnext()
                                        break
                                    elif self.c11 == '<function call+>':
                                        pass
                                    elif self.c11 == '<return+>':
                                        start_return = self.c22
                                        while self.c11 != '<return->':
                                            self.funcnext()
                                        end_return = self.c22 + 1
                                        back = "".join(self.value[start_return:end_return]).replace("back", "").replace(
                                            '"\\n"', '')
                                        variables = [key for key in self.FuncVariable.keys() if key in back]
                                        for variable in variables:
                                            back = back.replace(variable, str(self.FuncVariable[variable]))
                                        try:
                                            back = eval(back, None, self.tool)
                                        except:
                                            self.Output.append(
                                                f"|||Semantic Error: expression in \"back{back}\": Line {self.line_ctr(self.c22)}")
                                        while self.c11 != '<function loop body->':
                                            self.funcnext()
                                        break
                                    self.funcnext()
                                self.funcnext()
                            self.funcprev()
                    elif len(result) == 3:
                        start, stop, step = result
                        self.FuncVariable[id1] = start
                        if step == 0:
                            self.Output.append(f"|||Semantic Error: Increment should not be {step}: Line {self.line_ctr(self.c22)}")
                        elif start < stop and step > 0:
                            for _ in range(start, stop, step):
                                if self.c11 == '<function force loop->':
                                    break
                                print(_, self.FuncVariable[id1])
                                if _ > start:
                                    id = {id1: self.FuncVariable[id1] + step}
                                    self.FuncVariable.update(id)
                                    self.FuncVariableDatatype.update({id1: "inst"})
                                    self.FuncPosition = startpos_loop
                                    self.CurrentFuncSequence = self.FuncSequence[self.FuncPosition]
                                    ckeys = list(self.CurrentFuncSequence.keys())
                                    cvalues = list(self.CurrentFuncSequence.values())
                                    self.c11 = ckeys[0]
                                    self.c22 = cvalues[0]

                                while self.c11 != '<function force loop->':  # execute the force loop body
                                    if self.c11 == '<output statement+>':
                                        self.func_output()
                                    elif self.c11 == '<function loop condition+>':
                                        a = self.func_loop_condition()
                                        if a == "__STOP__":
                                            while self.c11 != '<function loop body->':
                                                self.funcnext()
                                            break
                                        elif a != "None" and a != "__STOP__":
                                            back = a
                                            while self.c11 != '<function loop body->':
                                                self.funcnext()
                                            break
                                    elif self.c11 in ['<function force loop+>', '<function watch loop+>']:
                                        a = self.func_loop()
                                        if a == "__STOP__":
                                            while self.c11 != '<function loop body->':
                                                self.funcnext()
                                            break
                                        elif a != "None" and a != "__STOP__":
                                            back = a
                                            while self.c11 != '<function loop body->':
                                                self.funcnext()
                                            break
                                    elif self.c11 == '<initialization statement+>':
                                        self.func_initialization()
                                    elif self.c11 == '<pass>':
                                        pass
                                    elif self.c11 == '<continue>':
                                        continue
                                    elif self.c11 == '<break>':
                                        while self.c11 != '<function loop body->':
                                            self.funcnext()
                                        break
                                    elif self.c11 == '<function call+>':
                                        pass
                                    elif self.c11 == '<return+>':
                                        start_return = self.c22
                                        while self.c11 != '<return->':
                                            self.funcnext()
                                        end_return = self.c22 + 1
                                        back = "".join(self.value[start_return:end_return]).replace("back", "").replace(
                                            '"\\n"', '')
                                        variables = [key for key in self.FuncVariable.keys() if key in back]
                                        for variable in variables:
                                            back = back.replace(variable, str(self.FuncVariable[variable]))
                                        try:
                                            back = eval(back, None, self.tool)
                                        except:
                                            self.Output.append(
                                                f"|||Semantic Error: expression in \"back{back}\": Line {self.line_ctr(self.c22)}")
                                        while self.c11 != '<function loop body->':
                                            self.funcnext()
                                        break
                                    self.funcnext()
                                self.funcnext()
                            self.funcprev()
                        elif start > stop and step < 0:
                            for _ in range(start, stop, step):
                                if self.c11 == '<function force loop->':
                                    break
                                print(_, self.FuncVariable[id1])
                                if _ < start:
                                    id = {id1: self.FuncVariable[id1] + step}
                                    self.FuncVariable.update(id)
                                    self.FuncVariableDatatype.update({id1: "inst"})
                                    self.FuncPosition = startpos_loop
                                    self.CurrentFuncSequence = self.FuncSequence[self.FuncPosition]
                                    ckeys = list(self.CurrentFuncSequence.keys())
                                    cvalues = list(self.CurrentFuncSequence.values())
                                    self.c11 = ckeys[0]
                                    self.c22 = cvalues[0]

                                while self.c11 != '<function force loop->':  # execute the force loop body
                                    if self.c11 == '<output statement+>':
                                        self.func_output()
                                    elif self.c11 == '<function loop condition+>':
                                        a = self.func_loop_condition()
                                        if a == "__STOP__":
                                            while self.c11 != '<function loop body->':
                                                self.funcnext()
                                            break
                                        elif a != "None" and a != "__STOP__":
                                            back = a
                                            while self.c11 != '<function loop body->':
                                                self.funcnext()
                                            break
                                    elif self.c11 in ['<function force loop+>', '<function watch loop+>']:
                                        a = self.func_loop()
                                        if a == "__STOP__":
                                            while self.c11 != '<function loop body->':
                                                self.funcnext()
                                            break
                                        elif a != "None" and a != "__STOP__":
                                            back = a
                                            while self.c11 != '<function loop body->':
                                                self.funcnext()
                                            break
                                    elif self.c11 == '<initialization statement+>':
                                        self.func_initialization()
                                    elif self.c11 == '<pass>':
                                        pass
                                    elif self.c11 == '<continue>':
                                        continue
                                    elif self.c11 == '<break>':
                                        while self.c11 != '<function loop body->':
                                            self.funcnext()
                                        break
                                    elif self.c11 == '<function call+>':
                                        pass
                                    elif self.c11 == '<return+>':
                                        start_return = self.c22
                                        while self.c11 != '<return->':
                                            self.funcnext()
                                        end_return = self.c22 + 1
                                        back = "".join(self.value[start_return:end_return]).replace("back", "").replace(
                                            '"\\n"', '')
                                        variables = [key for key in self.FuncVariable.keys() if key in back]
                                        for variable in variables:
                                            back = back.replace(variable, str(self.FuncVariable[variable]))
                                        try:
                                            back = eval(back, None, self.tool)
                                        except:
                                            self.Output.append(
                                                f"|||Semantic Error: expression in \"back{back}\": Line {self.line_ctr(self.c22)}")
                                        while self.c11 != '<function loop body->':
                                            self.funcnext()
                                        break
                                    self.funcnext()
                                self.funcnext()
                            self.funcprev()
                        else:
                            self.Output.append(f"|||Semantic Error: in force Loop: Line {self.line_ctr(self.c22)}")
                    else:
                        self.Output.append(f"|||Semantic Error: in force Loop: Line {self.line_ctr(self.c22)}")
                del self.FuncVariable[id1]
                del self.FuncVariableDatatype[id1]

            elif self.c11 == '<function watch loop+>':  # if loop statement is a watch loop then go here
                self.funcnext()
                startpos_loop = self.FuncPosition
                loop_ctr = 0
                cond_result = self.func_condition()
                breaker = ""
                if cond_result == "pos":
                    while cond_result == "pos" and breaker == "":
                        if loop_ctr > 0:
                            self.FuncPosition = startpos_loop
                            self.CurrentFuncSequence = self.FuncSequence[self.FuncPosition]
                            ckeys = list(self.CurrentFuncSequence.keys())
                            cvalues = list(self.CurrentFuncSequence.values())
                            self.c11 = ckeys[0]
                            self.c22 = cvalues[0]
                            cond_result = self.func_condition()
                            if cond_result == "neg":
                                while self.c11 != '<function watch loop->':
                                    self.funcnext()
                                break
                        while self.c11 != '<function watch loop->':
                            if self.c11 == '<output statement+>':
                                self.func_output()
                            elif self.c11 == '<function loop condition+>':
                                a = self.func_loop_condition()
                                print("aa", a, self.c22, self.c11, self.value[73], self.value[78])
                                if a == "__STOP__":
                                    while self.c11 != '<function loop body->':
                                        self.funcnext()
                                    breaker = "__STOP__"
                                    break
                                elif a != "None" and a != "__STOP__":
                                    back = a
                                    while self.c11 != '<function loop body->':
                                        self.funcnext()
                                    breaker = "__STOP__"
                                    break
                            elif self.c11 in ['<function force loop+>', '<function watch loop+>']:
                                a = self.func_loop()
                                if a == "__STOP__":
                                    while self.c11 != '<function loop body->':
                                        self.funcnext()
                                    breaker = "__STOP__"
                                    break
                                elif a != "None" and a != "__STOP__":
                                    back = a
                                    while self.c11 != '<function loop body->':
                                        self.funcnext()
                                    breaker = "__STOP__"
                                    break
                            elif self.c11 == '<initialization statement+>':
                                self.func_initialization()
                            elif self.c11 == '<pass>':
                                pass
                            elif self.c11 == '<continue>':
                                continue
                            elif self.c11 == '<break>':
                                while self.c11 != '<function loop body->':
                                    self.funcnext()
                                breaker = "__STOP__"
                                break
                            elif self.c11 == '<function call+>':
                                pass
                            elif self.c11 == '<return+>':
                                start_return = self.c22
                                while self.c11 != '<return->':
                                    self.funcnext()
                                end_return = self.c22 + 1
                                back = "".join(self.value[start_return:end_return]).replace("back", "").replace(
                                    '"\\n"', '')
                                variables = [key for key in self.FuncVariable.keys() if key in back]
                                for variable in variables:
                                    back = back.replace(variable, str(self.FuncVariable[variable]))
                                try:
                                    back = eval(back, None, self.tool)
                                except:
                                    self.Output.append(
                                        f"|||Semantic Error: expression in \"back{back}\": Line {self.line_ctr(self.c22)}")
                                while self.c11 != '<function loop body->':
                                    self.funcnext()
                                breaker = "__STOP__"
                                break
                            self.funcnext()
                        loop_ctr += 1
                        self.funcnext()
                elif cond_result == "neg":  # if result is neg then skip loop statement
                    while self.c11 != '<function watch loop->':
                        self.funcnext()
                else:
                    self.Output.append(f"|||Semantic Error: in watch Loop: Line {self.line_ctr(self.c22)}")
            return back
        except:
            self.Output.append(f"|||Semantic Error: in function loop: Line {self.line_ctr(self.c22)}")

    def func_globe(self):
        try:
            while self.c11 != '<globe->':
                if self.c11 == '<id>':
                    var = self.value[self.c22]
                    aa = self.c22
                elif self.c11 == '<data type>':
                    data_type = self.value[self.c22]
                    bb = self.c22
                self.funcnext()
            if var not in self.GlobalVar:
                self.Output.append(f"|||Semantic Error: '{var}' is not found: Line {self.line_ctr(aa)}")
            if self.GlobalDatatype[var] != data_type:
                self.Output.append(f"|||Semantic Error: data type mismatch {data_type}: Line {self.line_ctr(bb)}")
            else:
                self.UnivVar.append(var)
        except:
            self.Output.append(f"|||Semantic Error: in function globe: Line {self.line_ctr(self.c22)}")

    def fixer_func_loop_condition(self):
        if self.c11 == '<function loop condition+>':
            self.funcnext()
        while self.c11 != '<function loop condition->':
            if self.c11 == '<function loop condition+>':
                self.fixer_func_loop_condition()
            self.funcnext()

    def func_loop_condition(self):
        try:
            back = "None"
            a = "None"
            while self.c11 != '<condition+>':  # condition for if statement.
                self.funcnext()
            cond_result = self.func_condition()
            if cond_result == "pos":
                while self.c11 != '<function loop if->':
                    if self.c11 == '<output statement+>':
                        self.func_output()
                    elif self.c11 == '<function loop condition+>':
                        a = self.func_loop_condition()
                        if a == "__STOP__":
                            while self.c11 != '<function loop body->':
                                self.funcnext()
                            return "__STOP__"
                        elif a != "None" and a != "__STOP__":
                            back = a
                            while self.c11 != '<function loop body->':
                                self.funcnext()
                            break
                    elif self.c11 in ['<function force loop+>', '<function watch loop+>']:
                        a = self.func_loop()
                        if a == "__STOP__":
                            while self.c11 != '<function loop body->':
                                self.funcnext()
                            return "__STOP__"
                        elif a != "None" and a != "__STOP__":
                            back = a
                            while self.c11 != '<function loop body->':
                                self.funcnext()
                            break
                    elif self.c11 == '<initialization statement+>':
                        self.func_initialization()
                    elif self.c11 == '<pass>':
                        pass
                    elif self.c11 == '<continue>':
                        continue
                    elif self.c11 == '<break>':
                        while self.c11 != '<function loop body->':
                            self.funcnext()
                        return "__STOP__"
                    elif self.c11 == '<function call+>':
                        pass
                    elif self.c11 == '<return+>':
                        start_return = self.c22
                        while self.c11 != '<return->':
                            self.funcnext()
                        end_return = self.c22 + 1
                        back = "".join(self.value[start_return:end_return]).replace("back", "").replace(
                            '"\\n"', '')
                        variables = [key for key in self.FuncVariable.keys() if key in back]
                        for variable in variables:
                            back = back.replace(variable, str(self.FuncVariable[variable]))
                        try:
                            back = eval(back, None, self.tool)
                        except:
                            self.Output.append(
                                f"|||Semantic Error: expression in \"back{back}\": Line {self.line_ctr(self.c22)}")
                        while self.c11 != '<function loop body->':
                            self.funcnext()
                        break
                    self.funcnext()
                while self.c11 != '<function loop condition->' and self.c11 != '<function loop body->':
                    self.funcnext()  # after executing the loop if body then skip to end of condition
            else:  # if "loop if" is neg then go to loop elib or loop elsa
                while self.c11 not in ['<function loop condition->', '<function loop elif+>', '<function loop else+>']:
                    if self.c11 == '<function loop condition+>':
                        self.fixer_func_loop_condition()
                    self.funcnext()
                ctr = 0  # for checking if it run a condition body once

                while self.c11 != '<function loop condition->' and self.c11 != '<function loop else+>':
                    if self.c11 != '<function loop elif+>':
                        while self.c11 != '<condition+>':
                            self.funcnext()
                        cond_result = self.func_condition()
                        if cond_result == "pos" and ctr == 0:  # if condition is true in elib then run its body and check if there is already body run before this
                            while self.c11 != '<function loop elif->':
                                ctr = 1
                                if self.c11 == '<output statement+>':
                                    self.func_output()
                                elif self.c11 == '<function loop condition+>':
                                    a = self.func_loop_condition()
                                    print("asda", a)
                                    if a == "__STOP__":
                                        while self.c11 != '<function loop body->':
                                            self.funcnext()
                                        return "__STOP__"
                                    elif a != "None" and a != "__STOP__":
                                        back = a
                                        while self.c11 != '<function loop body->':
                                            self.funcnext()
                                        break
                                elif self.c11 in ['<function force loop+>', '<function watch loop+>']:
                                    a = self.func_loop()
                                    if a == "__STOP__":
                                        while self.c11 != '<function loop body->':
                                            self.funcnext()
                                        return "__STOP__"
                                    elif a != "None" and a != "__STOP__":
                                        back = a
                                        while self.c11 != '<function loop body->':
                                            self.funcnext()
                                        break
                                elif self.c11 == '<initialization statement+>':
                                    self.func_initialization()
                                elif self.c11 == '<pass>':
                                    pass
                                elif self.c11 == '<continue>':
                                    continue
                                elif self.c11 == '<break>':
                                    while self.c11 != '<function loop body->':
                                        self.funcnext()
                                    return "__STOP__"
                                elif self.c11 == '<function call+>':
                                    pass
                                elif self.c11 == '<return+>':
                                    start_return = self.c22
                                    while self.c11 != '<return->':
                                        self.funcnext()
                                    end_return = self.c22 + 1
                                    back = "".join(self.value[start_return:end_return]).replace("back", "").replace(
                                        '"\\n"', '')
                                    variables = [key for key in self.FuncVariable.keys() if key in back]
                                    for variable in variables:
                                        back = back.replace(variable, str(self.FuncVariable[variable]))
                                    try:
                                        back = eval(back, None, self.tool)
                                    except:
                                        self.Output.append(
                                            f"|||Semantic Error: expression in \"back{back}\": Line {self.line_ctr(self.c22)}")
                                    while self.c11 != '<function loop body->':
                                        self.funcnext()
                                    break
                                self.funcnext()
                        else:
                            while self.c11 != '<function loop elif->':  # if loop if and loop elif is error then go loop else
                                self.funcnext()
                    self.funcnext()

                if self.c11 == '<function loop else+>' and ctr == 0:  # if loop if and loop elib is false then run loop else, also check if a condition body is already ran
                    if cond_result == "neg":
                        while self.c11 != '<function loop condition->':
                            if self.c11 == '<output statement+>':
                                self.func_output()
                            elif self.c11 == '<function loop condition+>':
                                a = self.func_loop_condition()
                                print("asda", a)
                                if a == "__STOP__":
                                    while self.c11 != '<function loop body->':
                                        self.funcnext()
                                    return "__STOP__"
                                elif a != "None" and a != "__STOP__":
                                    back = a
                                    while self.c11 != '<function loop body->':
                                        self.funcnext()
                                    break
                            elif self.c11 in ['<function force loop+>', '<function watch loop+>']:
                                a = self.func_loop()
                                if a == "__STOP__":
                                    while self.c11 != '<function loop body->':
                                        self.funcnext()
                                    return "__STOP__"
                                elif a != "None" and a != "__STOP__":
                                    back = a
                                    while self.c11 != '<function loop body->':
                                        self.funcnext()
                                    break
                            elif self.c11 == '<initialization statement+>':
                                self.func_initialization()
                            elif self.c11 == '<pass>':
                                pass
                            elif self.c11 == '<continue>':
                                continue
                            elif self.c11 == '<break>':
                                while self.c11 != '<function loop body->':
                                    self.funcnext()
                                return "__STOP__"
                            elif self.c11 == '<function call+>':
                                pass
                            elif self.c11 == '<return+>':
                                start_return = self.c22
                                while self.c11 != '<return->':
                                    self.funcnext()
                                end_return = self.c22 + 1
                                back = "".join(self.value[start_return:end_return]).replace("back", "").replace(
                                    '"\\n"', '')
                                variables = [key for key in self.FuncVariable.keys() if key in back]
                                for variable in variables:
                                    back = back.replace(variable, str(self.FuncVariable[variable]))
                                try:
                                    back = eval(back, None, self.tool)
                                except:
                                    self.Output.append(
                                        f"|||Semantic Error: expression in \"back{back}\": Line {self.line_ctr(self.c22)}")
                                while self.c11 != '<function loop body->':
                                    self.funcnext()
                                break
                            self.funcnext()
                    else:
                        while self.c11 != '<function loop condition->':
                            self.funcnext()

            return back
        except:
            self.Output.append(f"|||Semantic Error: in function loop condition: Line {self.line_ctr(self.c2)}")



    def func_condition(self):
        try:
            start = self.c22  # get the conditionand evaluate if true or false
            end = 0
            self.funcnext()
            while '<condition->' != self.c11:
                self.funcnext()
            if '<condition->' == self.c11:
                end = self.c22

            cond_exp = " ".join(self.value[start:end + 1]).replace('"\\n"', "").replace("-", "-")
            cond_exp = self.replace_variables(cond_exp, self.FuncVariable)
            try:
                if "False" == (
                str(eval(str(cond_exp), None, self.tool))):  # return neg or pos instead of False or True
                    result = "neg"
                else:
                    result = "pos"
                return result
            except Exception as e:
                a = str(e)
                b = a.replace('int', 'inst').replace('str', 'strike').replace('float', 'flank')
                error_list = ["unsupported operand type(s) for +: 'int' and 'str'",
                              'can only concatenate str (not "int") to str',
                              'can only concatenate str (not "float") to str',
                              "unsupported operand type(s) for +: 'float' and 'str'",
                              "'<' not supported between instances of 'int' and 'str'",
                              "'<' not supported between instances of 'float' and 'str'",
                              "'>=' not supported between instances of 'int' and 'str'",
                              "'>=' not supported between instances of 'float' and 'str'",
                              "'<=' not supported between instances of 'int' and 'str'",
                              "'<=' not supported between instances of 'float' and 'str'",
                              "'>' not supported between instances of 'int' and 'str'",
                              "'>' not supported between instances of 'float' and 'str'"]

                if a in error_list:
                    self.Output.append(f"|||Semantic Error: {b}: Line {self.line_ctr(self.c22)}")
                elif "unexpected EOF while parsing" in a:
                    self.Output.append(
                        f"|||Semantic Error: strike cannot be operated with other data types: Line {self.line_ctr(self.c22)}")
                else:
                    self.Output.append(
                        f"|||Semantic Error: Undeclared Variable in {cond_exp}: Line {self.line_ctr(self.c22)}")
        except:
            self.Output.append(f"|||Semantic Error: in function condition: Line {self.line_ctr(self.c22)}")

    def fixer_func_condition(self):
        if self.c11 == '<function condition+>':
            self.funcnext()
        while self.c11 != '<function condition->':
            if self.c11 == '<function condition+>':
                self.fixer_func_condition()
            self.funcnext()

    def func_condition_statement(self):
        try:
            back = "None"
            a = "None"
            while self.c11 != '<condition+>':  # condition for if statement.
                self.funcnext()
            cond_result = self.func_condition()
            if cond_result == "pos":
                while self.c11 != '<function if->':
                    if self.c11 == '<output statement+>':
                        self.func_output()
                    elif self.c11 == '<function condition+>':
                        a = self.func_condition_statement()
                        if a != "None":
                            back = a
                            while self.c11 != '<function condition body->':
                                self.funcnext()
                            break
                    elif self.c11 in ['<function force loop+>', '<function watch loop+>']:
                        a = self.func_loop()
                        if a != "None":
                            back = a
                            while self.c11 != '<function condition body->':
                                self.funcnext()
                            break
                    elif self.c11 == '<initialization statement+>':
                        self.func_initialization()
                    elif self.c11 == '<pass>':
                        pass
                    elif self.c11 == '<function call+>':
                        pass
                    elif self.c11 == '<return+>':
                        start_return = self.c22
                        while self.c11 != '<return->':
                            self.funcnext()
                        end_return = self.c22 + 1
                        back = "".join(self.value[start_return:end_return]).replace("back", "").replace(
                            '"\\n"', '')
                        variables = [key for key in self.FuncVariable.keys() if key in back]
                        for variable in variables:
                            back = back.replace(variable, str(self.FuncVariable[variable]))
                        try:
                            back = eval(back, None, self.tool)
                        except:
                            self.Output.append(
                                f"|||Semantic Error: expression in \"back{back}\": Line {self.line_ctr(self.c22)}")
                        while self.c11 != '<function condition body->':
                            self.funcnext()
                        break
                    self.funcnext()
                while self.c11 != '<function condition->':
                    self.funcnext()
            else:  # for elib and elsa
                while self.c11 not in ['<function condition->', '<function elif+>', '<function else+>']:
                    if self.c11 == '<function condition+>':
                        self.fixer_func_condition()
                    self.funcnext()
                ctr = 0
                while self.c11 != '<function condition->' and self.c11 != '<function else+>':
                    if self.c11 != '<function elif+>':
                        while self.c11 != '<condition+>':
                            self.funcnext()
                        cond_result = self.func_condition()
                        if cond_result == "pos" and ctr == 0:
                            while self.c11 != '<function elif->':
                                ctr = 1
                                if self.c11 == '<output statement+>':
                                    self.func_output()
                                elif self.c11 == '<function condition+>':
                                    a = self.func_condition_statement()
                                    if a != "None":
                                        back = a
                                        while self.c11 != '<function condition body->':
                                            self.funcnext()
                                        break
                                elif self.c11 in ['<function force loop+>', '<function watch loop+>']:
                                    a = self.func_loop()
                                    if a != "None":
                                        back = a
                                        while self.c11 != '<function condition body->':
                                            self.funcnext()
                                        break
                                elif self.c11 == '<initialization statement+>':
                                    self.func_initialization()
                                elif self.c11 == '<pass>':
                                    pass
                                elif self.c11 == '<function call+>':
                                    pass
                                elif self.c11 == '<return+>':
                                    start_return = self.c22
                                    while self.c11 != '<return->':
                                        self.funcnext()
                                    end_return = self.c22 + 1
                                    back = "".join(self.value[start_return:end_return]).replace("back", "").replace(
                                        '"\\n"', '')
                                    variables = [key for key in self.FuncVariable.keys() if key in back]
                                    for variable in variables:
                                        back = back.replace(variable, str(self.FuncVariable[variable]))
                                    try:
                                        back = eval(back, None, self.tool)
                                    except:
                                        self.Output.append(
                                            f"|||Semantic Error: expression in \"back{back}\": Line {self.line_ctr(self.c22)}")
                                    while self.c11 != '<function condition body->':
                                        self.funcnext()
                                    break
                                self.funcnext()
                            while self.c11 != '<function elif->':
                                self.funcnext()
                        else:
                            while self.c11 != '<function elif->':
                                self.funcnext()
                    self.funcnext()
                if self.c11 == '<function else+>' and ctr == 0:
                    if cond_result == "neg":
                        while self.c11 != '<function condition->':
                            if self.c11 == '<output statement+>':
                                self.func_output()
                            elif self.c11 == '<function condition+>':
                                a = self.func_condition_statement()
                                if a != "None":
                                    back = a
                                    while self.c11 != '<function condition body->':
                                        self.funcnext()
                                    break
                            elif self.c11 in ['<function force loop+>', '<function watch loop+>']:
                                a = self.func_loop()
                                if a != "None":
                                    back = a
                                    while self.c11 != '<function condition body->':
                                        self.funcnext()
                                    break
                            elif self.c11 == '<initialization statement+>':
                                self.func_initialization()
                            elif self.c11 == '<pass>':
                                pass
                            elif self.c11 == '<function call+>':
                                pass
                            elif self.c11 == '<return+>':
                                start_return = self.c22
                                while self.c11 != '<return->':
                                    self.funcnext()
                                end_return = self.c22 + 1
                                back = "".join(self.value[start_return:end_return]).replace("back", "").replace(
                                    '"\\n"', '')
                                variables = [key for key in self.FuncVariable.keys() if key in back]
                                for variable in variables:
                                    back = back.replace(variable, str(self.FuncVariable[variable]))
                                try:
                                    back = eval(back, None, self.tool)
                                except:
                                    self.Output.append(
                                        f"|||Semantic Error: expression in \"back{back}\": Line {self.line_ctr(self.c22)}")
                                while self.c11 != '<function condition body->':
                                    self.funcnext()
                                break
                            self.funcnext()
                        while self.c11 != '<function condition->':
                            self.funcnext()
                else:
                    while self.c11 != '<function condition->':
                        self.funcnext()
            return back
        except:
            self.Output.append(f"|||Semantic Error: in function condition statement: Line {self.line_ctr(self.c22)}")

    def token_type(self):
        while self.c1 != '<program->' and self.c1 != '\0':
            if '<declaration+>' in self.c1:
                self.declaration()
            elif '<initialization statement+>' in self.c1:
                self.initialization_statement()
            elif '<output statement+>' in self.c1:
                self.output_statement()
            elif '<condition statement+>' in self.c1:
                self.condition_statement()
            elif self.c1 in ['<force loop+>', '<watch loop+>']:
                self.loop_statement()
            elif '<function call statement+>' in self.c1:
                self.function_call_statement()
            elif '<function+>' in self.c1:
                self.function()
            elif '<condition+>' in self.c1:
                self.condition()
            self.next()
        print("Global:", self.GlobalVar, "\nFuncVar: ", self.FuncVariable, "\nUnivar: ", self.UnivVar)

