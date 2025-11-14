# ...existing code...
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
import threading
import time
import selectors

class VirtualMachineInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Interface da Máquina Virtual")
        self.file_path = None
        self.proc = None
        self.proc_thread = None

        # Barra de botões no topo
        topbar = tk.Frame(root, bg="#e0e0e0")
        topbar.pack(fill="x")

        btn_abrir = tk.Button(topbar, text="Abrir MVD", command=self.abrir_arquivo)
        btn_abrir.pack(side="left", padx=2, pady=2)
        btn_executar = tk.Button(topbar, text="Executar", command=self.executar_maquina_virtual)
        btn_executar.pack(side="left", padx=2, pady=2)
        btn_parar = tk.Button(topbar, text="Parar", command=self.parar_execucao)
        btn_parar.pack(side="left", padx=2, pady=2)

        # Painel com código (à esquerda) e saída (à direita)
        paned = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True, padx=2, pady=2)

        # Área de código .mvd (read-only)
        self.code_text = scrolledtext.ScrolledText(paned, wrap="none", font=("Consolas", 11), width=60, bg="#ffffff")
        self.code_text.config(state="disabled")
        paned.add(self.code_text)

        # Área de saída / execução
        right_frame = tk.Frame(paned)
        paned.add(right_frame)

        self.output = scrolledtext.ScrolledText(right_frame, wrap="word", font=("Consolas", 11), height=20, bg="#f0f0f0")
        self.output.pack(fill="both", expand=True, padx=2, pady=2)
        self.output.config(state="disabled")

        # Entrada para enviar valores ao processo (quando a MV pedir input)
        input_frame = tk.Frame(right_frame)
        input_frame.pack(fill="x", padx=2, pady=(0,4))
        self.input_entry = tk.Entry(input_frame, font=("Consolas", 11))
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0,4))
        self.input_entry.bind("<Return>", self.enviar_input)
        send_btn = tk.Button(input_frame, text="Enviar", command=self.enviar_input)
        send_btn.pack(side="right")

    def _parse_mvd_lines_to_columns(self, lines):
        """
        Parse each linha do .mvd em 3 colunas:
          - label (se existir, ex: L0 NULL)
          - instrução/opcode
          - operandos/resto da linha
        Retorna lista de tuplas (label, instr, operand).
        """
        rows = []
        for raw in lines:
            line = raw.rstrip("\n")
            if not line.strip():
                rows.append(("", "", ""))  # linha vazia preservada
                continue
            tokens = line.split()
            # Caso rótulo com NULL (rótulos aparecem como "Lx NULL")
            if tokens[0].startswith("L") and "NULL" in line:
                label = tokens[0]
                # resto pode ter "NULL" como token[1] e nada mais
                instr = tokens[1] if len(tokens) > 1 else ""
                operand = " ".join(tokens[2:]) if len(tokens) > 2 else ""
                rows.append((label, instr, operand))
                continue
            # Caso linha normal: primeiro token = instr, resto = operandos
            instr = tokens[0]
            operand = " ".join(tokens[1:]) if len(tokens) > 1 else ""
            rows.append(("", instr, operand))
        return rows

    def _format_columns(self, rows, max_label=12, max_instr=12):
        """
        Formata as colunas em texto alinhado:
         [label padded]  [instr padded]  [operand]
        Ajusta larguras pelo máximo observado (limitadas pelos parâmetros).
        """
        # computar larguras observadas
        w_label = min(max_label, max((len(r[0]) for r in rows), default=0))
        w_instr = min(max_instr, max((len(r[1]) for r in rows), default=0))
        lines = []
        header = f"{'LABEL'.ljust(w_label)}  {'INSTR'.ljust(w_instr)}  OPERAND"
        sep = "-" * len(header)
        lines.append(header)
        lines.append(sep)
        for label, instr, operand in rows:
            if not label and not instr and not operand:
                lines.append("")  # keep blank line
                continue
            # if label exists and is the only thing (e.g., "L0 NULL"), show NULL in instr column
            lines.append(f"{label.ljust(w_label)}  {instr.ljust(w_instr)}  {operand}")
        return "\n".join(lines)

    def abrir_arquivo(self):
        caminho = filedialog.askopenfilename(
            filetypes=[("Arquivos MVD", "*.mvd"), ("Todos os arquivos", "*.*")]
        )
        if caminho:
            self.file_path = caminho
            self.root.title(f"Interface da Máquina Virtual - {os.path.basename(caminho)}")
            # Mostrar conteúdo do arquivo .mvd na área de código, formatado em colunas
            try:
                with open(caminho, "r") as f:
                    raw_lines = f.readlines()
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível ler o arquivo: {e}")
                return

            rows = self._parse_mvd_lines_to_columns(raw_lines)
            formatted = self._format_columns(rows)

            self.code_text.config(state="normal")
            self.code_text.delete(1.0, tk.END)
            self.code_text.insert(tk.END, formatted)
            self.code_text.config(state="disabled")
            # Limpa área de saída
            self.mostrar_saida("")

    def executar_maquina_virtual(self):
        if not self.file_path:
            messagebox.showwarning("Aviso", "Selecione um arquivo MVD antes de executar.")
            return
        if self.proc and self.proc.poll() is None:
            messagebox.showinfo("Info", "Execução já em andamento.")
            return

        # Inicia subprocesso em modo binário/unbuffered para permitir leitura imediata via os.read
        cmd = ["python3", "maquina_virtual.py", self.file_path]
        try:
            self.proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0  # unbuffered binary
            )
        except Exception as e:
            self.mostrar_saida(f"Erro ao executar: {e}")
            return

        self.mostrar_saida("=== Execução iniciada ===\n")

        def reader():
            sel = selectors.DefaultSelector()
            try:
                if self.proc.stdout:
                    sel.register(self.proc.stdout, selectors.EVENT_READ)
                if self.proc.stderr:
                    sel.register(self.proc.stderr, selectors.EVENT_READ)

                # loop até processo terminar e até não restar dados
                while True:
                    if self.proc.poll() is not None:
                        # processo terminou, ainda consumir tudo que restou
                        events = sel.select(timeout=0.1)
                        for key, _ in events:
                            try:
                                data = os.read(key.fileobj.fileno(), 4096)
                                if data:
                                    text = data.decode("utf-8", errors="replace")
                                    self._append_output_threadsafe(text)
                            except Exception:
                                pass
                        break

                    events = sel.select(timeout=0.1)
                    for key, _ in events:
                        try:
                            data = os.read(key.fileobj.fileno(), 4096)
                            if data:
                                text = data.decode("utf-8", errors="replace")
                                self._append_output_threadsafe(text)
                        except Exception:
                            pass
                    time.sleep(0.01)

                # make sure to flush any remaining bytes
                events = sel.select(timeout=0.1)
                for key, _ in events:
                    try:
                        data = os.read(key.fileobj.fileno(), 4096)
                        if data:
                            text = data.decode("utf-8", errors="replace")
                            self._append_output_threadsafe(text)
                    except Exception:
                        pass

                code = self.proc.returncode
                self._append_output_threadsafe(f"\n=== Execução finalizada (exit {code}) ===\n")
            except Exception as e:
                self._append_output_threadsafe(f"\nErro na leitura do processo: {e}\n")
            finally:
                try:
                    sel.close()
                except Exception:
                    pass

        self.proc_thread = threading.Thread(target=reader, daemon=True)
        self.proc_thread.start()

    def parar_execucao(self):
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()
                self._append_output_threadsafe("\n=== Processo terminado pelo usuário ===\n")
            except Exception as e:
                self._append_output_threadsafe(f"\nErro ao terminar processo: {e}\n")
        else:
            messagebox.showinfo("Info", "Nenhuma execução em andamento.")

    def enviar_input(self, event=None):
        if not self.proc or self.proc.poll() is not None:
            messagebox.showinfo("Info", "Nenhuma execução em andamento para enviar input.")
            return
        valor = self.input_entry.get()
        try:
            # Envia bytes com newline e faz flush
            self.proc.stdin.write((valor + "\n").encode("utf-8"))
            self.proc.stdin.flush()
            # mostramos o input na saída para feedback
            self._append_output_threadsafe(f">>> {valor}\n")
            self.input_entry.delete(0, tk.END)
        except Exception as e:
            self._append_output_threadsafe(f"\nErro ao enviar input: {e}\n")

    def mostrar_saida(self, saida):
        self.output.config(state="normal")
        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, saida)
        self.output.config(state="disabled")

    def _append_output_threadsafe(self, texto):
        # chamada de background threads para atualizar UI
        self.root.after(0, self._append_output, texto)

    def _append_output(self, texto):
        self.output.config(state="normal")
        self.output.insert(tk.END, texto)
        self.output.see(tk.END)
        self.output.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualMachineInterface(root)
    root.mainloop()
# ...existing code...