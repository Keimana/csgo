
currentChar = ""  # Current character being processed
errorChar = []  # Define error characters
alpha = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j','k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't','u', 'v', 'w', 'x', 'y', 'z']
num = list('0123456789')  # Convert string to list of characters
delim1 = ['{']
delim2 = ['~']
delim3 = [' ']
delim4 = ['(']
delim5 = [' ', '(']
delim6 = [' ', '^', '}', '\n', '\0', '+', '-', '*', '/', '%', '=', '<', '>', '!', '#']  + num + alpha
delim7 = ['=', ' ']
delim8 = [' ', '=', ')', '\0', '!', ',', '\n'] + alpha
delim9 = [' ', "'", '(', '"', ] + num + alpha
delim10 = ['num', "'", '"', '[', ']', ')', '#'] + num + alpha
delim11 = [' ', '\0', '\n'] + alpha
delim12 = [' ', '\0', '~', '\n']
delim13 = [' ', '"', '(', "'"] + num + alpha
delim14 = [' ', 'num', '(', '_']
delim15 = [' ', 'num', '(', '_', '"']
delim16 = [' ', '\0', '\n', '~', '$']
delim17 = [' ', '\0', '"', '(', "'", ')'] + num + alpha
delim18 = [' ', '\0', '\n', '+', '-', '*', '/', '%', '!', '=', '<', '>', ',', '}', ')', '{', ] + alpha
delim19 = ['=', '*', ')', ' ', '\0', '+', ']', '%', ',', '}', '/', '<', '[', '>', '\n', '!', '-' ]
delim20 = [' ', '+', '=', '!', ',', '^', ')', '}', '\n', '\0', ']', '$']
delim21 = ['\0', '}', ' ', '\n', '^', ']', '$', '#', '%', '+', '>', '<', '/', '`', '*', '!', '-', ')' ]
delim22 = [' ', '\0', '\n', '"', '(', ')', '-', "'", '#', ']', ','] + num + alpha
delim23 = ['[', '}', '$', "'", '\0', "#", '"', ')'] + num + alpha
delim24 = [')', ']', '+', '=', '}', '*', '\0', ',', '/', '[', '<', '>', '-', ' ', '%', '{', '(', '\n', '!', '`']
delim25 = [' ', '(', '_', '"'] + num + alpha
delim26 = [' ', '\n', '}', '$', "'", ]
delim27 = [' ', '\n']
delim28 = [' ',  '\n', '\0']
delim29 = ['\n', '\0', 'a', 'b', 'c', 'd', 'f', 'g', 'i', 'l', 'n', 'o', 'p', 'r', 's', 't', 'w', '`', '$' ]
zero = '0'
errorChar = ['!', '@', '%', '&', '*', '(', ')', '-', '_', '+', '=', '{', '}', '[', ']', '~', '\\', ':', "'", '"', ',', '.', '<', '>', '/', '?', '~']
unknownCharacters = ['@',  '&', '_', '?', '~', '-', '~', '\\', ':', 'e', 'h', 'j', 'k', 'm', 'q', 'u', 'v', 'x', 'y', 'z', '.', "'"] + [chr(ord('A') + i) for i in range(26)]
reservedkeywords = ["abort", "an ", "back", "bounce", "chat", "defuse", "flank", "force", "in", "inst", "info","load", "neg", "not", "or", "perim", "plant", "push", "re", "reload", "strike", "tool", "watch"]

class DEDOSLexicalAnalyzer:
    def __init__(self, lexeme):         #local declarations inside the class
        self.lexeme = lexeme
        self.currentChar = lexeme[0]
        self.position = 0
        self.value_ = None
        self.type_ = None
        self.fullResult = None
        self.tokens = []
        self.IDcounter = 0
        self.tokensForUnknown = []
        self.lineCounter = 1

    def peek(self):
        # Assuming self.input is your input string and self.position is the index of self.currentChar
        pos = self.position + 1
        if pos < len(self.lexeme):
            return self.lexeme[pos]
        return '\0'


    def next(self):                     #character next function
        self.position += 1
        if self.position > len(self.lexeme) - 1:
            self.currentChar = '\0'
        else:
            self.currentChar = self.lexeme[self.position]

             
    def a_token(self):  # Tokens that start with A
        result = ""
        result += self.currentChar
        self.next()

        if self.currentChar == "b":  # abort token
            result += self.currentChar
            self.next()
            
            for char in "ort":
                if self.currentChar != char:
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use "abort"'
                result += self.currentChar
                self.next()
            
            # Ensure that the next character is a valid delimiter after "abort"
            if self.currentChar in delim12:
                return "abort", result
            else:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use {", ".join([repr(x) for x in delim12])}'


        elif self.currentChar == "n":  # and token
            result += self.currentChar
            self.next()
            if self.currentChar == 'd':
                result += self.currentChar
                self.next()
                if self.currentChar in delim5:  # Ensure correct delimiter
                    return "and", result
                else:
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use {", ".join([repr(x) for x in delim5])}'

            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use "and"'

        else:
            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use "and"'

        
    def b_token(self):  # Tokens that start with B
        result = ""

        result += self.currentChar
        self.next()

        if self.currentChar == 'a':  # back token
            result += self.currentChar
            self.next()
            if self.currentChar == 'c':
                result += self.currentChar
                self.next()
                if self.currentChar == 'k':
                    result += self.currentChar
                    self.next()
                    if self.currentChar not in delim4:
                        return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use {", ".join([repr(x) for x in delim4])}'
                    return "back", result

                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use "back"'

        elif self.currentChar == 'o':  # bounce token
            result += self.currentChar
            self.next()
            if self.currentChar == 'u':
                result += self.currentChar
                self.next()
                if self.currentChar == 'n':
                    result += self.currentChar
                    self.next()
                    if self.currentChar == 'c':
                        result += self.currentChar
                        self.next()
                        if self.currentChar == 'e':
                            result += self.currentChar
                            self.next()
                            if self.currentChar in delim12:  # Ensure it's correctly delimited
                                return "bounce", result
                            else:
                                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use {", ".join([repr(x) for x in delim12])}'

                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use "bounce"'

        return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use "bounce", "back"'

    
    def c_token(self):  # Tokens that start with C
        result = ""

        result += self.currentChar  # 'c'
        self.next()

        if self.currentChar == "h":  # 'chat' token
            result += self.currentChar  # 'ca'
            self.next()
            if self.currentChar == 'a':
                result += self.currentChar
                self.next()
                if self.currentChar == 't':
                    result += self.currentChar
                    self.next()
                    if self.currentChar not in delim5:
                        return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim5])}'

                    return "chat", result

        # If no valid token is found, return a default value
        return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use "chat"'

        
    def d_token(self):  # Tokens that start with D
        result = ""

        result += self.currentChar
        self.next()

        if self.currentChar == 'e':  # defuse token
            result += self.currentChar
            self.next()
            if self.currentChar == 'f':
                result += self.currentChar
                self.next()
                if self.currentChar == 'u':
                    result += self.currentChar
                    self.next()
                    if self.currentChar == 's':
                        result += self.currentChar
                        self.next()
                        if self.currentChar == 'e':
                            result += self.currentChar
                            self.next()
                            if self.currentChar not in delim3:
                                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim3])}'
                            return "defuse", result

                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use   "defuse"'


            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  "defuse"'

        else:
            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  "defuse"'

    def f_token(self):  # Tokens that start with F
        result = ""
        result += self.currentChar
        self.next()

        if self.currentChar == 'l':  # Check for "flank" token
            result += self.currentChar
            self.next()
            if self.currentChar == 'a':
                result += self.currentChar
                self.next()
                if self.currentChar == 'n':
                    result += self.currentChar
                    self.next()
                    if self.currentChar == 'k':
                        result += self.currentChar
                        self.next()
                        if self.currentChar not in delim3:
                            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim3])}'
                        return "flank", result

                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  "flank"'

                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  "flank"'

            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  "flank"'

        elif self.currentChar == 'o':  # Check for "force" token
            result += self.currentChar
            self.next()
            if self.currentChar == 'r':
                result += self.currentChar
                self.next()
                if self.currentChar == 'c':
                    result += self.currentChar
                    self.next()
                    if self.currentChar == 'e':
                        result += self.currentChar
                        self.next()
                        if self.currentChar not in delim3:
                            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim3])}'
                        return "force", result

                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  "force"'

                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  "force"'

            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  "force"'

        # If no valid token is found, return a default value
        return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use "flank" or "force"'


    def g_token(self):  # Tokens that start with G
        result = ""

        for char in "globe":  # goon token
            if self.currentChar != char:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use   "globe"'
            result += self.currentChar
            self.next()
        if self.currentChar not in delim3:
            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim3])}'

        return "globe", result
        
    def i_token(self):  # Tokens that start with "i"
        result = ""

        # Read initial "i"
        if self.currentChar is None:
            return "Hey Agent! This Lexeme is Unknown", '"i" \nUnexpected end of input'
        result += self.currentChar  # result = "i"
        self.next()

        # Expect an "n" after "i"
        if self.currentChar is None:
            return "Hey Agent! This Lexeme is Unknown", f'"{result}" \nUnexpected end of input'
        if self.currentChar != 'n':
            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Expected "in", got {self.currentChar!r}'
        result += self.currentChar  # result = "in"
        self.next()

        # Now, look ahead to see if we have extra letters
        if self.currentChar is not None:
            # If the next letter is 's', it might be "inst"
            if self.currentChar == 's':
                result += self.currentChar  # result = "ins"
                self.next()
                if self.currentChar is not None and self.currentChar == 't':
                    result += self.currentChar  # result = "inst"
                    self.next()
                    # Only check the delimiter if there is a next character
                    if self.currentChar is not None and self.currentChar not in delim3:
                        return "Hey Agent! This Lexeme is Unknown", f'"{result}" \nUse one of: {", ".join([repr(x) for x in delim3])}'
                    return "inst", result
                else:
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Expected "inst"'
            
            # If the next letter is 'f', it might be "info"
            elif self.currentChar == 'f':
                result += self.currentChar  # result = "inf"
                self.next()
                if self.currentChar is not None and self.currentChar == 'o':
                    result += self.currentChar  # result = "info"
                    self.next()
                    # Check delimiter only if there's another character
                    if self.currentChar is not None and self.currentChar not in delim4 and self.currentChar != '(':
                        return "Hey Agent! This Lexeme is Unknown", f'"{result}" \nUse one of: {", ".join([repr(x) for x in delim4])}'
                    return "info", result
                else:
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Expected "info"'
            
            # Otherwise, if the next character is a valid delimiter, we have just "in"
            else:
                if self.currentChar not in delim3:
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" \nUse one of: {", ".join([repr(x) for x in delim3])}'
                return "in", result
        else:
            # End of input after "in" is acceptable
            return "in", result


    def l_token(self):  # Tokens that start with F
        result = ""

        for char in "load":  # load token
            if self.currentChar != char:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  "load"'
            result += self.currentChar
            self.next()
        if self.currentChar not in delim1:
            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim1])}'

        return "load", result
        
    def n_token(self):  # Tokens that start with N
        result = ""
        result += self.currentChar  # already 'n'
        self.next()

        # Handle "neg"
        if self.currentChar == 'e':
            result += self.currentChar
            self.next()
            if self.currentChar != 'g':  # If next character isn't 'g', return error
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use   "neg"'
            result += self.currentChar
            self.next()

            if self.currentChar not in delim8:  # Check if current character is in delim8
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" \n Use   {", ".join([repr(x) for x in delim8])}'

            return "neg", result

        # Handle "not"
        elif self.currentChar == 'o':
            result += self.currentChar
            self.next()
            if self.currentChar != 't':  # Now expect a 't'
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use   "not"'
            result += self.currentChar
            self.next()

            if self.currentChar not in delim5:  # Check if current character is in delim5
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" \n Use   {", ".join([repr(x) for x in delim5])}'

            return "not", result

        # Default case when neither "neg" nor "not" are found
        return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use   "neg", "not"'


        

    def o_token(self):  # Tokens that start with O
        result = ""

        for char in "or":  # or token
            if self.currentChar != char:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use   "or"'
            result += self.currentChar
            self.next()
        if self.currentChar not in delim5:
            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim5])}'

        return "or", result

        
    def p_token(self):  # Tokens that start with P
        result = ""

        result += self.currentChar
        self.next()

        # Handle "plant" token
        if self.currentChar == 'l':  
            result += self.currentChar
            self.next()
            if self.currentChar == 'a':
                result += self.currentChar
                self.next()
                if self.currentChar == 'n':
                    result += self.currentChar
                    self.next()
                    if self.currentChar == 't':
                        result += self.currentChar
                        self.next()

                    if self.currentChar not in delim4:  # Check if in delim4
                        return "Hey Agent! This Lexeme is Unknown", f'"{result}" \n Use   {", ".join([repr(x) for x in delim4])}'

                    return "plant", result

                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  "plant"'

        # Handle "poor" token
        elif self.currentChar == 'o':
            result += self.currentChar
            self.next()
            if self.currentChar == 's':
                result += self.currentChar
                self.next()
                if self.currentChar not in delim8:  # Check if in delim8
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" \n Use   {", ".join([repr(x) for x in delim8])}'

                return "pos", result

            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  "pos"'

        # Handle "push" token
        elif self.currentChar == 'u':
            result += self.currentChar
            self.next()
            if self.currentChar == 's':
                result += self.currentChar
                self.next()
                if self.currentChar == 'h':
                    result += self.currentChar
                    self.next()

                if self.currentChar not in delim12:  # Check if in delim12
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" \n Use   {", ".join([repr(x) for x in delim12])}'

                return "push", result

            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  "push"'

        # Handle "perim" token (new addition)
        elif self.currentChar == 'e':  # Check for "perim"
            result += self.currentChar
            self.next()
            if self.currentChar == 'r':
                result += self.currentChar
                self.next()
                if self.currentChar == 'i':
                    result += self.currentChar
                    self.next()
                    if self.currentChar == 'm':
                        result += self.currentChar
                        self.next()

                    if self.currentChar not in delim4:  # Check if in delim4
                        return "Hey Agent! This Lexeme is Unknown", f'"{result}" \n Use   {", ".join([repr(x) for x in delim4])}'

                    return "perim", result

                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  "perim"'

            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  "perim"'

        # If no valid token is found, return a default value
        return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  "plant", "poor", "push", or "perim"'

                
    def r_token(self):  # Tokens that start with R
        result = ""

        result += self.currentChar
        self.next()

        if self.currentChar == 'e':  # Possible 're' or 'reload' token
            result += self.currentChar
            self.next()

            if self.currentChar == 'l':  # Check for 'reload' token
                result += self.currentChar
                self.next()
                for char in "oad":
                    if self.currentChar != char:
                        return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  "reload"'
                    result += self.currentChar
                    self.next()

                if self.currentChar not in delim4:
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim4])}'

                return "reload", result

            elif self.currentChar not in delim4:  # Check for 're' token with delim4
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" \n Use   {", ".join([repr(x) for x in delim4])}'

            return "re", result

        return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  "re" or "reload"'



    def s_token(self):                       # Tokens that start with S
        result = ""

        for char in "strike":                 #strike token
            if self.currentChar != char:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  "strike"'
            result += self.currentChar
            self.next()
        if self.currentChar not in delim3:
            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim3])}'

        return "strike", result

    def t_token(self): # Tokens that start with T
        result = ""

        for char in "tool":                
            if self.currentChar != char:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use   "tool"'
            result += self.currentChar
            self.next()
        if self.currentChar not in delim3:
            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim3])}'

        return "tool", result


    def w_token(self): # Tokens that start with W
        result = ""

        for char in "watch": 
            if self.currentChar != char:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use   "watch"'
            result += self.currentChar
            self.next()
        if self.currentChar not in delim4:
            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim4])}'

        return "watch", result


    def rel_token(self):                 #Tokens for Relational Operators
        result = ""

        result += self.currentChar
        self.next()

        if result[0] == "<":                    #< token
            if self.currentChar == "=":
                result += self.currentChar
                self.next()
                if self.currentChar in delim14:  #<= token
                    return "<=", result
                else:
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim14])}'
            if self.currentChar in delim5:
                return "<", result
            else:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim5])}'

        elif result[0] == ">":                  #> token
            if self.currentChar == "=":
                result += self.currentChar
                self.next()
                if self.currentChar in delim14:  #>= token
                    return ">=", result
                else:
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim14])}'
            if self.currentChar in delim5:
                return ">", result
            else:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim5])}'

        elif result[0] == "=":                  #= token
            if self.currentChar == "=":
                result += self.currentChar
                self.next()

                if self.currentChar in delim14:  #== token
                    return "==", result
                else:
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim14])}'
            if self.currentChar in delim3:    # = token
                return "=", result
            else:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim3])}'
            
        elif result[0] == "!":                  #!= token
            if self.currentChar == "=":
                result += self.currentChar
                self.next()

                if self.currentChar in delim14:
                    return "!=", result
                else:
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim14])}'
            else:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use   "!="'

        return "Hey Agent! This Lexeme is Unknown", f'"{result}" \n ERROR: Incorrect Delimiter'
    
    def operatorToken(self):  # Tokens for Arithmetic Operators
        result = ""

        if self.currentChar == "+":             # + Token
            result += self.currentChar
            self.next()

            if self.currentChar in delim22:
                return "+", result

            if self.currentChar == "=":
                result += self.currentChar
                self.next()

                if self.currentChar in delim15:  # += Token
                    return "+=", result
                else:
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use {", ".join([repr(x) for x in delim15])}'

            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use {", ".join([repr(x) for x in delim22])}'

        elif self.currentChar == "-":  # - Token
            # Peek at the next character to decide if it's a negative literal
            if self.peek() in "0123456789":
                return self.digits()  # Delegate to digits() to handle negative numbers like -2 or -2.2
            
            result += self.currentChar
            self.next()

            if self.currentChar in delim22:
                return "-", result

            if self.currentChar == "=":         # -= Token
                result += self.currentChar
                self.next()

                if self.currentChar in delim22:
                    return "-=", result
                else:
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use {", ".join([repr(x) for x in delim14])}'

            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use {", ".join([repr(x) for x in delim14])}'

        # ... handle other operators (*, /, %) as before
        elif self.currentChar == "*":
            result += self.currentChar
            self.next()

            if self.currentChar in delim14:      # * Token
                return "*", result

            if self.currentChar == "=":
                result += self.currentChar
                self.next()

                if self.currentChar in delim14:  # *= Token
                    return "*=", result
                else:
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use {", ".join([repr(x) for x in delim14])}'

            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use {", ".join([repr(x) for x in delim14])}'

        elif self.currentChar == "/":
            result += self.currentChar
            self.next()

            if self.currentChar in delim14:      # / Token
                return "/", result

            if self.currentChar == "=":
                result += self.currentChar
                self.next()

                if self.currentChar in delim14:  # /= Token
                    return "/=", result
                else:
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use {", ".join([repr(x) for x in delim14])}'

            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use {", ".join([repr(x) for x in delim14])}'

        elif self.currentChar == "%":
            result += self.currentChar
            self.next()

            if self.currentChar in delim14:      # % Token
                return "%", result

            if self.currentChar == "=":
                result += self.currentChar
                self.next()

                if self.currentChar in delim14:  # %= Token
                    return "%=", result
                else:
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use {", ".join([repr(x) for x in delim14])}'

            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use {", ".join([repr(x) for x in delim14])}'

        else:
            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use "+", "-", "*", "/", "%", "+=", "-=", "*=", "/=", "%="'

    def comment_token(self):
        result = ""
        if self.currentChar == "`":
            result += self.currentChar

            while True:
                self.next()
                result += self.currentChar

                if self.currentChar == "`":
                    self.next()

                    if self.currentChar in delim28:
                        return "COMMENT", result
                    else:
                        return "Hey Agent! This Lexeme is Unknown", f'"{result}" \n'
                        #break

                elif self.currentChar == '\0':
                    print("1", result)
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use   "`"'

        elif self.currentChar == "$":
            result += self.currentChar

            while True:
                self.next()
                result += self.currentChar

                if self.currentChar == "$":
                    self.next()

                    if self.currentChar in delim28:
                        return "COMMENT", result
                    else:
                        return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim28])}'
                        #break

                elif self.currentChar == '\0':
                    print("1", result)
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use   "$"'

        else:
            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use   "##", "`"'

    def special_token(self):
        result = ""

        if self.currentChar == "{":         #{ Token
            result += self.currentChar
            self.next()

            if self.currentChar in delim11:
                return "{", result
            else:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim11])}'
        elif self.currentChar == "}":         #} Token
            result += self.currentChar
            self.next()

            if self.currentChar in delim11:
                return "}", result
            else:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim11])}'
        elif self.currentChar == "(":         #(Token
            result += self.currentChar
            self.next()

            if self.currentChar in delim23:
                return "(", result
            else:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim23])}'
        elif self.currentChar == ")":         #) Token
            result += self.currentChar
            self.next()

            if self.currentChar in delim18:
                return ")", result
            else:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim18])}'
        elif self.currentChar == "[":         #[Token
            result += self.currentChar
            self.next()

            if self.currentChar in delim10:
                return "[", result
            else:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim10])}'
        elif self.currentChar == "]":         #] Token
            result += self.currentChar
            self.next()

            if self.currentChar in delim19:
                return "]", result
            else:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim19])}'
            
        elif self.currentChar == "~":  # | Token
            result += self.currentChar
            self.next()

            if self.currentChar in delim29:
                return "~", result
            else:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim29])}'
            
        elif self.currentChar == "'":  # ' Token
            result += self.currentChar
            self.next()
            print(result, self.currentChar)
            if self.currentChar == "\0":
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use   "\'\'"'
            if self.currentChar == "'":
                result += self.currentChar
                self.next()
                return "CHATLIT", result
            result += self.currentChar
            self.next()
            print(result, self.currentChar)
            if self.currentChar == "'":
                result += self.currentChar
                self.next()
                print(result, self.currentChar)
                if self.currentChar in delim20:
                    return "CHATLIT", result
                else:
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim20])}'
            else:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use   "\'\'"'

        elif self.currentChar == '"':  # ' Token
            result += self.currentChar
            self.next()
            print(result, self.currentChar)
            if self.currentChar == "\0":
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use   "\'\'"'
            if self.currentChar == '"':
                result += self.currentChar
                self.next()
                return "STRIKELIT", result
            result += self.currentChar
            self.next()
            print(result, self.currentChar)
            if self.currentChar == '"':
                result += self.currentChar
                self.next()
                print(result, self.currentChar)
                if self.currentChar in delim20:
                    return "STRIKELIT", result
                else:
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim20])}'
            else:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use   "\'\'"'
            
        else:
            return "Hey Agent! This Lexeme is Unknown", f'"{result}" \n ERROR: Incorrect Delimiter'

    def UnknownToken(self):
        result = self.currentChar  # Start with the first unknown character
        self.next()

        while self.currentChar.isalpha():  # Continue if it's part of a word
            result += self.currentChar
            self.next()

        return "Hey Agent! This Lexeme is Unknown.", result

    
    def strikelit_token(self):               #Token for STRIKELIT
        result = ""

        if self.currentChar == '"':
            while True:
                result += self.currentChar
                self.next()

                if self.currentChar == '"':
                    result += self.currentChar
                    self.next()

                    if self.currentChar in delim20:
                        return "STRIKELIT", result
                    else:
                        return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim20])}'

                if self.currentChar == '\n' or self.currentChar == '\0':
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use   (\" \")'

    def chatlit_token(self):               #Token for STRIKELIT
        result = ""

        if self.currentChar == "'":
            while True:
                result += self.currentChar
                self.next()

                if self.currentChar == "'":
                    result += self.currentChar
                    self.next()

                    if self.currentChar in delim20:
                        return "CHATLIT", result
                    else:
                        return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim20])}'

                if self.currentChar == '\n' or self.currentChar == '\0':
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use   (\" \")'
                
    def seperator_token(self):
        result = ""
        result += self.currentChar
        self.next()

        if self.currentChar in delim22:
            return "COMMA", result
        else:
            return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use  {", ".join([repr(x) for x in delim22])}'
    def digits(self):
        result = ""
        instctr = 0  # Counter for integer part
        flankctr = 0  # Counter for decimal part
        has_decimal = False  # Flag to track if a decimal has been encountered


        # Check for negative sign at the start
        if self.currentChar == "-":
            result += self.currentChar
            self.next()

        if self.currentChar in "0123456789":  
            if self.currentChar == "0":  # Check for leading zero issue
                result += self.currentChar
                self.next()
                if self.currentChar in "0123456789":  
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" \n ERROR: Leading zeros are not allowed'

            while self.currentChar in "0123456789" and self.currentChar != '\0':
                if instctr >= 9:  # Prevent exceeding max integer length
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" \n Bullet Error: Integer part exceeds 9 digits'

                result += self.currentChar
                self.next()
                instctr += 1

            if self.currentChar == ".":  # Decimal point found
                if has_decimal:
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" \n ERROR: Multiple decimal points are not allowed'

                has_decimal = True
                result += self.currentChar
                self.next()

                while self.currentChar in "0123456789" and self.currentChar != '\0':
                    if flankctr >= 5:  # Prevent exceeding max decimal length
                        return "Hey Agent! This Lexeme is Unknown", f'"{result}" \n Bullet Error: Decimal part exceeds 5 digits'

                    result += self.currentChar
                    self.next()
                    flankctr += 1

                if flankctr == 0:
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" \n Expected digits after "."'

                if self.currentChar in delim22:  # Valid floating-point literal
                    return "FLANKLIT", result

            elif self.currentChar in delim22:  # Valid integer literal
                return "INSTLIT", result

            return "Hey Agent! This Lexeme is Unknown", f'"{result}" \n Expected Delimiter⏵ {", ".join([repr(x) for x in delim22])}'

        return "Hey Agent! This Lexeme is Unknown", f'"{result}" \n Expected a number"'


    def SpaceToken(self):
        result = '"'
        result += self.currentChar
        self.next()
        if self.currentChar != " ":
            pass
        return "SPACE_TOKEN", "SPACE"

    def IdentifierToken(self):
        result = ""
        result += self.currentChar
        self.next()

        if self.currentChar in "abcdefghijklmnopqrstuvwxyz" or self.currentChar == "_":  # First character must be lowercase or _
            result += self.currentChar
            self.next()

            while (self.currentChar in "abcdefghijklmnopqrstuvwxyz" or 
                self.currentChar in "0123456789" or 
                self.currentChar == "_"):

                if (self.currentChar in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" or  # Uppercase not allowed
                    self.currentChar == "#" or 
                    not (len(result) < 15) or  # Limit to 15 characters
                    self.currentChar in delim24):
                    return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use {", ".join([repr(x) for x in delim24])}'

                result += self.currentChar
                self.next()

                if self.currentChar == '\0':
                    break

            if self.currentChar in delim24:
                self.IDcounter += 1
                return f"IDENTIFIER{self.IDcounter}", result
            else:
                return "Hey Agent! This Lexeme is Unknown", f'"{result}" Use {", ".join([repr(x) for x in delim24])}'

        else:
            return "Hey Agent! First letter must be lowercase or underscore", f'"{result}" Use "a" to "z" or "_"'



    def getNextTokens(self):
        counter = 0
        error = "Hey Agent! This Lexeme is Unknown"


        while True:
            if counter >= len(self.lexeme):
                break
            if '0' <= self.currentChar <= '9' or self.currentChar == ".":
                self.type_, self.value_ = self.digits()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar in "+-*/%":
                self.type_, self.value_ = self.operatorToken()
                if self.type_ in error:
                    print(f"DEBUG: lineCounter={self.lineCounter}, type_={self.type_}, value_={self.value_}")
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == 'a':
                self.type_, self.value_ = self.a_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == 'b':
                self.type_, self.value_ = self.b_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == 'c':
                self.type_, self.value_ = self.c_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == 'd':
                self.type_, self.value_ = self.d_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == 'f':
                self.type_, self.value_ = self.f_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == 'g':
                self.type_, self.value_ = self.g_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == 'i':
                self.type_, self.value_ = self.i_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == 'l':
                self.type_, self.value_ = self.l_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == 'n':
                self.type_, self.value_ = self.n_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == 'o':
                self.type_, self.value_ = self.o_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == 'p':
                self.type_, self.value_ = self.p_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == 'r':
                self.type_, self.value_ = self.r_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == 's':
                self.type_, self.value_ = self.s_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == 't':
                self.type_, self.value_ = self.t_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == 'w':
                self.type_, self.value_ = self.w_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == '#':
                self.type_, self.value_ = self.IdentifierToken()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == '`' or self.currentChar == '$':
                self.type_, self.value_ = self.comment_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar in "({[)}]~}-":
                self.type_, self.value_ = self.special_token()
                if self.type_ == "Hey Agent! This Lexeme is Unknown":
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == '"':
                self.type_, self.value_ = self.strikelit_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == "'":
                self.type_, self.value_ = self.chatlit_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif (self.currentChar == '<' or self.currentChar == '>' or self.currentChar == '!' or self.currentChar == '='):
                self.type_, self.value_ = self.rel_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == ',':
                self.type_, self.value_ = self.seperator_token()
                if self.type_ in error:
                    self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                else:
                    self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            elif self.currentChar == ' ':
                self.type_, self.value_ = self.SpaceToken()
                self.tokens.append(f'{self.type_} : {self.value_}')
                continue
            if self.currentChar == "\n":
                self.tokens.append(f'"NEWLINE" : "\\n"')
                self.lineCounter += 1
                self.next()
                continue
            if self.currentChar == "\t":
                self.tokens.append(f'"Tab" "\\t"')
                self.lineCounter += 1
                self.next()
                continue
            elif self.currentChar in unknownCharacters:
                self.type_, self.value_ = self.UnknownToken()
                self.tokensForUnknown.append(f'line #{self.lineCounter} : {self.type_} : {self.value_}')
                continue

            counter += 1

        return self.tokens  # Return the complete list of tokens


def main():
    while True:
        lexeme = input("Enter lexeme: ")
        lexer = DEDOSLexicalAnalyzer(lexeme)
        print("Token: Lexeme")
        lexer.getNextTokens()
        print(lexer.tokens)
        print(lexer.tokensForUnknown)
        if lexeme == "~":
            break


if __name__ == "__main__":
    main()
