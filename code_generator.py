# file to create code generation logic
import os

class Gera:
    def __init__(self, filename="output.obj"):
        self.instructions = []
        self.label_counter = 0
        # aceita caminho completo ou apenas nome; garante extensão .obj
        if not filename.endswith('.obj'):
            filename = f"{filename}.obj"
        self.filename = filename
        self.indent = " " * 4  # 4 espaços de indentação

    def __call__(self, label, instr, end1, end2):
        label = str(label)
        instr = str(instr)
        end1 = str(end1)
        end2 = str(end2)

        if label == "":
            self.instructions.append(f"{self.indent}{instr} {end1} {end2}")
        else:
            self.instructions.append(f"{label}{(4 - len(label)) * ' '}{instr} {end1} {end2}")

    def escreve(self):
        # garante que a pasta de destino exista
        dirname = os.path.dirname(self.filename)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(self.filename, "w") as f:
            for instr in self.instructions:
                f.write(instr + "\n")