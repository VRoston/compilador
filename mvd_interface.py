import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

# =============================================================================
# 1. CLASSE MVD (SEU CÓDIGO, MODIFICADO PARA O GUI)
# =============================================================================

class MVD:
    """
    Implementação da Máquina Virtual Didática (MVD) em Python,
    adaptada para ser controlada por uma interface gráfica.
    
    MODIFICAÇÕES:
    - O método `executar()` foi dividido em `executar_passo()`.
    - `RD` (Leitura) não bloqueia mais. Ele retorna um status 'NEED_INPUT'.
    - `PRN` (Impressão) retorna um status 'PRN_OUTPUT' com o valor.
    - `fornecer_entrada(valor)` é o novo método para injetar o valor do 'RD'.
    - `resetar()` foi adicionado para limpar o estado da MVD.
    """
    
    def __init__(self, tamanho_memoria=5000):
        self.P = []
        self.M_size = tamanho_memoria
        self.M = [0] * self.M_size
        self.mapa_rotulos = {}
        self.debug = True # (Deixei seu debug ativado)
        
        # Estado da MVD
        self.i = 0
        self.s = -1
        self.running = False
        self.aguardando_input = False
        self.proxima_inst_apos_input = 0 # Para salvar 'i' durante RD

    def resetar(self):
        """ Limpa a memória e os registradores para uma nova execução. """
        self.M = [0] * self.M_size
        self.i = 0
        self.s = -1
        self.running = False
        self.aguardando_input = False
        print("MVD Resetada.")

    # (Seu método _parse_argumento original)
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

    # (Seu método carregar_programa original)
    def carregar_programa(self, nome_arquivo):
        # Limpa estado anterior antes de carregar
        self.P = []
        self.mapa_rotulos = {}
        
        programa_temp = []
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
                    self.mapa_rotulos[rotulo_token] = len(programa_temp)
                if not partes:
                    continue
                mnemonico = partes[0].upper()
                args = partes[1:] + [None, None]
                programa_temp.append((mnemonico, args[0], args[1]))

        for mnemonico, arg1_str, arg2_str in programa_temp:
            arg1 = self._parse_argumento(arg1_str, mnemonico)
            arg2 = self._parse_argumento(arg2_str, mnemonico)
            self.P.append((mnemonico, arg1, arg2))

        self.running = True # Pronto para executar
        print(f"Programa carregado. {len(self.P)} instruções.")
        print(f"Rótulos encontrados: {self.mapa_rotulos}")

    def _ensure_capacity(self, idx):
        if idx < len(self.M):
            return
        extra = idx - len(self.M) + 1024
        self.M.extend([0] * extra)

    def fornecer_entrada(self, valor_str):
        """
        Recebe a entrada do GUI e completa a instrução RD.
        """
        if not self.aguardando_input:
            return

        try:
            valor_lido = int(valor_str)
        except ValueError:
            print("Erro: Entrada inválida, usando 0.")
            valor_lido = 0
            
        self.s += 1
        self._ensure_capacity(self.s)
        self.M[self.s] = valor_lido
        
        self.aguardando_input = False
        self.running = True
        self.i = self.proxima_inst_apos_input # Restaura 'i' para a próxima instrução
        print(f"[RD] Valor {valor_lido} recebido. s={self.s}. Próximo i={self.i}")

    def executar_passo(self):
        """
        Executa UMA ÚNICA instrução da MVD.
        Retorna (STATUS, DADOS)
        """
        if not self.running or self.i >= len(self.P) or self.aguardando_input:
            if not self.running:
                return ("HALTED", None)
            if self.aguardando_input:
                return ("NEED_INPUT", None)
            # Se 'i' ultrapassar o programa sem HLT, é um HLT implícito
            self.running = False
            return ("HALTED", None)

        # 1. Fetch (Busca)
        instrucao, arg1, arg2 = self.P[self.i]

        # Endereço da próxima instrução (default)
        proxima_inst = self.i + 1
        
        status_retorno = ("RUNNING", None)

        # 2. Decode & 3. Execute
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
                # --- MODIFICAÇÃO PARA GUI ---
                self.running = False
                self.aguardando_input = True
                self.proxima_inst_apos_input = proxima_inst # Salva para onde pular
                status_retorno = ("NEED_INPUT", None)
            
            elif instrucao == "PRN":
                # --- MODIFICAÇÃO PARA GUI ---
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
            print(erro_msg)
            return ("ERROR", erro_msg)
        
        # 4. Incremento
        if self.aguardando_input == False:
            self.i = proxima_inst
        
        return status_retorno

# =============================================================================
# 2. CLASSE MVD_GUI (A NOVA INTERFACE GRÁFICA)
# =============================================================================

class MVD_GUI(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.title("Simulador MVD (Máquina Virtual Didática)")
        self.geometry("1000x700")
        
        self.mvd = MVD()
        self.filepath = None
        self.running_fast = False

        self.criar_widgets()
        self._set_controls_state("INICIAL")

    def criar_widgets(self):
        # --- Frame de Controles (Topo) ---
        frame_controles = tk.Frame(self, bd=2, relief=tk.RAISED)
        frame_controles.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.btn_load = tk.Button(frame_controles, text="Carregar Arquivo (.obj)", command=self.carregar_arquivo)
        self.btn_load.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_run = tk.Button(frame_controles, text="Executar", command=self.executar_direto, bg="#c0ffc0")
        self.btn_run.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_step = tk.Button(frame_controles, text="Passo-a-Passo", command=self.executar_passo)
        self.btn_step.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_stop = tk.Button(frame_controles, text="Parar", command=self.parar_execucao, bg="#ffc0c0")
        self.btn_stop.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_reset = tk.Button(frame_controles, text="Resetar", command=self.resetar_mvd)
        self.btn_reset.pack(side=tk.LEFT, padx=5, pady=5)

        self.status_label = tk.Label(frame_controles, text="Nenhum arquivo carregado.", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5, pady=5)

        # --- Frame Principal (Código e Pilha) ---
        frame_principal = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=5)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Sub-frame do Código
        frame_codigo = tk.Frame(frame_principal, bd=2, relief=tk.SUNKEN)
        tk.Label(frame_codigo, text="Programa (Memória P)").pack(side=tk.TOP, fill=tk.X)
        scrollbar_codigo = tk.Scrollbar(frame_codigo, orient=tk.VERTICAL)
        self.program_listbox = tk.Listbox(frame_codigo, yscrollcommand=scrollbar_codigo.set, font=("Courier", 10))
        scrollbar_codigo.config(command=self.program_listbox.yview)
        scrollbar_codigo.pack(side=tk.RIGHT, fill=tk.Y)
        self.program_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        frame_principal.add(frame_codigo)

        # Sub-frame da Pilha
        frame_pilha = tk.Frame(frame_principal, bd=2, relief=tk.SUNKEN)
        tk.Label(frame_pilha, text="Pilha de Dados (Memória M)").pack(side=tk.TOP, fill=tk.X)
        scrollbar_pilha = tk.Scrollbar(frame_pilha, orient=tk.VERTICAL)
        self.stack_listbox = tk.Listbox(frame_pilha, yscrollcommand=scrollbar_pilha.set, font=("Courier", 10))
        scrollbar_pilha.config(command=self.stack_listbox.yview)
        scrollbar_pilha.pack(side=tk.RIGHT, fill=tk.Y)
        self.stack_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        frame_principal.add(frame_pilha)

        # --- Frame de I/O (Baixo) ---
        frame_io = tk.Frame(self, height=150, bd=2, relief=tk.SUNKEN)
        frame_io.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        frame_io.pack_propagate(False) # Impede que o frame encolha

        # Frame de Input (Fica escondido)
        self.input_frame = tk.Frame(frame_io)
        tk.Label(self.input_frame, text="Entrada (RD):", font=("Courier", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.input_entry = tk.Entry(self.input_frame, font=("Courier", 10), width=20)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        self.input_submit = tk.Button(self.input_frame, text="Submeter", command=self.submeter_entrada)
        self.input_submit.pack(side=tk.LEFT, padx=5)
        self.input_entry.bind("<Return>", (lambda event: self.submeter_entrada()))

        # Frame de Output (Sempre visível)
        tk.Label(frame_io, text="Saída (PRN) e Erros:", anchor=tk.NW).pack(side=tk.TOP, fill=tk.X, padx=5)
        self.output_text = scrolledtext.ScrolledText(frame_io, height=5, font=("Courier", 10), wrap=tk.WORD, state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def _set_controls_state(self, state):
        """ Gerencia o estado dos botões (INICIAL, CARREGADO, RODANDO, INPUT) """
        if state == "INICIAL":
            self.btn_load.config(state=tk.NORMAL)
            self.btn_run.config(state=tk.DISABLED)
            self.btn_step.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.DISABLED)
            self.btn_reset.config(state=tk.DISABLED)
        elif state == "CARREGADO": # (parado, pronto para rodar)
            self.btn_load.config(state=tk.NORMAL)
            self.btn_run.config(state=tk.NORMAL)
            self.btn_step.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            self.btn_reset.config(state=tk.NORMAL)
        elif state == "RODANDO": # (execução rápida)
            self.btn_load.config(state=tk.DISABLED)
            self.btn_run.config(state=tk.DISABLED)
            self.btn_step.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.btn_reset.config(state=tk.DISABLED)
        elif state == "AGUARDANDO_INPUT":
            self.btn_load.config(state=tk.DISABLED)
            self.btn_run.config(state=tk.DISABLED)
            self.btn_step.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL) # Pode parar/resetar
            self.btn_reset.config(state=tk.NORMAL)

    def log_output(self, message, is_error=False):
        """ Adiciona uma mensagem à caixa de Saída/Erros """
        self.output_text.config(state=tk.NORMAL)
        tag = "error" if is_error else "output"
        self.output_text.tag_configure("error", foreground="red")
        self.output_text.tag_configure("output", foreground="blue")
        self.output_text.insert(tk.END, f"{message}\n", (tag,))
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def atualizar_ui(self):
        """ Atualiza os listboxes de Código e Pilha """
        
        # 1. Atualiza Lista de Programa e destaca 'i'
        if self.mvd.i < self.program_listbox.size():
            self.program_listbox.selection_clear(0, tk.END)
            self.program_listbox.selection_set(self.mvd.i)
            self.program_listbox.see(self.mvd.i)
            self.program_listbox.activate(self.mvd.i)

        # 2. Atualiza Lista da Pilha
        self.stack_listbox.delete(0, tk.END)
        # Mostra 20 posições além do topo da pilha, ou 50, o que for maior
        limite_pilha = max(50, self.mvd.s + 20)
        
        # Otimização: só mostra posições relevantes (perto de 0 e perto de 's')
        indices_para_mostrar = set(range(20)) # Primeiros 20
        indices_para_mostrar.update(range(max(0, self.mvd.s - 20), self.mvd.s + 20)) # Perto do 's'
        
        last_idx = -2
        for i in sorted(list(indices_para_mostrar)):
            if i >= len(self.mvd.M):
                break
            
            # Adiciona "..." para saltos
            if i != last_idx + 1:
                self.stack_listbox.insert(tk.END, f"...")
            
            val = self.mvd.M[i]
            prefixo = "s ->" if i == self.mvd.s else "    "
            self.stack_listbox.insert(tk.END, f"{prefixo} M[{i}]: {val}")
            
            last_idx = i

        if self.mvd.s >= 0:
            self.stack_listbox.see(self.stack_listbox.size() - 1) # Vê o final

    def carregar_arquivo(self):
        filepath = filedialog.askopenfilename(
            title="Selecionar Arquivo .obj",
            filetypes=(("OBJ files", "*.obj"), ("All files", "*.*"))
        )
        if not filepath:
            return

        self.filepath = filepath
        self.resetar_mvd() # Reseta e carrega o novo arquivo
        
    def resetar_mvd(self):
        self.running_fast = False
        self.mvd.resetar() # Limpa a MVD interna

        # Limpa UI
        self.program_listbox.delete(0, tk.END)
        self.stack_listbox.delete(0, tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.input_frame.pack_forget()

        if self.filepath:
            try:
                # Recarrega o programa no estado limpo da MVD
                self.mvd.carregar_programa(self.filepath)
                
                # Popula o listbox do programa
                for i, (mnem, a1, a2) in enumerate(self.mvd.P):
                    a1_str = str(a1) if a1 is not None else ""
                    a2_str = str(a2) if a2 is not None else ""
                    self.program_listbox.insert(tk.END, f"{i:03d}: {mnem:<8} {a1_str:<5} {a2_str:<5}")
                
                self.status_label.config(text=f"Carregado: {self.filepath}")
                self._set_controls_state("CARREGADO")
                self.atualizar_ui()
            except Exception as e:
                messagebox.showerror("Erro ao Carregar", f"Falha ao carregar o arquivo {self.filepath}:\n{e}")
                self.filepath = None
                self._set_controls_state("INICIAL")
        else:
            self.status_label.config(text="Nenhum arquivo carregado.")
            self._set_controls_state("INICIAL")
            
    def executar_direto(self):
        if not self.mvd.running:
            return
            
        self.running_fast = True
        self._set_controls_state("RODANDO")
        self.status_label.config(text="Executando...")
        self.run_loop() # Inicia o loop de execução rápida

    def run_loop(self):
        """ Loop de execução rápida (usa 'after' para não travar o GUI) """
        if not self.running_fast:
            return # 'Parar' foi pressionado
            
        status, data = self.executar_passo(is_direct_run=True)
        
        # Continua o loop se estiver rodando
        if status == "RUNNING" or status == "PRN_OUTPUT":
            # O 'after(1)' dá 1ms para o GUI respirar e atualizar
            self.after(1, self.run_loop) 

    def parar_execucao(self):
        self.running_fast = False
        self.mvd.running = False
        self._set_controls_state("CARREGADO") # Volta ao estado "pronto"
        self.status_label.config(text="Execução parada pelo usuário.")
        self.input_frame.pack_forget()

    def executar_passo(self, is_direct_run=False):
        """ Executa um único passo e atualiza o GUI """
        if not self.mvd.running and not self.mvd.aguardando_input:
            self.status_label.config(text="Execução finalizada.")
            return "HALTED", None

        try:
            status, data = self.mvd.executar_passo()
        except Exception as e:
            status, data = "ERROR", str(e)
            
        # Atualiza a UI (pilha, ponteiro 'i')
        self.atualizar_ui() 

        if status == "RUNNING":
            if not is_direct_run: # Se foi só um passo
                self.status_label.config(text=f"Instrução {self.mvd.i} executada.")
                self._set_controls_state("CARREGADO")
        
        elif status == "HALTED":
            self.running_fast = False
            self.status_label.config(text="Execução Finalizada (HLT).")
            self._set_controls_state("CARREGADO")
            self.btn_run.config(state=tk.DISABLED) # Não pode rodar de novo
            self.btn_step.config(state=tk.DISABLED)
        
        elif status == "NEED_INPUT":
            self.running_fast = False # Pausa a execução rápida
            self.status_label.config(text="Aguardando entrada (RD)...")
            self._set_controls_state("AGUARDANDO_INPUT")
            self.input_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            self.input_entry.focus()
            
        elif status == "PRN_OUTPUT":
            self.log_output(f"Saída: {data}")
            if not is_direct_run:
                self.status_label.config(text=f"Instrução {self.mvd.i} (PRN) executada.")
                self._set_controls_state("CARREGADO")

        elif status == "ERROR":
            self.running_fast = False
            self.log_output(data, is_error=True)
            self.status_label.config(text="Erro na execução!")
            self._set_controls_state("CARREGADO")
            self.btn_run.config(state=tk.DISABLED) # Não pode continuar
            self.btn_step.config(state=tk.DISABLED)
            
        return status, data

    def submeter_entrada(self):
        valor = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        self.input_frame.pack_forget() # Esconde o frame de input
        
        self.mvd.fornecer_entrada(valor)
        
        if self.running_fast:
            # Se estávamos em modo "Executar", retoma o loop
            self._set_controls_state("RODANDO")
            self.status_label.config(text="Executando...")
            self.run_loop()
        else:
            # Se estávamos em modo "Passo", apenas re-habilita os botões
            self._set_controls_state("CARREGADO")
            self.status_label.config(text="Entrada recebida. Pronto para o próximo passo.")
            self.atualizar_ui() # Atualiza para mostrar o valor na pilha


# =============================================================================
# 3. INICIALIZAÇÃO DA APLICAÇÃO
# =============================================================================

if __name__ == "__main__":
    try:
        app = MVD_GUI()
        app.mainloop()
    except Exception as e:
        print(f"Erro fatal ao iniciar a GUI: {e}")