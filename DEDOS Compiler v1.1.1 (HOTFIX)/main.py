import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from lexer import DEDOSLexicalAnalyzer
from Syntax import DEDOSParser  # Import your PLY-based parser
import Semantic

class LexerGUI:
    def __init__(self, master):
        self.master = master
        master.geometry("1280x800")
        master.title("DEDOS Compiler")  # Window title
        master.iconbitmap("counterstrikeconditionzero_11724.ico")  # Window icon
        master.resizable(False, False)
        # Configure grid layout for responsiveness
        master.grid_columnconfigure(0, weight=2, uniform="equal")
        master.grid_columnconfigure(1, weight=3, uniform="equal")
        master.grid_columnconfigure(2, weight=2, uniform="equal")
        master.grid_columnconfigure(3, weight=3, uniform="equal")
        master.grid_columnconfigure(4, weight=2, uniform="equal")
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=3)
        master.grid_rowconfigure(2, weight=2)
        master.grid_rowconfigure(3, weight=1)

        analyzer_button_frame = tk.Frame(master, bg="#3c3f59")
        analyzer_button_frame.grid(row=3, column=0, columnspan=5, padx=0, pady=10, sticky="ew")

        self.lexical_button = self.create_rounded_button(analyzer_button_frame, "Run Lexical Analyzer", self.analyze_code, "#fb5421", "white", ("Consolas", 10))
        self.lexical_button.pack(side=tk.LEFT, padx=5)

        self.syntax_button = self.create_rounded_button(analyzer_button_frame, "Run Syntax Analyzer", self.analyze_syntax, "#fb5421", "white", ("Consolas", 10))
        self.syntax_button.pack(side=tk.LEFT, padx=0)
        self.syntax_button.configure(state="disabled")

        self.semantic_button = self.create_rounded_button(analyzer_button_frame, "Run Semantic Analyzer", self.analyze_semantic, "#fb5421", "white", ("Consolas", 10))
        self.semantic_button.pack(side=tk.LEFT, padx=5)
        self.semantic_button.configure(state="disabled")

        # New Code Generation Button (disabled by default)
        self.codegen_button = self.create_rounded_button(analyzer_button_frame, "Generate Code", self.generate_code, "#fb5421", "white", ("Consolas", 10))
        self.codegen_button.pack(side=tk.LEFT, padx=5)
        self.codegen_button.configure(state="disabled")

        self.import_button = self.create_rounded_button(analyzer_button_frame, "Import File", self.import_file, "#fb5421", "white", ("Consolas", 10))
        self.import_button.pack(side=tk.LEFT, padx=5)

        self.export_button = self.create_rounded_button(analyzer_button_frame, "Export Results", self.export_file, "#fb5421", "white", ("Consolas", 10))
        self.export_button.pack(side=tk.LEFT, padx=5)

        self.help_button = self.create_rounded_button(analyzer_button_frame, "Help", self.show_help, "#fb5421", "white", ("Consolas", 10))
        self.help_button.pack(side=tk.LEFT, padx=5)

        # Input Code Frame (first instance)
        input_frame = tk.Frame(master, bg="#3c3f59")
        input_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=20, sticky="nsew")
        # (This instance will be overridden later by the final code input widget)
        self.code_input = scrolledtext.ScrolledText(input_frame, bg="#161527", fg="#fbb200",
                                                     insertbackground="#fbb200", font=("Consolas", 12))
        self.code_input.pack(fill=tk.BOTH, expand=True)

        # Error Output with scrollbar
        error_frame = tk.Frame(master, bg="#161527")
        error_frame.grid(row=2, column=0, columnspan=5, padx=6, pady=5, sticky="nsew")
        self.errors_list = tk.Listbox(error_frame, bg="#161527", fg="#fbb200", font=("Consolas", 10))
        scrollbar_errors = tk.Scrollbar(error_frame, orient=tk.VERTICAL, command=self.errors_list.yview)
        self.errors_list.config(yscrollcommand=scrollbar_errors.set)
        self.errors_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_errors.pack(side=tk.RIGHT, fill=tk.Y)

        # Tokens Panel with scrollbar
        tokens_frame = ttk.LabelFrame(master, text="Tokens")
        tokens_frame.grid(row=1, column=3, padx=0, pady=5, sticky="nsew")
        self.tokens_list = tk.Listbox(tokens_frame, width=40)
        scrollbar_tokens = tk.Scrollbar(tokens_frame, orient=tk.VERTICAL, command=self.tokens_list.yview)
        self.tokens_list.config(yscrollcommand=scrollbar_tokens.set)
        self.tokens_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar_tokens.pack(side=tk.RIGHT, fill=tk.Y)

        # Lexemes Panel with scrollbar
        lexemes_frame = ttk.LabelFrame(master, text="Lexemes")
        lexemes_frame.grid(row=1, column=4, padx=0, pady=5, sticky="nsew")
        self.lexemes_list = tk.Listbox(lexemes_frame, width=40)
        scrollbar_lexemes = tk.Scrollbar(lexemes_frame, orient=tk.VERTICAL, command=self.lexemes_list.yview)
        self.lexemes_list.config(yscrollcommand=scrollbar_lexemes.set)
        self.lexemes_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar_lexemes.pack(side=tk.RIGHT, fill=tk.Y)

        # Apply Dark Mode by Default
        self.apply_dark_mode()

        # Bind Ctrl+F to the find_text function and Esc to close the find bar
        self.master.bind("<Control-f>", self.show_find_bar)
        self.master.bind("<Escape>", self.hide_find_bar)
        self.master.bind("<Control-BackSpace>", self.handle_ctrl_backspace)
        # Find bar frame (hidden by default)
        self.find_frame = None

        # --- Input Frame with Line Numbers ---
        input_frame = tk.Frame(master, bg="#3c3f59")
        input_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")
        self.line_numbers = tk.Text(input_frame, width=4, padx=5, bg="#161527",
                                     fg="white", state="disabled", font=("Consolas", 13))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        # Create the final code input widget (this one will be used)
        self.code_input = scrolledtext.ScrolledText(input_frame, bg="#161527", fg="#fbb200",
                                                      insertbackground="#fbb200", font=("Consolas", 13))
        self.code_input.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Add status bar at the top
        self.status_frame = tk.Frame(master, bg="#2c2c2c", height=20)
        self.status_frame.grid(row=0, column=0, columnspan=5, sticky="ew", padx=0, pady=0)
        self.status_label = tk.Label(self.status_frame, text="Ready", bg="#2c2c2c", fg="#5cb85c", anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=10, pady=2)
        # Configure hover help for elements
        self.setup_hover_help()

        # Bind events to update line numbers and sync scrolling
        self.code_input.bind("<KeyRelease>", self.update_line_numbers)
        self.code_input.bind("<MouseWheel>", self.sync_scroll)
        self.code_input.bind("<Configure>", self.update_line_numbers)
        self.code_input.bind("<KeyRelease>", self.highlight_words, add="+")
        # Bind Tab key for inserting 4 spaces
        self.code_input.bind("<Tab>", self.handle_tab)
        


    def show_help(self):
        """Show help window with input field instructions"""
        help_text = """DEDOS Input Field Guide:
        
1. Basic Syntax:
- Use indentation (4 spaces) for code blocks
- start statements with ~ and end statements with ~
- Example:
    ~
    inst #x = 10
    plant(#x)
    ~

2. Shortcuts:
- Ctrl+F: Find text
- Tab: Insert 4 spaces
- Mouse hover: See element descriptions above

3. Special Symbols:
- ~ : Code of Block 
- +-*/ : Arithmetic operators
- () : Parameter grouping
- "" : String delimiters

4. Code Examples:
Variable declaration:
    inst ammo = 30 
Conditional statement:
    re(ammo < 10){
        plant("the ammo is greater than 10")
    }
    reload{
        plant("The ammo is less than 10")
    }
Function call:
    defuse bomb_siteb(){
    }"""
        
        help_window = tk.Toplevel(self.master)
        help_window.title("Input Field Help")
        help_window.geometry("600x400")
        
        text_area = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, font=("Consolas", 11))
        text_area.insert(tk.INSERT, help_text)
        text_area.configure(state='disabled', bg="#161527", fg="#fbb200")
        text_area.pack(fill=tk.BOTH, expand=True)

    def setup_hover_help(self):
        """Configure hover help messages for UI elements"""
        hover_help = {
            self.code_input: "Enter your DEDOS code here | Use Ctrl+F to find text | Tab for 4 spaces",
            self.tokens_list: "Displays identified tokens from lexical analysis",
            self.lexemes_list: "Shows corresponding lexeme values for tokens",
            self.errors_list: "Displays compilation errors and warnings",
            self.syntax_button: "Check code structure and syntax rules compliance",
            self.lexical_button: "Analyze code for valid tokens and lexemes",
            self.semantic_button: "Verify semantic rules and type checking",
            self.import_button: "Import code from .dedos files",
            self.export_button: "Export code and analysis results",
            self.codegen_button: "Generate target code from the analyzed input"
        }

        for widget, message in hover_help.items():
            self.add_hover_help(widget, message)

    def add_hover_help(self, widget, message):
        """Add hover help functionality to a widget"""
        widget.bind("<Enter>", lambda e, m=message: self.status_label.config(text=m))
        widget.bind("<Leave>", lambda e: self.status_label.config(text="Ready"))
        
    def handle_tab(self, event):
        """Insert 4 spaces when Tab is pressed"""
        event.widget.insert(tk.INSERT, "    ")  # 4 spaces
        return "break"  # Prevents default Tab behavior
        
    def highlight_words(self, event=None):
        """Highlight multiple groups of words in different colors."""
        highlight_groups = {
            "group1": (["defuse", "in", "not"], "#F93827"),
            "group2": (["inst", "flank", "chat", "strike", "tool"], "#5cffe4"),
            "group3": (["abort", "back", "push", "perim"], "#aeac95"),
            "group4": (["plant", "info"], "#FFD65A"),
            "group5": (["re", "reload", "load"], "#ff1377"),
            "group6": (["force"], "#F3CFC6"),
            "group7": (["+", "-", "/", "*", "="], "#ffffff"),
            "group8": ("numbers", "#d6fa51"),  # Special handling for numbers
            "group9": (["~"], "#16C47F"),
            "group10": (["(", ")", "[", "{", "}", "]"], "white"),
            "group11": ("quoted_text", "#FFEB00"),  # Color for text inside quotes
            "group12": ("comment", "#A9A9A9")  # Color for text inside comments
        }

        # Remove old highlights and set colors
        for tag, (words, color) in highlight_groups.items():
            self.code_input.tag_remove(tag, "1.0", tk.END)
            self.code_input.tag_config(tag, foreground=color)

            if words == "numbers":
                # Special handling for full numbers
                start_pos = "1.0"
                while True:
                    start_pos = self.code_input.search("0", start_pos, stopindex=tk.END)
                    if not start_pos:
                        break
                    # Expand to capture the full number Sequence
                    end_pos = start_pos
                    while True:
                        next_char = self.code_input.get(end_pos)
                        if not next_char.isdigit():
                            break
                        end_pos = f"{end_pos}+1c"
                    before = self.code_input.get(f"{start_pos}-1c", start_pos)
                    after = self.code_input.get(end_pos, f"{end_pos}+1c")
                    if (before.isspace() or before in "{}[]();.,") and (after.isspace() or after in "{}[]();.,"):
                        self.code_input.tag_add(tag, start_pos, end_pos)
                    start_pos = end_pos

            elif words == "quoted_text":
                # Search for text inside quotes (single and double)
                for quote in ["'", '"']:
                    start_pos = "1.0"
                    while True:
                        start_pos = self.code_input.search(quote, start_pos, stopindex=tk.END)
                        if not start_pos:
                            break
                        end_pos = f"{start_pos}+1c"
                        while True:
                            next_char = self.code_input.get(end_pos)
                            if next_char == quote:
                                end_pos = f"{end_pos}+1c"
                                break
                            elif next_char == "":
                                break
                            end_pos = f"{end_pos}+1c"
                        self.code_input.tag_add(tag, start_pos, end_pos)
                        start_pos = end_pos
                        
            elif words == "comment":
                # Search for text inside comments marked with '$'
                for quote in ["$"]:
                    start_pos = "1.0"
                    while True:
                        start_pos = self.code_input.search(quote, start_pos, stopindex=tk.END)
                        if not start_pos:
                            break
                        end_pos = f"{start_pos}+1c"
                        while True:
                            next_char = self.code_input.get(end_pos)
                            if next_char == quote:
                                end_pos = f"{end_pos}+1c"
                                break
                            elif next_char == "":
                                break
                            end_pos = f"{end_pos}+1c"
                        self.code_input.tag_add(tag, start_pos, end_pos)
                        start_pos = end_pos
            else:
                # Standard word highlighting
                for word in words:
                    start_pos = "1.0"
                    while True:
                        start_pos = self.code_input.search(word, start_pos, stopindex=tk.END)
                        if not start_pos:
                            break
                        before = self.code_input.get(f"{start_pos}-1c", start_pos)
                        after = self.code_input.get(f"{start_pos}+{len(word)}c", f"{start_pos}+{len(word) + 1}c")
                        if (before.isspace() or before in "{}[]();.,") and (after.isspace() or after in "{}[]();.,"):
                            end_pos = f"{start_pos}+{len(word)}c"
                            self.code_input.tag_add(tag, start_pos, end_pos)
                        start_pos = f"{start_pos}+{len(word)}c"

    def create_rounded_button(self, parent, text, command, bg, fg, font):
        """Creates a rounded button with a hover effect."""
        button = tk.Button(
            parent,
            text=text,
            bg=bg,
            fg=fg,
            font=font,
            command=command,
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=12,
            highlightthickness=0,
            bd=0,
            activebackground=bg,
            activeforeground=fg
        )
        button.config(
            highlightthickness=0,
            relief="solid",
        )
        def on_enter(e):
            button.config(bg="#303358", fg="#fbb200")
        def on_leave(e):
            button.config(bg=bg, fg=fg)
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        return button

    def update_line_numbers(self, event=None):
        """Update line numbers dynamically."""
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        line_count = self.code_input.get("1.0", tk.END).count("\n")
        line_numbers_str = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert("1.0", line_numbers_str)
        self.line_numbers.config(state="disabled")

    def sync_scroll(self, event):
        """Sync scrolling between code input and line numbers."""
        self.line_numbers.yview_moveto(self.code_input.yview()[0])

    def apply_dark_mode(self):
        """Apply dark mode theme."""
        self.master.config(bg="#3c3f59")
        self.code_input.config(bg="#161527", fg="#fbb200", insertbackground="#fbb200")
        self.errors_list.config(bg="#161527", fg="#fbb200")
        self.tokens_list.config(bg="#161527", fg="#fbb200")
        self.lexemes_list.config(bg="#161527", fg="#fbb200")

    def show_find_bar(self, event=None):
        """Display the find bar at the top like in VS Code."""
        if self.find_frame and self.find_frame.winfo_exists():
            self.find_entry.focus_set()
            return
        self.find_frame = tk.Frame(self.master, bg="#2c2c2c")
        self.find_frame.grid(row=0, column=0, columnspan=5, sticky="ew", padx=5, pady=5)
        label = tk.Label(self.find_frame, text="Find:", bg="#2c2c2c", fg="white", font=("Consolas", 12))
        label.pack(side=tk.LEFT, padx=5, pady=5)
        self.find_entry = tk.Entry(self.find_frame, font=("Consolas", 12))
        self.find_entry.pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.X)
        search_button = tk.Button(self.find_frame, text="Find", command=self.find_text)
        search_button.pack(side=tk.LEFT, padx=5, pady=5)
        close_button = tk.Button(self.find_frame, text="X", command=self.hide_find_bar)
        close_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.find_entry.bind("<Return>", lambda e: self.find_text())
        self.find_entry.focus_set()

    def hide_find_bar(self, event=None):
        """Close the find bar."""
        if self.find_frame and self.find_frame.winfo_exists():
            self.find_frame.destroy()

    def find_text(self):
        """Find text in the input field."""
        search_text = self.find_entry.get()
        if not search_text:
            return
        self.code_input.tag_remove("highlight", "1.0", tk.END)
        start_pos = '1.0'
        while True:
            start_pos = self.code_input.search(search_text, start_pos, stopindex=tk.END, nocase=True)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(search_text)}c"
            self.code_input.tag_add("highlight", start_pos, end_pos)
            start_pos = end_pos
        self.code_input.tag_config("highlight", background="yellow", foreground="black")
        
    def analyze_code(self):
        """Run Lexical Analysis"""
        self.tokens_list.delete(0, tk.END)
        self.lexemes_list.delete(0, tk.END)
        self.errors_list.delete(0, tk.END)
        code = self.code_input.get("1.0", tk.END).strip()
        if not code:
            self.errors_list.delete(0, tk.END)
            self.errors_list.insert(tk.END, "Error: Please enter some code to analyze!")
            return

        self.lexer = DEDOSLexicalAnalyzer(code)
        self.lexer.getNextTokens()
        current_line = 1
        for token in self.lexer.tokens:
            if " : " in token:
                token_type, lexeme_value = token.split(" : ", 1)
                self.tokens_list.insert(tk.END, f"{current_line}. {token_type}")
                self.lexemes_list.insert(tk.END, f"{current_line}. {lexeme_value}")
            else:
                self.tokens_list.insert(tk.END, f"{current_line}. {token}")
                self.lexemes_list.insert(tk.END, f"{current_line}. {token}")
            if " : " in token:
                if "\n" in lexeme_value:
                    current_line += lexeme_value.count("\n")
                else:
                    current_line += 1
            else:
                current_line += 1

        if self.lexer.tokensForUnknown:
            for error in self.lexer.tokensForUnknown:
                self.errors_list.insert(tk.END, f" 💥 {error}")
            self.syntax_button.configure(state="disabled")
        else:
            self.errors_list.insert(tk.END, "-" * 180)
            self.errors_list.insert(tk.END, "----------------------------------------------------------------------LEXICAL COMPILE SUCCESSFULLY AGENT!---------------------------------------------------------------------------")
            self.errors_list.insert(tk.END, "-" * 180)
            self.syntax_button.configure(state="normal")

    def handle_ctrl_backspace(self, event):
        # Get the current insertion index
        current_index = self.code_input.index("insert")
        # Get the start index of the current line
        line_start = self.code_input.index("insert linestart")
        # Retrieve the text from the beginning of the line to the current insertion point
        text_before = self.code_input.get(line_start, current_index)
        
        # Remove trailing spaces in case the cursor is after spaces
        stripped_text = text_before.rstrip()
        if not stripped_text:
            # Nothing to delete on this line, so let the default behavior occur
            return "break"
        
        # Calculate how many characters to delete:
        # Find the last space character in the stripped text. If none is found, delete from the beginning of the line.
        last_space = stripped_text.rfind(" ")
        if last_space == -1:
            delete_start = line_start
        else:
            # +1 to delete the space as well, so start from the character right after the last space.
            delete_start = f"{line_start}+{last_space + 1}c"
        
        # Delete from the calculated starting position to the current insertion point.
        self.code_input.delete(delete_start, current_index)
        
        return "break"  # Prevent any default behavior
    
    def analyze_syntax(self):
        """Run Syntax Analysis"""
        self.errors_list.delete(0, tk.END)
        # Create the parser instance using tokens from the lexer.
        print("Tokens received for syntax analysis:", self.lexer.tokens)  # Debugging
        self.parser = DEDOSParser(self.lexer.tokens)
        self.parser.ListToDict()
        
        # Try to run the parser. If an IndexError occurs, capture and log the error location using a line counter.
        try:
            self.parser.GetNextTerminal()
        except IndexError as e:
            # Compute the current line number by iterating over tokens up to the error position
            line_counter = 1
            for idx in range(self.parser.position):
                token = self.lexer.tokens[idx]
                if " : " in token:
                    # The token is expected to be in the form "TOKEN_TYPE : lexeme_value"
                    _, lexeme_value = token.split(" : ", 1)
                    if "\n" in lexeme_value:
                        # Increase by the number of newline characters encountered in the lexeme
                        line_counter += lexeme_value.count("\n")
                    else:
                        # Otherwise, assume the token occupies one line
                        line_counter += 1
                else:
                    line_counter += 1

            # Since we don't compute column reliably with this counter, we'll leave it as "unknown"
            column = "unknown"
            error_message = f"Syntax Error at line {line_counter}, column {column}: {str(e)}"
            # Append the error as a tuple (message, line, column)
            self.parser.SyntaxErrors.append((error_message, line_counter, column))
            print(error_message)
        
        syntaxErrors = self.parser.SyntaxErrors
        print("Raw Syntax Errors:", syntaxErrors)  # Debugging

        # Display only the nearest (first) syntax error in the GUI
        if syntaxErrors:
            nearest_error = syntaxErrors[0]
            if isinstance(nearest_error, tuple) and len(nearest_error) == 3:
                error_message, line, column = nearest_error
                formatted_error = f"Syntax Error at line {line}, column {column}: {error_message}"
            else:
                formatted_error = str(nearest_error)
            self.errors_list.insert(tk.END, formatted_error)
            print(formatted_error)  # Print the nearest error with location
            # Disable semantic analysis button if there is an error
            self.semantic_button.configure(state="disabled")
        else:
            # If no error, enable the semantic analysis button and run semantic analysis.
            print("Syntax analysis succeeded, enabling semantic analysis.")
            self.semantic_button.configure(state="normal")
            self.analyze_semantic()

        # Clear syntax errors for subsequent runs.
        self.parser.SyntaxErrors = []




    def enteringErrorsOfSyntax(self, syntaxErrors):
        # For a Listbox widget, use numeric indices.
        self.errors_list.delete(0, tk.END)
        for err in syntaxErrors:
            self.errors_list.insert(tk.END, err)

    def analyze_semantic(self):
        # Check if the parser and its outputs are available.
        if not hasattr(self, 'parser') or not self.parser:
            self.errors_list.delete(0, tk.END)
            self.errors_list.insert(tk.END, "Syntax analysis has not been run yet.")
            return

        if self.parser.SyntaxErrors:
            print("Syntax Errors:", self.parser.SyntaxErrors)  # Debugging
            return

        Terminals = getattr(self.parser, 'Terminals', [])
        Sequence = getattr(self.parser, 'SemanticSequence', None) or getattr(self.parser, 'Sequence', []) or Terminals

        if not Terminals or not Sequence:
            self.errors_list.delete(0, tk.END)
            self.errors_list.insert(tk.END, "Required syntax analysis outputs are missing!")
            return

        print("Running Semantic Analysis with Terminals:", Terminals)
        print("Running Semantic Analysis with Sequence:", Sequence)

        # Create the semantic analyzer instance.
        sem = Semantic.DEDOSSemantic(Terminals, Sequence)
        
        # Run semantic processing.
        sem.keyval_fix()
        sem.token_type()
        
        # Ensure output is a list
        output = sem.Output if sem.Output is not None else []
        
        # Retrieve only unique errors
        errors = list(dict.fromkeys([
            item.replace("|||", "") for item in output
            if isinstance(item, str) and ('|||Semantic Error' in item or '|||Runtime Error' in item)
        ]))

        # Clear previous output
        self.errors_list.delete(0, tk.END)
        
        # Display errors if found, else show success message and enable code generation.
        if errors:
            for line in errors:
                # Attempt to convert the line to a float and format if possible;
                # if conversion fails, show the original line.
                try:
                    num = float(line)
                    formatted_line = f"{num:.5f}"
                except ValueError:
                    formatted_line = line
                self.errors_list.insert(tk.END, formatted_line)
            # Disable the Generate Code button if errors are present.
            self.codegen_button.configure(state="disabled")
        else:
            self.errors_list.insert(tk.END, "-------------------------------------------------------------SEMANTIC COMPILE SUCCESSFUL\n-------------------------------------------------------------")
            # Enable the Generate Code button when semantic analysis is successful.
            self.codegen_button.configure(state="normal")

    def generate_code(self):
        """Generate target code by running semantic analysis and print the output in the error output box.
        If semantic errors are found, disable the Generate Code button."""
        # Check if the parser and its outputs are available.
        if not hasattr(self, 'parser') or not self.parser:
            self.errors_list.delete(0, tk.END)
            self.errors_list.insert(tk.END, "Syntax analysis has not been run yet.")
            return

        if self.parser.SyntaxErrors:
            print("Syntax Errors:", self.parser.SyntaxErrors)  # Debugging
            return

        Terminals = getattr(self.parser, 'Terminals', [])
        Sequence = getattr(self.parser, 'SemanticSequence', None) or getattr(self.parser, 'Sequence', []) or Terminals

        if not Terminals or not Sequence:
            self.errors_list.delete(0, tk.END)
            self.errors_list.insert(tk.END, "Required syntax analysis outputs are missing!")
            return

        print("Running Semantic Analysis with Terminals:", Terminals)
        print("Running Semantic Analysis with Sequence:", Sequence)

        # Create the semantic analyzer instance.
        sem = Semantic.DEDOSSemantic(Terminals, Sequence)

        # Run semantic processing.
        sem.keyval_fix()
        sem.token_type()

        # Retrieve output from the semantic analyzer.
        output = sem.Output

        # --- Filtering step ---
        # If output is a list, remove all occurrences of "(" from each element.
        if output:
            if isinstance(output, list):
                filtered_output = []
                for item in output:
                    if isinstance(item, str):
                        # Remove any '(' characters from the string
                        new_item = item.replace('(', '')
                        # Optionally, if you want to completely discard lines that are only '(':
                        if new_item.strip() != "":
                            filtered_output.append(new_item)
                    else:
                        filtered_output.append(item)
                output = filtered_output
            elif isinstance(output, str):
                # Remove any '(' in a string output.
                output = output.replace('(', '')

        # Print the final (filtered) output in the error output box.
        self.errors_list.delete(0, tk.END)
        errors_found = False
        if output:
            if isinstance(output, list):
                for line in output:
                    try:
                        num = float(line)
                        formatted_line = f"{num:.5f}"
                    except ValueError:
                        formatted_line = line
                    self.errors_list.insert(tk.END, formatted_line)
                    if ("Semantic Error" in line) or ("Runtime Error" in line):
                        errors_found = True
            else:
                try:
                    num = float(output)
                    formatted_output = f"{num:.5f}"
                except ValueError:
                    formatted_output = output
                self.errors_list.insert(tk.END, formatted_output)
                if ("Semantic Error" in output) or ("Runtime Error" in output):
                    errors_found = True
        else:
            self.errors_list.insert(tk.END, "No output generated.")

        # Disable the Generate Code button if errors are found.
        if errors_found:
            self.codegen_button.configure(state="disabled")

    def import_file(self):
        """Open a file dialog to import a code file."""
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.dedos"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                code = file.read()
                self.code_input.delete(1.0, tk.END)
                self.code_input.insert(tk.END, code)

    def export_file(self):
        """Export the code from the input box to a text file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".dedos", 
            filetypes=[("Text Files", "*.dedos"), ("All Files", "*.*")]
        )
        if file_path:
            code = self.code_input.get("1.0", tk.END)
            with open(file_path, "w") as file:
                file.write(code)

def inputter(desc):
    if desc.startswith("("):
        desc = desc[1:]
    
    # Create a new Toplevel window for input
    top = tk.Toplevel()
    top.title("Input")
    top.configure(bg="#3c3f59")

    # Label for the description with specified font and color
    tk.Label(top, text=desc, font=("Consolas", 14), bg="#3c3f59", fg="#fbb200",
             anchor='w', justify='left').pack(pady=10)
    
    # Entry widget for user input with specified font and color
    entry = tk.Entry(top, font=("Consolas", 12), width=40, bg="#3c3f59", fg="#fbb200",
                     insertbackground="#fbb200")
    entry.pack(padx=20, pady=10)
    entry.focus_set()
    value = None

    def submit():
        nonlocal value
        # Capture the entry value (the replace is left as in the original)
        value = str(entry.get()).replace("-", "-")
        top.destroy()  # Close the input window

    # Submit button with specified design
    tk.Button(top, text="Submit", command=submit, font=("Consolas", 12),
              bg="#fb5421", fg="#fbb200", padx=20, pady=5, relief="flat", borderwidth=0).pack(pady=10)
    
    top.wait_window()  # Wait for the input window to close
    try:
        if value in [True, False]:
            pass
        elif type(eval(value)) == int:
            pass
        elif type(eval(value)) == float:
            pass
    except:
        value = "\"" + value + "\""
    return value

def main():
    root = tk.Tk()
    app = LexerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
