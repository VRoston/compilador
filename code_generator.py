# code_generator.py
# Gerador de código para a MVD didática.
# Produz instruções em formato textual e grava em um arquivo .mvd

class CodeGenerator:
    def __init__(self, filename="output.mvd"):
        self.instructions = []
        self.label_counter = 0
        self.filename = filename

    # Helpers básicos
    def new_label(self):
        lbl = f"L{self.label_counter}"
        self.label_counter += 1
        return lbl

    def emit(self, instr):
        """Adiciona uma instrução (string)."""
        self.instructions.append(instr)

    def emit_label(self, label):
        """Adiciona uma label (formatada como: Lx  NULL)."""
        self.instructions.append(f"{label}  NULL")

    # Programa / memória
    def start_program(self):
        self.emit("START")

    def alloc(self, n):
        if n > 0:
            self.emit(f"ALLOC {n}")

    def daloc(self, n):
        if n > 0:
            self.emit(f"DALLOC {n}")

    def halt(self):
        self.emit("HLT")

    # Constantes / variáveis
    def ldc(self, value):
        # Load constant
        self.emit(f"LDC {value}")

    def ldv(self, addr_or_name):
        # Load variable at address
        # addr_or_name may be integer address or a name (the parser can pass address)
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
        self.emit("DIV")

    def and_(self):
        self.emit("AND")

    def or_(self):
        self.emit("OR")

    def not_(self):
        self.emit("NOT")

    # Comparisons (names from notes: CMA, CMEQ, etc.)
    def cmeq(self):
        self.emit("CMEQ")  # <= ? depends on naming; adapt if needed

    def cma(self):
        self.emit("CMA")   # >  (compare maior)
    def cme(self):
        self.emit("CME")   # <  (compare menor)

    def cmae(self):
        self.emit("CMAQ")  # >= (compare maior ou igual)

    def cmee(self):
        self.emit("CMEQ")  # <= (compare menor ou igual)

    def cmeq_eq(self):
        self.emit("CMEQ")  # <= / == vary by naming in VM

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
