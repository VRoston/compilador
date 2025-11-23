class MVD:
    """
    Máquina Virtual (MVD) com pilha dinâmica e mecanismo de "shadow stack".
    Objetivo: suportar alocação/desalocação de variáveis locais, chamadas/retorno
    e I/O em um espaço de memória único.
    Principais convenções:
      - Memória principal M: vetor de inteiros.
      - Ponteiro de pilha 's': índice do topo da pilha real (inicia em -1).
      - Programa P: lista de tuplas (mnemonico, arg1, arg2).
      - 'labels_by_index' e 'mapa_rotulos' para resolução de rótulos.
    """
    
    def __init__(self, tamanho_memoria=5000):
        # Tamanho inicial da memória (expansível)
        self.M_size = tamanho_memoria
        # Memória principal: valores inteiros
        self.M = [0] * self.M_size
        # Programa (lista de instruções)
        self.P = []
        # Mapeamento rótulo -> índice de instrução
        self.mapa_rotulos = {}
        # Representação textual dos rótulos por índice
        self.labels_by_index = []
        
        # Contador de instrução atual
        self.i = 0
        # Ponteiro do topo da pilha. -1 indica pilha vazia.
        # Usar -1 evita conflitos com endereços de variáveis (que começam em 0).
        self.s = -1 
        # Flags de execução
        self.running = False
        self.aguardando_input = False
        self.proxima_inst_apos_input = 0

    def resetar(self):
        """Redefine o estado da máquina conservando capacidade de memória."""
        self.M = [0] * self.M_size
        self.i = 0
        # Mantém a convenção: pilha vazia = -1
        self.s = -1 
        self.running = False
        self.aguardando_input = False
        self.labels_by_index = []

    def _parse_argumento(self, arg, mnemonico=None):
        """
        Converte um argumento textual em inteiro ou índice de rótulo.
        Aceita strings vazias e tokens de 'nulo' (NULL, NONE, -).
        Para instruções de salto, resolve rótulos usando mapa de rótulos.
        """
        if arg is None: return None
        arg_str = str(arg).strip()
        if arg_str == "" or arg_str.upper() in ("NULL", "NONE", "-"): return None
        # Se for um salto e o token é um rótulo conhecido, devolve o índice
        if mnemonico in ("JMP", "JMPF", "CALL") and arg_str in self.mapa_rotulos:
            return self.mapa_rotulos[arg_str]
        try:
            # Tenta converter para inteiro direto
            return int(arg_str)
        except ValueError:
            # Última tentativa: resolver como rótulo (para outros mnemonicos)
            if arg_str in self.mapa_rotulos:
                return self.mapa_rotulos[arg_str]
            raise ValueError(f"Argumento inválido: '{arg_str}'")

    def carregar_programa(self, nome_arquivo):
        """
        Lê um arquivo fonte com um programa MVD.
        - Suporta rótulos colocados no início da linha (com ou sem ':').
        - Ignora linhas vazias e comentários iniciados por ';'.
        - Preenche self.P com tuplas (mnemonico, arg1, arg2) já parseadas.
        """
        self.P = []
        self.mapa_rotulos = {}
        self.labels_by_index = []
        programa_temp = []
        temp_label_map = {}
        
        # Conjunto de mnemonicos reconhecidos (maiúsculos)
        MNEMONICOS = {
            "START","HLT","NULL","LDC","LDV","STR","ALLOC","DALLOC",
            "ADD","SUB","MULT","DIVI","INV","AND","OR","NEG",
            "CME","CMA","CEQ","CDIF","CMEQ","CMAQ",
            "JMP","JMPF","CALL","RETURN","RD","PRN"
        }
        
        with open(nome_arquivo, 'r') as f:
            for linha in f:
                linha = linha.strip()
                # Ignora comentários e linhas vazias
                if not linha or linha.startswith(';'): continue
                if ';' in linha: linha = linha.split(';', 1)[0].strip()
                partes = linha.split()
                if not partes: continue
                
                first = partes[0]
                rotulo = None
                # Detecta rótulo terminando com ':' ou quando o primeiro token não é mnemonico
                if first.endswith(':'):
                    rotulo = first[:-1]
                    partes = partes[1:]
                elif first.upper() not in MNEMONICOS:
                    rotulo = first
                    partes = partes[1:]
                
                if rotulo:
                    # Registra rótulo apontando para a próxima instrução (índice atual)
                    temp_label_map.setdefault(len(programa_temp), []).append(rotulo)
                    self.mapa_rotulos[rotulo] = len(programa_temp)
                
                if not partes: continue
                mnemonico = partes[0].upper()
                # Garante dois argumentos (pode haver None)
                args = partes[1:] + [None, None]
                programa_temp.append((mnemonico, args[0], args[1]))

        # Constroi labels_by_index para fins de debugging/exibição
        self.labels_by_index = [None] * len(programa_temp)
        for idx, lbs in temp_label_map.items():
            self.labels_by_index[idx] = ",".join(lbs)

        # Converte argumentos textuais para inteiros ou índices de rótulo
        for mnemonico, arg1_str, arg2_str in programa_temp:
            arg1 = self._parse_argumento(arg1_str, mnemonico)
            arg2 = self._parse_argumento(arg2_str, mnemonico)
            self.P.append((mnemonico, arg1, arg2))
        # Marca que o programa está pronto para executar
        self.running = True

    def _ensure_capacity(self, idx):
        """
        Garante que a memória M tenha pelo menos índice 'idx'.
        Se necessário, expande a memória por blocos.
        """
        if idx < len(self.M): return
        extra = idx - len(self.M) + 1024
        self.M.extend([0] * extra)

    def fornecer_entrada(self, valor_str):
        """
        Recebe a entrada do usuário quando a máquina está aguardando um RD.
        Converte para inteiro (fallback 0) e empilha no topo.
        Retoma a execução na instrução seguinte ao RD.
        """
        if not self.aguardando_input: return
        try: val = int(valor_str)
        except: val = 0
        
        # Insere o valor na pilha
        self.s += 1
        self._ensure_capacity(self.s)
        self.M[self.s] = val
        
        # Restaura flags de execução
        self.aguardando_input = False
        self.running = True
        self.i = self.proxima_inst_apos_input

    def executar_passo(self):
        """
        Executa uma única instrução do programa (ou retorna estado se precisar de input / estiver parado).
        Retorna uma tupla (status, valor) onde status pode ser:
          - "RUNNING": continua
          - "NEED_INPUT": aguardando entrada (RD)
          - "PRN_OUTPUT": valor para imprimir
          - "HALTED": programa finalizado
          - "ERROR": erro com mensagem
        """
        if not self.running or self.i >= len(self.P) or self.aguardando_input:
            if self.aguardando_input: return ("NEED_INPUT", None)
            self.running = False
            return ("HALTED", None)

        instrucao, arg1, arg2 = self.P[self.i]
        proxima_inst = self.i + 1
        status_retorno = ("RUNNING", None)

        try:
            # --- Controle de início / pilha ---
            if instrucao == "START":
                # Inicializa ponteiro de pilha como vazio (-1)
                self.s = -1

            elif instrucao == "ALLOC":
                # ALLOC m n : reserva/garante espaço para variáveis em endereços [m, m+n-1]
                # Implementa um "shadow stack" que salva (backup) os valores atuais
                # das variáveis para permitir restauração após DALLOC.
                m = arg1 if arg1 is not None else 0
                n = arg2 if arg2 is not None else 0
                
                # Calcula o índice do topo necessário para cobrir as variáveis
                topo_necessario = m + n - 1
                # Se s < topo_necessario, ajusta s para que a região de variáveis exista
                if self.s < topo_necessario:
                    self.s = topo_necessario
                    self._ensure_capacity(self.s)

                # Salva (faz backup) dos valores das variáveis no topo da pilha
                # Cada valor é empilhado acima do espaço atual usado.
                for k in range(n):
                    addr = m + k
                    val = self.M[addr]  # valor atual da variável (ou 0 se não inicializada)
                    self.s += 1
                    self._ensure_capacity(self.s)
                    self.M[self.s] = val
                    
            elif instrucao == "DALLOC":
                # DALLOC m n : restaura n valores salvos no ALLOC para os endereços [m, m+n-1]
                # A restauração ocorre em ordem inversa (LIFO) para corresponder ao backup.
                m = arg1 if arg1 is not None else 0
                n = arg2 if arg2 is not None else 0
                
                for k in range(n - 1, -1, -1):
                    addr = m + k
                    val = self.M[self.s]    # pega o último valor empilhado
                    self.s -= 1             # desempilha
                    self.M[addr] = val      # restaura na memória fixa

                # Nota: após DALLOC, o topo s já foi reduzido conforme os desempilhamentos.

            elif instrucao == "CALL":
                # CALL addr : empilha endereço de retorno e pula para addr
                self.s += 1
                self._ensure_capacity(self.s)
                self.M[self.s] = proxima_inst
                proxima_inst = arg1

            elif instrucao == "RETURN":
                # RETURN : desempilha endereço de retorno e ajusta o contador
                ret_addr = self.M[self.s]
                self.s -= 1
                proxima_inst = ret_addr

            # --- Acesso à memória e operações aritméticas / lógicas ---
            elif instrucao == "LDV":
                # LDV addr : carrega valor de M[addr] para o topo da pilha
                addr = arg1
                self.s += 1
                self._ensure_capacity(self.s)
                self.M[self.s] = self.M[addr]

            elif instrucao == "STR":
                # STR addr : armazena o topo da pilha em M[addr] (consome o topo)
                addr = arg1
                self.M[addr] = self.M[self.s]
                self.s -= 1
            
            elif instrucao == "HLT":
                # Finaliza execução
                self.running = False
                status_retorno = ("HALTED", None)
            elif instrucao == "NULL":
                # Instrução nula / no-op
                pass
            elif instrucao == "LDC":
                # LDC k : empilha constante k
                self.s += 1; self._ensure_capacity(self.s); self.M[self.s] = arg1
            
            # Operações binárias que consomem o topo da pilha
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

            # --- Saltos e controle de fluxo ---
            elif instrucao == "JMP": proxima_inst = arg1
            elif instrucao == "JMPF":
                # JMPF addr : se topo == 0, pula para addr; consome o topo
                if self.M[self.s] == 0: proxima_inst = arg1
                self.s -= 1

            # --- I/O ---
            elif instrucao == "RD":
                # RD : solicita entrada, pausa execução e espera fornecer_entrada()
                self.running = False; self.aguardando_input = True
                self.proxima_inst_apos_input = proxima_inst; status_retorno = ("NEED_INPUT", None)
            elif instrucao == "PRN":
                # PRN : desempilha e retorna valor para impressão
                valor = self.M[self.s]; self.s -= 1; status_retorno = ("PRN_OUTPUT", valor)
            else:
                raise ValueError(f"Instrução desconhecida: {instrucao}")

        except Exception as e:
            # Em caso de erro, interrompe execução e reporta o erro com a linha atual
            self.running = False
            return ("ERROR", f"{str(e)} em linha {self.i}")
        
        # Se não estamos aguardando entrada, atualiza contador de instrução
        if not self.aguardando_input:
            self.i = proxima_inst
        
        return status_retorno