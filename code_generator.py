# code_generator.py
# Gerador de código para a MVD didática.
# Mantém toda a lógica original, mas adiciona indentação visual no arquivo .mvd

class CodeGenerator:
    def __init__(self, filename="output.mvd"):
        self.instructions = []
        self.label_counter = 0
        self.filename = filename
        self.indent = " " * 4  # 4 espaços de indentação

    # Helpers básicos
    def new_label(self):
        lbl = f"L{self.label_counter}"
        self.label_counter += 1
        return lbl

    def emit(self, instr, indent=True):
        """Adiciona uma instrução com indentação padrão (exceto rótulos)."""
        if indent:
            self.instructions.append(f"{self.indent}{instr}")
        else:
            self.instructions.append(instr)

    def emit_label(self, label):
        """Adiciona um rótulo (sem indentação)."""
        self.emit(f"{label}  NULL", indent=False)

    # Programa / memória
    def start_program(self):
        self.emit("START", indent=False)

    def alloc(self, n):
        if n > 0:
            self.emit(f"ALLOC {n}")

    def daloc(self, n):
        if n > 0:
            self.emit(f"DALLOC {n}")

    def halt(self):
        self.emit("HLT", indent=False)

    # Constantes / variáveis
    def ldc(self, value):
        self.emit(f"LDC {value}")

    def ldv(self, addr_or_name):
        self.emit(f"LDV {addr_or_name}")

    def str_(self, addr_or_name):
        self.emit(f"STR {addr_or_name}")

    # I/O
    def rd(self):
        self.emit("RD")

    def prn(self):
        self.emit("PRN")

    # Arithmetic / logical
    def add(self):
        self.emit("ADD")

    def sub(self):
        self.emit("SUB")

    def mult(self):
        self.emit("MULT")

    def div(self):
        self.emit("DIVI")  # mantém compatível com sua MVD atual

    def and_(self):
        self.emit("AND")

    def or_(self):
        self.emit("OR")

    def not_(self):
        self.emit("NOT")

    # Comparisons
    def cma(self):
        self.emit("CMA")   # >
    def cme(self):
        self.emit("CME")   # <
    def cmae(self):
        self.emit("CMAE")  # >=
    def cmee(self):
        self.emit("CMEE")  # <=
    def cmeq_eq(self):
        self.emit("CMEQ")  # ==
    def cmdif(self):
        self.emit("CMDIF") # !=

    # Jumps
    def jmp(self, label):
        self.emit(f"JMP {label}")

    def jmpf(self, label):
        self.emit(f"JMPF {label}")

    # Label emission convenience for user
    def place_label(self, label):
        self.emit_label(label)

    # Save file
    def write_file(self):
        with open(self.filename, "w") as f:
            for instr in self.instructions:
                f.write(instr + "\n")
