def load_program(file_path):
    """
    Load a program from a specified file and parse its instructions.

    Args:
        file_path (str): The path to the program file.

    Returns:
        list: A list of parsed instructions.
    """
    program = []
    label_map = {}
    mnemonics = {
        "START", "HLT", "NULL", "LDC", "LDV", "STR", "ALLOC", "DALLOC",
        "ADD", "SUB", "MULT", "DIVI", "INV",
        "AND", "OR", "NEG", "CME", "CMA", "CEQ", "CDIF", "CMEQ", "CMAQ",
        "JMP", "JMPF", "CALL", "RETURN", "RD", "PRN"
    }

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            if ';' in line:
                line = line.split(';', 1)[0].strip()
                if not line:
                    continue
            parts = line.split()
            first = parts[0]
            label_token = None
            if first.endswith(':'):
                label_token = first[:-1]
                parts = parts[1:]
            elif first.upper() not in mnemonics:
                label_token = first
                parts = parts[1:]
            if label_token is not None:
                label_map[label_token] = len(program)
            if not parts:
                continue
            mnemonic = parts[0].upper()
            args = parts[1:] + [None, None]
            program.append((mnemonic, args[0], args[1]))

    return program, label_map