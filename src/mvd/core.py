class MVD:
    """
    Implementação da Máquina Virtual Didática (MVD) em Python,
    adaptada para ser controlada por uma interface gráfica.
    """
    
    def __init__(self, tamanho_memoria=5000):
        self.P = []
        self.M_size = tamanho_memoria
        self.M = [0] * self.M_size
        self.mapa_rotulos = {}
        self.labels_by_index = []   # <-- novo: rótulos por instrução
        self.debug = True
        
        self.i = 0
        self.s = -1
        self.running = False
        self.aguardando_input = False
        self.proxima_inst_apos_input = 0

    def resetar(self):
        """ Limpa a memória e os registradores para uma nova execução. """
        self.M = [0] * self.M_size
        self.i = 0
        self.s = -1
        self.running = False
        self.aguardando_input = False
        self.labels_by_index = []   # <-- resetar também os rótulos

    def _parse_argumento(self, arg, mnemonico=None):
        if arg is None:
            return None
        arg_str = str(arg).strip()
        if arg_str == "" or arg_str.upper() in ("NULL", "NONE", "-"):
            return None
        if mnemonico in ("JMP", "JMPF", "CALL") and arg_str in self.mapa_rotulos:
            return self.mapa_rotulos[arg_str]
        try:
            return int(arg_str)
        except ValueError:
            if arg_str in self.mapa_rotulos:
                return self.mapa_rotulos[arg_str]
            raise ValueError(f"Erro: Rótulo desconhecido ou argumento inválido '{arg_str}'")

    def carregar_programa(self, nome_arquivo):
        self.P = []
        self.mapa_rotulos = {}
        self.labels_by_index = []
        
        programa_temp = []
        temp_label_map = {}  # índice -> lista de rótulos
        MNEMONICOS = {
            "START","HLT","NULL","LDC","LDV","STR","ALLOC","DALLOC",
            "ADD","SUB","MULT","DIVI","INV",
            "AND","OR","NEG","CME","CMA","CEQ","CDIF","CMEQ","CMAQ",
            "JMP","JMPF","CALL","RETURN","RD","PRN"
        }
        with open(nome_arquivo, 'r') as f:
            for linha in f:
                linha = linha.strip()
                if not linha or linha.startswith(';'):
                    continue
                if ';' in linha:
                    linha = linha.split(';', 1)[0].strip()
                    if not linha:
                        continue
                partes = linha.split()
                first = partes[0]
                rotulo_token = None
                if first.endswith(':'):
                    rotulo_token = first[:-1]
                    partes = partes[1:]
                elif first.upper() not in MNEMONICOS:
                    rotulo_token = first
                    partes = partes[1:]
                if rotulo_token is not None:
                    # marca o índice atual do programa_temp com o rótulo
                    temp_label_map.setdefault(len(programa_temp), []).append(rotulo_token)
                    # mantém mapa de rótulos para resolução de argumentos (compatível com antes)
                    self.mapa_rotulos[rotulo_token] = len(programa_temp)
                if not partes:
                    continue
                mnemonico = partes[0].upper()
                args = partes[1:] + [None, None]
                programa_temp.append((mnemonico, args[0], args[1]))

        # constrói labels_by_index alinhado com programa_temp
        self.labels_by_index = [None] * len(programa_temp)
        for idx, labels in temp_label_map.items():
            self.labels_by_index[idx] = ",".join(labels)

        for mnemonico, arg1_str, arg2_str in programa_temp:
            arg1 = self._parse_argumento(arg1_str, mnemonico)
            arg2 = self._parse_argumento(arg2_str, mnemonico)
            self.P.append((mnemonico, arg1, arg2))

        self.running = True

    def _ensure_capacity(self, idx):
        if idx < len(self.M):
            return
        extra = idx - len(self.M) + 1024
        self.M.extend([0] * extra)

    def fornecer_entrada(self, valor_str):
        if not self.aguardando_input:
            return

        try:
            valor_lido = int(valor_str)
        except ValueError:
            valor_lido = 0
            
        self.s += 1
        self._ensure_capacity(self.s)
        self.M[self.s] = valor_lido
        
        self.aguardando_input = False
        self.running = True
        self.i = self.proxima_inst_apos_input

    def executar_passo(self):
        if not self.running or self.i >= len(self.P) or self.aguardando_input:
            if not self.running:
                return ("HALTED", None)
            if self.aguardando_input:
                return ("NEED_INPUT", None)
            self.running = False
            return ("HALTED", None)

        instrucao, arg1, arg2 = self.P[self.i]
        proxima_inst = self.i + 1
        
        status_retorno = ("RUNNING", None)

        try:
            if instrucao == "START":
                self.s = -1
            
            elif instrucao == "HLT":
                self.running = False
                status_retorno = ("HALTED", None)
            
            elif instrucao == "NULL":
                pass

            elif instrucao == "LDC":
                self.s += 1
                self._ensure_capacity(self.s)
                self.M[self.s] = arg1
            
            elif instrucao == "LDV":
                self.s += 1
                self._ensure_capacity(self.s)
                if arg1 >= len(self.M) or arg1 < 0:
                    raise IndexError(f"LDV: Endereço inválido M[{arg1}]")
                self.M[self.s] = self.M[arg1]
            
            elif instrucao == "STR":
                if arg1 >= len(self.M) or arg1 < 0:
                    raise IndexError(f"STR: Endereço inválido M[{arg1}]")
                self.M[arg1] = self.M[self.s]
                self.s -= 1
            
            elif instrucao == "ALLOC":
                m = arg1 if arg1 is not None else 0
                n = arg2 if arg2 is not None else 0
                if n < 0 or m < 0:
                    raise ValueError(f"ALLOC: Argumentos negativos m={m}, n={n}")
                if m + n > len(self.M):
                    self._ensure_capacity(m + n - 1)
                
                src = self.M[m : m + n]
                self._ensure_capacity(self.s + n)
                for val in src:
                    self.s += 1
                    self.M[self.s] = val
            
            elif instrucao == "DALLOC":
                m = arg1 if arg1 is not None else 0
                n = arg2 if arg2 is not None else 0
                if n < 0 or m < 0:
                    raise ValueError(f"DALLOC: Argumentos negativos m={m}, n={n}")
                if self.s - (n - 1) < 0:
                    raise ValueError("DALLOC: underflow de pilha")
                if m + n > len(self.M):
                    self._ensure_capacity(m + n - 1)

                vals = []
                for _ in range(n):
                    vals.append(self.M[self.s])
                    self.s -= 1
                vals.reverse()
                for k, v in enumerate(vals):
                    self.M[m + k] = v
            
            elif instrucao == "ADD":
                self.M[self.s - 1] = self.M[self.s - 1] + self.M[self.s]
                self.s -= 1
            elif instrucao == "SUB":
                self.M[self.s - 1] = self.M[self.s - 1] - self.M[self.s]
                self.s -= 1
            elif instrucao == "MULT":
                self.M[self.s - 1] = self.M[self.s - 1] * self.M[self.s]
                self.s -= 1
            elif instrucao == "DIVI":
                if self.M[self.s] == 0:
                    raise ZeroDivisionError("Divisão por zero")
                self.M[self.s - 1] = int(self.M[self.s - 1] / self.M[self.s])
                self.s -= 1
            elif instrucao == "INV":
                self.M[self.s] = -self.M[self.s]
            
            elif instrucao == "AND":
                self.M[self.s - 1] = 1 if (self.M[self.s - 1] == 1 and self.M[self.s] == 1) else 0
                self.s -= 1
            elif instrucao == "OR":
                self.M[self.s - 1] = 1 if (self.M[self.s - 1] == 1 or self.M[self.s] == 1) else 0
                self.s -= 1
            elif instrucao == "NEG":
                self.M[self.s] = 1 - self.M[self.s]
            elif instrucao == "CME":
                self.M[self.s - 1] = 1 if self.M[self.s - 1] < self.M[self.s] else 0
                self.s -= 1
            elif instrucao == "CMA":
                self.M[self.s - 1] = 1 if self.M[self.s - 1] > self.M[self.s] else 0
                self.s -= 1
            elif instrucao == "CEQ":
                self.M[self.s - 1] = 1 if self.M[self.s - 1] == self.M[self.s] else 0
                self.s -= 1
            elif instrucao == "CDIF":
                self.M[self.s - 1] = 1 if self.M[self.s - 1] != self.M[self.s] else 0
                self.s -= 1
            elif instrucao == "CMEQ":
                self.M[self.s - 1] = 1 if self.M[self.s - 1] <= self.M[self.s] else 0
                self.s -= 1
            elif instrucao == "CMAQ":
                self.M[self.s - 1] = 1 if self.M[self.s - 1] >= self.M[self.s] else 0
                self.s -= 1
            
            elif instrucao == "JMP":
                proxima_inst = arg1
            
            elif instrucao == "JMPF":
                cond = self.M[self.s]
                if cond == 0:
                    proxima_inst = arg1
                self.s -= 1
            
            elif instrucao == "CALL":
                self.s += 1
                self._ensure_capacity(self.s)
                self.M[self.s] = proxima_inst
                proxima_inst = arg1
            
            elif instrucao == "RETURN":
                proxima_inst = self.M[self.s]
                self.s -= 1
            
            elif instrucao == "RD":
                self.running = False
                self.aguardando_input = True
                self.proxima_inst_apos_input = proxima_inst
                status_retorno = ("NEED_INPUT", None)
            
            elif instrucao == "PRN":
                valor_saida = self.M[self.s]
                self.s -= 1
                status_retorno = ("PRN_OUTPUT", valor_saida)
            
            else:
                raise ValueError(f"Instrução MVD desconhecida: {instrucao}")

        except Exception as e:
            self.running = False
            erro_msg = f"--- ERRO NA EXECUÇÃO (Instrução {self.i}) ---\n"
            erro_msg += f"Instrução: {instrucao} {arg1} {arg2}\n"
            erro_msg += f"Erro: {e}\n"
            erro_msg += f"Topo da Pilha (s={self.s}): {self.M[max(0, self.s-5):self.s+1]}"
            return ("ERROR", erro_msg)
        
        if self.aguardando_input == False:
            self.i = proxima_inst
        
        return status_retorno