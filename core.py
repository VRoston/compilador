class MVD:
    """
    MVD Ajustada: Pilha Dinâmica e Shadow Stack Seguro.
    - Inicia s=-1 para evitar conflito com variáveis.
    - ALLOC gerencia o topo da pilha automaticamente.
    - Suporta recursão profunda e muitas variáveis.
    """
    
    def __init__(self, tamanho_memoria=5000):
        self.M_size = tamanho_memoria
        self.M = [0] * self.M_size
        self.P = []
        self.mapa_rotulos = {}
        self.labels_by_index = []
        
        self.i = 0
        # CORREÇÃO 1: Inicializa s em -1. A pilha cresce a partir do zero.
        # O primeiro ALLOC do programa (ex: ALLOC 0 5) vai mover o s para 4.
        self.s = -1 
        self.running = False
        self.aguardando_input = False
        self.proxima_inst_apos_input = 0

    def resetar(self):
        self.M = [0] * self.M_size
        self.i = 0
        # CORREÇÃO 1: Resetar s para -1 também.
        self.s = -1 
        self.running = False
        self.aguardando_input = False
        self.labels_by_index = []

    def _parse_argumento(self, arg, mnemonico=None):
        if arg is None: return None
        arg_str = str(arg).strip()
        if arg_str == "" or arg_str.upper() in ("NULL", "NONE", "-"): return None
        if mnemonico in ("JMP", "JMPF", "CALL") and arg_str in self.mapa_rotulos:
            return self.mapa_rotulos[arg_str]
        try:
            return int(arg_str)
        except ValueError:
            if arg_str in self.mapa_rotulos:
                return self.mapa_rotulos[arg_str]
            raise ValueError(f"Argumento inválido: '{arg_str}'")

    def carregar_programa(self, nome_arquivo):
        self.P = []
        self.mapa_rotulos = {}
        self.labels_by_index = []
        programa_temp = []
        temp_label_map = {}
        
        MNEMONICOS = {
            "START","HLT","NULL","LDC","LDV","STR","ALLOC","DALLOC",
            "ADD","SUB","MULT","DIVI","INV","AND","OR","NEG",
            "CME","CMA","CEQ","CDIF","CMEQ","CMAQ",
            "JMP","JMPF","CALL","RETURN","RD","PRN"
        }
        
        with open(nome_arquivo, 'r') as f:
            for linha in f:
                linha = linha.strip()
                if not linha or linha.startswith(';'): continue
                if ';' in linha: linha = linha.split(';', 1)[0].strip()
                partes = linha.split()
                if not partes: continue
                
                first = partes[0]
                rotulo = None
                if first.endswith(':'):
                    rotulo = first[:-1]
                    partes = partes[1:]
                elif first.upper() not in MNEMONICOS:
                    rotulo = first
                    partes = partes[1:]
                
                if rotulo:
                    temp_label_map.setdefault(len(programa_temp), []).append(rotulo)
                    self.mapa_rotulos[rotulo] = len(programa_temp)
                
                if not partes: continue
                mnemonico = partes[0].upper()
                args = partes[1:] + [None, None]
                programa_temp.append((mnemonico, args[0], args[1]))

        self.labels_by_index = [None] * len(programa_temp)
        for idx, lbs in temp_label_map.items():
            self.labels_by_index[idx] = ",".join(lbs)

        for mnemonico, arg1_str, arg2_str in programa_temp:
            arg1 = self._parse_argumento(arg1_str, mnemonico)
            arg2 = self._parse_argumento(arg2_str, mnemonico)
            self.P.append((mnemonico, arg1, arg2))
        self.running = True

    def _ensure_capacity(self, idx):
        if idx < len(self.M): return
        extra = idx - len(self.M) + 1024
        self.M.extend([0] * extra)

    def fornecer_entrada(self, valor_str):
        if not self.aguardando_input: return
        try: val = int(valor_str)
        except: val = 0
        
        self.s += 1
        self._ensure_capacity(self.s)
        self.M[self.s] = val
        
        self.aguardando_input = False
        self.running = True
        self.i = self.proxima_inst_apos_input

    def executar_passo(self):
        if not self.running or self.i >= len(self.P) or self.aguardando_input:
            if self.aguardando_input: return ("NEED_INPUT", None)
            self.running = False
            return ("HALTED", None)

        instrucao, arg1, arg2 = self.P[self.i]
        proxima_inst = self.i + 1
        status_retorno = ("RUNNING", None)

        try:
            if instrucao == "START":
                # CORREÇÃO 1: Inicia a pilha vazia (base -1)
                self.s = -1

            elif instrucao == "ALLOC":
                m = arg1 if arg1 is not None else 0
                n = arg2 if arg2 is not None else 0
                
                # CORREÇÃO 2: Lógica de Shadow Stack
                # Primeiro, verifica se precisamos expandir a pilha para cobrir as novas variáveis
                # Se s está em -1 e alocamos m=0, n=5, o novo s deve ser pelo menos 4.
                topo_necessario = m + n - 1
                if self.s < topo_necessario:
                    self.s = topo_necessario
                    self._ensure_capacity(self.s)

                # Agora fazemos o backup (Shadow Stack)
                # Empilhamos os valores atuais das variáveis m até m+n-1 no topo ATUAL da pilha
                for k in range(n):
                    addr = m + k
                    # Pega valor atual (pode ser 0 se for primeira vez, ou lixo de recursão)
                    val = self.M[addr] 
                    
                    # Empilha no topo seguro (acima de todas as variáveis alocadas)
                    self.s += 1
                    self._ensure_capacity(self.s)
                    self.M[self.s] = val
                    
            elif instrucao == "DALLOC":
                m = arg1 if arg1 is not None else 0
                n = arg2 if arg2 is not None else 0
                
                # Restaura na ordem inversa (LIFO) do topo da pilha para as variáveis
                for k in range(n - 1, -1, -1):
                    addr = m + k
                    val = self.M[self.s] # Pega do backup
                    self.s -= 1 # Desempilha
                    self.M[addr] = val # Restaura na memória fixa
                
                # Opcional: Se desalocamos variáveis globais no fim, poderíamos reduzir s,
                # mas o DALLOC padrão apenas restaura valores. 
                # A redução do topo 's' acontece naturalmente ao consumir o backup.

            elif instrucao == "CALL":
                self.s += 1
                self._ensure_capacity(self.s)
                self.M[self.s] = proxima_inst
                proxima_inst = arg1

            elif instrucao == "RETURN":
                ret_addr = self.M[self.s]
                self.s -= 1
                proxima_inst = ret_addr

            # --- Instruções de Acesso e Aritmética ---
            # (Permanecem iguais, pois usam s relativo ou endereços absolutos)

            elif instrucao == "LDV":
                addr = arg1
                self.s += 1
                self._ensure_capacity(self.s)
                self.M[self.s] = self.M[addr]

            elif instrucao == "STR":
                addr = arg1
                self.M[addr] = self.M[self.s]
                self.s -= 1
            
            elif instrucao == "HLT":
                self.running = False
                status_retorno = ("HALTED", None)
            elif instrucao == "NULL": pass
            elif instrucao == "LDC":
                self.s += 1; self._ensure_capacity(self.s); self.M[self.s] = arg1
            
            elif instrucao == "ADD": self.M[self.s-1] += self.M[self.s]; self.s -= 1
            elif instrucao == "SUB": self.M[self.s-1] -= self.M[self.s]; self.s -= 1
            elif instrucao == "MULT": self.M[self.s-1] *= self.M[self.s]; self.s -= 1
            elif instrucao == "DIVI": self.M[self.s-1] = int(self.M[self.s-1] / self.M[self.s]); self.s -= 1
            elif instrucao == "INV": self.M[self.s] = -self.M[self.s]
            elif instrucao == "AND": self.M[self.s-1] = 1 if (self.M[self.s-1] and self.M[self.s]) else 0; self.s -= 1
            elif instrucao == "OR": self.M[self.s-1] = 1 if (self.M[self.s-1] or self.M[self.s]) else 0; self.s -= 1
            elif instrucao == "NEG": self.M[self.s] = 1 - self.M[self.s]
            elif instrucao == "CME": self.M[self.s-1] = 1 if self.M[self.s-1] < self.M[self.s] else 0; self.s -= 1
            elif instrucao == "CMA": self.M[self.s-1] = 1 if self.M[self.s-1] > self.M[self.s] else 0; self.s -= 1
            elif instrucao == "CEQ": self.M[self.s-1] = 1 if self.M[self.s-1] == self.M[self.s] else 0; self.s -= 1
            elif instrucao == "CDIF": self.M[self.s-1] = 1 if self.M[self.s-1] != self.M[self.s] else 0; self.s -= 1
            elif instrucao == "CMEQ": self.M[self.s-1] = 1 if self.M[self.s-1] <= self.M[self.s] else 0; self.s -= 1
            elif instrucao == "CMAQ": self.M[self.s-1] = 1 if self.M[self.s-1] >= self.M[self.s] else 0; self.s -= 1

            elif instrucao == "JMP": proxima_inst = arg1
            elif instrucao == "JMPF":
                if self.M[self.s] == 0: proxima_inst = arg1
                self.s -= 1

            elif instrucao == "RD":
                self.running = False; self.aguardando_input = True
                self.proxima_inst_apos_input = proxima_inst; status_retorno = ("NEED_INPUT", None)
            elif instrucao == "PRN":
                valor = self.M[self.s]; self.s -= 1; status_retorno = ("PRN_OUTPUT", valor)
            else:
                raise ValueError(f"Instrução desconhecida: {instrucao}")

        except Exception as e:
            self.running = False
            return ("ERROR", f"{str(e)} em linha {self.i}")
        
        if not self.aguardando_input:
            self.i = proxima_inst
        
        return status_retorno