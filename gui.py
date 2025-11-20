from tkinter import Tk, Frame, Button, Label, Listbox, Scrollbar, Entry, messagebox, scrolledtext, filedialog, PanedWindow

class MVD_GUI(Tk):
    
    def __init__(self):
        super().__init__()
        self.title("Simulador MVD (Máquina Virtual Didática)")
        self.geometry("1000x700")
        
        self.mvd = None  # This will be initialized in main.py
        self.filepath = None
        self.running_fast = False
        self.LABEL_COL_WIDTH = 4

        self.criar_widgets()
        self._set_controls_state("INICIAL")

    def criar_widgets(self):
        frame_controles = Frame(self, bd=2, relief='raised')
        frame_controles.pack(side='top', fill='x', padx=5, pady=5)

        self.btn_load = Button(frame_controles, text="Carregar Arquivo (.obj)", command=self.carregar_arquivo)
        self.btn_load.pack(side='left', padx=5, pady=5)

        self.btn_run = Button(frame_controles, text="Executar", command=self.executar_direto, bg="#c0ffc0")
        self.btn_run.pack(side='left', padx=5, pady=5)

        self.btn_step = Button(frame_controles, text="Passo-a-Passo", command=self.executar_passo)
        self.btn_step.pack(side='left', padx=5, pady=5)

        self.btn_stop = Button(frame_controles, text="Parar", command=self.parar_execucao, bg="#ffc0c0")
        self.btn_stop.pack(side='left', padx=5, pady=5)

        self.btn_reset = Button(frame_controles, text="Resetar", command=self.resetar_mvd)
        self.btn_reset.pack(side='left', padx=5, pady=5)

        self.status_label = Label(frame_controles, text="Nenhum arquivo carregado.", bd=1, relief='sunken', anchor='w')
        self.status_label.pack(side='right', fill='x', expand=True, padx=5, pady=5)

        frame_principal = PanedWindow(self, orient='horizontal', sashrelief='raised', sashwidth=5)
        frame_principal.pack(fill='both', expand=True, padx=5, pady=5)

        frame_codigo = Frame(frame_principal, bd=2, relief='sunken')
        # largura desejada inicial para o painel de código (favorece o código)
        frame_codigo.config(width=700)
        Label(frame_codigo, text="Programa (Memória P)").pack(side='top', fill='x')
        scrollbar_codigo = Scrollbar(frame_codigo, orient='vertical')
        self.program_listbox = Listbox(frame_codigo, yscrollcommand=scrollbar_codigo.set, font=("Courier", 10))
        scrollbar_codigo.config(command=self.program_listbox.yview)
        scrollbar_codigo.pack(side='right', fill='y')
        self.program_listbox.pack(side='left', fill='both', expand=True)
        # adiciona o painel de código com minsize maior
        frame_principal.add(frame_codigo, minsize=600)

        frame_pilha = Frame(frame_principal, bd=2, relief='sunken')
        # largura menor para painel da pilha (reduz o espaço ocupado)
        frame_pilha.config(width=300)
        Label(frame_pilha, text="Pilha de Dados (Memória M)").pack(side='top', fill='x')
        scrollbar_pilha = Scrollbar(frame_pilha, orient='vertical')
        self.stack_listbox = Listbox(frame_pilha, yscrollcommand=scrollbar_pilha.set, font=("Courier", 10))
        scrollbar_pilha.config(command=self.stack_listbox.yview)
        scrollbar_pilha.pack(side='right', fill='y')
        self.stack_listbox.pack(side='left', fill='both', expand=True)
        # adiciona o painel da pilha com minsize menor
        frame_principal.add(frame_pilha, minsize=200)

        frame_io = Frame(self, height=150, bd=2, relief='sunken')
        frame_io.pack(side='bottom', fill='x', padx=5, pady=5)
        frame_io.pack_propagate(False)

        self.input_frame = Frame(frame_io)
        Label(self.input_frame, text="Entrada (RD):", font=("Courier", 10, "bold")).pack(side='left', padx=5)
        self.input_entry = Entry(self.input_frame, font=("Courier", 10), width=20)
        self.input_entry.pack(side='left', padx=5)
        self.input_submit = Button(self.input_frame, text="Submeter", command=self.submeter_entrada)
        self.input_submit.pack(side='left', padx=5)
        self.input_entry.bind("<Return>", (lambda event: self.submeter_entrada()))

        Label(frame_io, text="Saída (PRN) e Erros:", anchor='nw').pack(side='top', fill='x', padx=5)
        self.output_text = scrolledtext.ScrolledText(frame_io, height=5, font=("Courier", 10), wrap='word', state='disabled')
        self.output_text.pack(fill='both', expand=True, padx=5, pady=5)

    def _set_controls_state(self, state):
        if state == "INICIAL":
            self.btn_load.config(state='normal')
            self.btn_run.config(state='disabled')
            self.btn_step.config(state='disabled')
            self.btn_stop.config(state='disabled')
            self.btn_reset.config(state='disabled')
        elif state == "CARREGADO":
            self.btn_load.config(state='normal')
            self.btn_run.config(state='normal')
            self.btn_step.config(state='normal')
            self.btn_stop.config(state='disabled')
            self.btn_reset.config(state='normal')
        elif state == "RODANDO":
            self.btn_load.config(state='disabled')
            self.btn_run.config(state='disabled')
            self.btn_step.config(state='disabled')
            self.btn_stop.config(state='normal')
            self.btn_reset.config(state='disabled')
        elif state == "AGUARDANDO_INPUT":
            self.btn_load.config(state='disabled')
            self.btn_run.config(state='disabled')
            self.btn_step.config(state='disabled')
            self.btn_stop.config(state='normal')
            self.btn_reset.config(state='normal')

    def log_output(self, message, is_error=False):
        self.output_text.config(state='normal')
        tag = "error" if is_error else "output"
        self.output_text.tag_configure("error", foreground="red")
        self.output_text.tag_configure("output", foreground="blue")
        self.output_text.insert('end', f"{message}\n", (tag,))
        self.output_text.see('end')
        self.output_text.config(state='disabled')

    def atualizar_ui(self):
        if self.mvd.i < self.program_listbox.size():
            self.program_listbox.selection_clear(0, 'end')
            self.program_listbox.selection_set(self.mvd.i)
            self.program_listbox.see(self.mvd.i)
            self.program_listbox.activate(self.mvd.i)

        self.stack_listbox.delete(0, 'end')
        limite_pilha = max(50, self.mvd.s + 20)
        
        indices_para_mostrar = set(range(20))
        indices_para_mostrar.update(range(max(0, self.mvd.s - 20), self.mvd.s + 20))
        
        last_idx = -2
        for i in sorted(list(indices_para_mostrar)):
            if i >= len(self.mvd.M):
                break
            
            if i != last_idx + 1:
                self.stack_listbox.insert('end', f"...")
            
            val = self.mvd.M[i]
            prefixo = "s ->" if i == self.mvd.s else "    "
            self.stack_listbox.insert('end', f"{prefixo} M[{i}]: {val}")
            
            last_idx = i

        if self.mvd.s >= 0:
            self.stack_listbox.see(self.stack_listbox.size() - 1)

    def carregar_arquivo(self):
        filepath = filedialog.askopenfilename(
            title="Selecionar Arquivo .obj",
            filetypes=(("OBJ files", "*.obj"), ("All files", "*.*"))
        )
        if not filepath:
            return

        self.filepath = filepath
        self.resetar_mvd()
        
    def resetar_mvd(self):
        self.running_fast = False
        self.mvd.resetar()

        self.program_listbox.delete(0, 'end')
        self.stack_listbox.delete(0, 'end')
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, 'end')
        self.output_text.config(state='disabled')
        self.input_frame.pack_forget()

        if self.filepath:
            try:
                self.mvd.carregar_programa(self.filepath)
                
                for i, (mnem, a1, a2) in enumerate(self.mvd.P):
                    a1_str = str(a1) if a1 is not None else ""
                    a2_str = str(a2) if a2 is not None else ""
                    label = None
                    if hasattr(self.mvd, "labels_by_index") and i < len(self.mvd.labels_by_index):
                        label = self.mvd.labels_by_index[i]
                    label_display = ""
                    if label:
                        # remove espaços e mantém múltiplos rótulos separados por vírgula
                        label_display = str(label)
                        if len(label_display) > self.LABEL_COL_WIDTH:
                            label_display = label_display[:self.LABEL_COL_WIDTH-1] + "…"
                    # formatação com coluna fixa para rótulo, separador de 2 espaços
                    self.program_listbox.insert(
                        'end',
                        f"{i:03d}: {label_display:<{self.LABEL_COL_WIDTH}}  {mnem:<8} {a1_str:<5} {a2_str:<5}"
                    )
                
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
        self.run_loop()

    def run_loop(self):
        if not self.running_fast:
            return
            
        status, data = self.executar_passo(is_direct_run=True)
        
        if status == "RUNNING" or status == "PRN_OUTPUT":
            self.after(1, self.run_loop) 

    def parar_execucao(self):
        self.running_fast = False
        self.mvd.running = False
        self._set_controls_state("CARREGADO")
        self.status_label.config(text="Execução parada pelo usuário.")
        self.input_frame.pack_forget()

    def executar_passo(self, is_direct_run=False):
        if not self.mvd.running and not self.mvd.aguardando_input:
            self.status_label.config(text="Execução finalizada.")
            return "HALTED", None

        try:
            status, data = self.mvd.executar_passo()
        except Exception as e:
            status, data = "ERROR", str(e)
            
        self.atualizar_ui() 

        if status == "RUNNING":
            if not is_direct_run:
                self.status_label.config(text=f"Instrução {self.mvd.i} executada.")
                self._set_controls_state("CARREGADO")
        
        elif status == "HALTED":
            self.running_fast = False
            self.status_label.config(text="Execução Finalizada (HLT).")
            self._set_controls_state("CARREGADO")
            self.btn_run.config(state='disabled')
            self.btn_step.config(state='disabled')
        
        elif status == "NEED_INPUT":
            # se vier de "executar tudo" (is_direct_run == True), mantém running_fast=True
            # para que, após o usuário submeter a entrada, o run_loop seja reiniciado automaticamente.
            if not is_direct_run:
                self.running_fast = False
            self.status_label.config(text="Aguardando entrada (RD)...")
            self._set_controls_state("AGUARDANDO_INPUT")
            self.input_frame.pack(side='top', fill='x', padx=5, pady=5)
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
            self.btn_run.config(state='disabled')
            self.btn_step.config(state='disabled')
            
        return status, data

    def submeter_entrada(self):
        valor = self.input_entry.get()
        self.input_entry.delete(0, 'end')
        self.input_frame.pack_forget()
        
        self.mvd.fornecer_entrada(valor)
        
        if self.running_fast:
            self._set_controls_state("RODANDO")
            self.status_label.config(text="Executando...")
            self.run_loop()
        else:
            self._set_controls_state("CARREGADO")
            self.status_label.config(text="Entrada recebida. Pronto para o próximo passo.")
            self.atualizar_ui()