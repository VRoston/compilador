import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

class EditorTxt:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor txt")
        self.file_path = None

        # Barra de botões no topo
        topbar = tk.Frame(root, bg="#e0e0e0")
        topbar.pack(fill="x")

        btn_abrir = tk.Button(topbar, text="Abrir", command=self.abrir_arquivo)
        btn_abrir.pack(side="left", padx=2, pady=2)
        btn_salvar = tk.Button(topbar, text="Salvar", command=self.salvar_arquivo)
        btn_salvar.pack(side="left", padx=2, pady=2)
        btn_executar = tk.Button(topbar, text="Executar", command=self.executar_analisador)
        btn_executar.pack(side="left", padx=2, pady=2)

        # Frame para editor, números de linha e scrollbar
        editor_frame = tk.Frame(root)
        editor_frame.pack(expand=1, fill="both")

        # Números de linha (Text)
        self.linenumbers = tk.Text(editor_frame, width=5, padx=4, takefocus=0, border=0,
                                   background="#e0e0e0", state="disabled", font=("Consolas", 12))
        self.linenumbers.pack(side="left", fill="y")

        # Área de texto
        self.text = tk.Text(editor_frame, wrap="word", font=("Consolas", 12), undo=True)
        self.text.pack(side="left", expand=1, fill="both")

        # Scrollbar vertical que controla ambos
        self.vscroll = tk.Scrollbar(editor_frame, orient="vertical", command=self._on_scrollbar)
        self.vscroll.pack(side="right", fill="y")

        # Configura yscrollcommand do text para atualizar a scrollbar e os números
        self.text.configure(yscrollcommand=self._on_text_scroll)

        # Sincroniza mouse wheel para mover ambos
        self.text.bind("<MouseWheel>", self._on_mouse_wheel)      # Windows
        self.text.bind("<Button-4>", self._on_mouse_wheel)        # Linux scroll up
        self.text.bind("<Button-5>", self._on_mouse_wheel)        # Linux scroll down

        # Atualiza números de linha ao modificar texto ou rolar
        self.text.bind("<KeyRelease>", self.update_linenumbers)
        self.text.bind("<Button-1>", self.update_linenumbers)
        self.text.bind("<Configure>", self.update_linenumbers)
        self.text.bind("<FocusIn>", self.update_linenumbers)

        # Área de saída
        self.output = tk.Text(root, wrap="word", font=("Consolas", 11), height=10, bg="#f0f0f0")
        self.output.pack(fill="both", padx=2, pady=2)
        self.output.config(state="disabled")

        self.update_linenumbers()

    # chamada pelo text via yscrollcommand
    def _on_text_scroll(self, first, last):
        # atualiza a scrollbar e sincroniza a view dos números de linha
        try:
            self.vscroll.set(first, last)
            # first é string; converte para float e move a view dos números
            self.linenumbers.yview_moveto(float(first))
        except Exception:
            pass

    # chamada pela scrollbar; args como ('moveto', fraction) ou ('scroll', number, 'units/pages')
    def _on_scrollbar(self, *args):
        # Move o text e os linenumbers com o mesmo comando
        self.text.yview(*args)
        self.linenumbers.yview(*args)

    def _on_mouse_wheel(self, event):
        # Unifica comportamento do scroll entre plataformas
        if event.num == 4:   # linux up
            self.text.yview_scroll(-1, "units")
        elif event.num == 5: # linux down
            self.text.yview_scroll(1, "units")
        else:  # Windows / Mac (event.delta)
            if event.delta > 0:
                self.text.yview_scroll(-1, "units")
            else:
                self.text.yview_scroll(1, "units")
        # atualiza a posição dos números
        first, _ = self.text.yview()
        self.linenumbers.yview_moveto(first)
        # atualizar a scrollbar visual
        self.vscroll.set(*self.text.yview())
        return "break"

    def update_linenumbers(self, event=None):
        # Remove destaque de erro ao digitar
        self.text.tag_remove("erro_destacado", "1.0", tk.END)
        self.linenumbers.config(state="normal")
        self.linenumbers.delete("1.0", tk.END)
        line_count = int(self.text.index('end-1c').split('.')[0])
        linenums = "\n".join(str(i) for i in range(1, line_count + 1))
        self.linenumbers.insert("1.0", linenums)
        self.linenumbers.config(state="disabled")
        # sincroniza posição dos números com o editor (se o editor estiver scrolled)
        try:
            first, _ = self.text.yview()
            self.linenumbers.yview_moveto(first)
            self.vscroll.set(*self.text.yview())
        except Exception:
            pass

    def abrir_arquivo(self):
        caminho = filedialog.askopenfilename(
            filetypes=[("Arquivos txt", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        if caminho:
            with open(caminho, "r", encoding="utf-8") as f:
                conteudo = f.read()
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, conteudo)
            self.file_path = caminho
            self.root.title(f"Editor txt - {os.path.basename(caminho)}")
            self.update_linenumbers()

    def salvar_arquivo(self):
        if not self.file_path:
            caminho = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Arquivos txt", "*.txt"), ("Todos os arquivos", "*.*")]
            )
            if not caminho:
                return
            self.file_path = caminho
        conteudo = self.text.get(1.0, tk.END)
        if conteudo.endswith('\n'):
            conteudo = conteudo[:-1]  # Remove o último '\n'
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(conteudo)
        messagebox.showinfo("Salvo", "Arquivo salvo com sucesso!")

    def executar_analisador(self):
        if not self.file_path:
            messagebox.showwarning("Aviso", "Salve o arquivo antes de executar.")
            return
        try:
            resultado = subprocess.run(
                ["python3", "analisador_sintatico.py", self.file_path],
                capture_output=True, text=True
            )
            saida = resultado.stdout + resultado.stderr
            self.mostrar_saida(saida)
        except Exception as e:
            self.mostrar_saida(f"Erro ao executar: {e}")

    def mostrar_saida(self, saida):
        self.output.config(state="normal")
        self.output.delete(1.0, tk.END)
        linhas_erro = [line for line in saida.splitlines() if "linha" in line]
        if not linhas_erro:
            # Sem erros: exibe mensagem de compilação concluída
            msg = "Compilação concluída sem erros."
            self.output.insert(tk.END, msg + "\n")
            messagebox.showinfo("Compilação", msg)
        else:
            for idx, line in enumerate(linhas_erro, 1):
                self.output.insert(tk.END, line + "\n")
                start = f"{idx}.0"
                end = f"{idx}.end"
                self.output.tag_add("erro", start, end)
            self.output.tag_configure("erro", foreground="red", underline=True)
        self.output.config(state="disabled")
        self.output.bind("<Button-1>", self.on_output_click)

    def on_output_click(self, event):
        # Remove destaque anterior
        self.text.tag_remove("erro_destacado", "1.0", tk.END)
        index = self.output.index(f"@{event.x},{event.y}")
        line_content = self.output.get(f"{index} linestart", f"{index} lineend")
        import re
        match = re.search(r"linha (\d+)", line_content)
        if match:
            linha = int(match.group(1))
            # Move o cursor
            self.text.mark_set("insert", f"{linha}.0")
            self.text.see(f"{linha}.0")
            # Destaca a linha
            self.text.tag_add("erro_destacado", f"{linha}.0", f"{linha}.0 lineend")
            self.text.tag_configure("erro_destacado", background="#ffcccc")

if __name__ == "__main__":
    root = tk.Tk()
    app = EditorTxt(root)
    root.mainloop()