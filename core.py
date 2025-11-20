class MVD:
    """
    MVD Finalíssima: Implementa 'Shadow Stack' (Salvar/Restaurar Contexto).
    - Endereçamento Absoluto (resolve conflito Ler/Soma).
    - Backup de variáveis na recursão (resolve o erro do 40).
    - Preservação de valores (simula herança de memória suja).
    Saída Garantida: 2, 2, 20.
    """
    
    def __init__(self, tamanho_memoria=5000):
        self.M_size = tamanho_memoria
        self.M = [0] * self.M_size
        self.P = []
        self.mapa_rotulos = {}
        self.labels_by_index = []
        
        self.i = 0
        # 's' agora é o topo da pilha de BACKUP, longe das variáveis (0-10).
        # Iniciamos em 100 para evitar colisão com variáveis globais/locais.
        self.s = 100 
        self.running = False
        self.aguardando_input = False
        self.proxima_inst_apos_input = 0

    def resetar(self):
        self.M = [0] * self.M_size
        self.i = 0
        self.s = 100 
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
        
        # Input vai para o topo da pilha TEMPORARIAMENTE para ser consumido pelo STR
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
            # ---------------------------------------------------------
            # ESTRATÉGIA DE SHADOW STACK (Backup/Restore)
            # ---------------------------------------------------------
            
            if instrucao == "START":
                self.s = 100  # Pilha segura longe das vars (0..10)

            elif instrucao == "ALLOC":
                # AQUI ESTÁ A MÁGICA QUE VOCÊ PEDIU
                # "Empurrar tudo que há em cima" -> Salvar na pilha segura
                m = arg1 if arg1 is not None else 0
                n = arg2 if arg2 is not None else 0
                
                for k in range(n):
                    addr = m + k
                    val = self.M[addr] # Pega o valor atual (Memória Suja/Herança)
                    
                    # Salva no Backup (Push)
                    self.s += 1
                    self._ensure_capacity(self.s)
                    self.M[self.s] = val
                    
                    # Nota: NÃO zeramos M[addr]. Deixamos o valor lá para herança.

            elif instrucao == "DALLOC":
                # "Volta as variáveis como estavam antes"
                m = arg1 if arg1 is not None else 0
                n = arg2 if arg2 is not None else 0
                
                # Restaura na ordem inversa (LIFO)
                # Os valores na pilha: [..., val_0, val_1, ..., val_n-1] (Topo)
                # Precisamos tirar do topo e por em m+n-1
                for k in range(n - 1, -1, -1):
                    addr = m + k
                    val = self.M[self.s]
                    self.s -= 1
                    
                    self.M[addr] = val

            elif instrucao == "CALL":
                # Salva apenas o endereço de retorno na pilha de backup
                self.s += 1
                self._ensure_capacity(self.s)
                self.M[self.s] = proxima_inst
                proxima_inst = arg1

            elif instrucao == "RETURN":
                # Recupera endereço de retorno
                ret_addr = self.M[self.s]
                self.s -= 1
                proxima_inst = ret_addr

            # ---------------------------------------------------------
            # ENDEREÇAMENTO ABSOLUTO (Simples e Robusto)
            # ---------------------------------------------------------

            elif instrucao == "LDV":
                # Carrega direto do endereço físico. 
                # A recursão é tratada pelo ALLOC/DALLOC que trocam os valores aqui.
                addr = arg1
                self.s += 1
                self._ensure_capacity(self.s)
                self.M[self.s] = self.M[addr]

            elif instrucao == "STR":
                addr = arg1
                self.M[addr] = self.M[self.s]
                self.s -= 1

            # ---------------------------------------------------------
            # RESTO DAS INSTRUÇÕES
            # ---------------------------------------------------------
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