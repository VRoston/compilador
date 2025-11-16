# file to create code generation logic
class Gera:
    def __init__(self, filename="output.obj"):
        self.instructions = []
        self.label_counter = 0
        self.filename = f'./output/{filename}.obj'
        self.indent = " " * 4  # 4 espaços de indentação

    def __call__(self, label, instr, end1, end2):
        label = str(label)
        instr = str(instr)
        end1 = str(end1)
        end2 = str(end2)

        if label == "":
            self.instructions.append(f"{self.indent}{instr} {end1} {end2}")
        else:
            self.instructions.append(f"{label}{(4 - len(label)) * " "}{instr} {end1} {end2}")

    def escreve(self):
        with open(self.filename, "w") as f:
            for instr in self.instructions:
                f.write(instr + "\n")