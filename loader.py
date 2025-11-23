def load_program(file_path):
    """
    Load a program from a specified file and parse its instructions.

    Args:
        file_path (str): The path to the program file.

    Returns:
        list: A list of parsed instructions.
    """
    program = []                # Lista final de instruções já parseadas
    label_map = {}              # Mapa: nome_do_rotulo -> índice da instrução
    mnemonics = {               # Conjunto de instruções válidas reconhecidas pela MVD
        "START", "HLT", "NULL", "LDC", "LDV", "STR", "ALLOC", "DALLOC",
        "ADD", "SUB", "MULT", "DIVI", "INV",
        "AND", "OR", "NEG", "CME", "CMA", "CEQ", "CDIF", "CMEQ", "CMAQ",
        "JMP", "JMPF", "CALL", "RETURN", "RD", "PRN"
    }

    with open(file_path, 'r') as f:                     # Abre o arquivo .obj para leitura
        for line in f:                                  # Percorre cada linha
            line = line.strip()                         # Remove espaços extras
            if not line or line.startswith(';'):        # Ignora linha vazia ou comentário
                continue
            if ';' in line:                             # Remove comentários no fim da linha
                line = line.split(';', 1)[0].strip()
                if not line:
                    continue
            parts = line.split()                        # Quebra linha em tokens
            first = parts[0]                            # Primeiro token pode ser rótulo ou instrução
            label_token = None
            if first.endswith(':'):                     # Caso 1: rótulo com dois pontos (Ex: L1:)
                label_token = first[:-1]                # Salva sem ':'
                parts = parts[1:]                       # Remove rótulo da linha
            elif first.upper() not in mnemonics:        # Caso 2: rótulo sem ':'
                label_token = first                     # Ex: L1  START
                parts = parts[1:]
            if label_token is not None:                 # Se houve rótulo
                label_map[label_token] = len(program)   # Mapeia para índice atual
            if not parts:                               # Linha só tinha rótulo
                continue
            mnemonic = parts[0].upper()                 # Nome da instrução
            args = parts[1:] + [None, None]             # Sempre deixa 2 argumentos (padrão)
            program.append((mnemonic, args[0], args[1]))# Guarda instrução final

    return program, label_map                           # Retorna lista de instruções e mapa de rótulos