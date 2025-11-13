# maquina_virtual.py
# Máquina Virtual para executar código MVD gerado pelo compilador

import sys

class MaquinaVirtual:
    def __init__(self, arquivo, debug=False):
        with open(arquivo, 'r') as f:
            self.codigo = [linha.strip() for linha in f if linha.strip()]
        self.memoria = [0] * 1000
        self.pilha = []
        self.pc = 0
        self.rotulos = self._mapear_rotulos()
        self.debug = debug
        self.instr_count = 0

    def _mapear_rotulos(self):
        """Mapeia rótulos (Lx NULL) para índices."""
        rotulos = {}
        for i, linha in enumerate(self.codigo):
            if linha.startswith("L") and "NULL" in linha:
                nome = linha.split()[0]
                rotulos[nome] = i
        return rotulos

    def _ler_valor(self, mensagem="Digite um valor: "):
        while True:
            try:
                return int(input(mensagem))
            except ValueError:
                print("Valor inválido. Digite um número inteiro.")

    def rodar(self):
        """Executa o código MVD."""
        while self.pc < len(self.codigo):
            linha = self.codigo[self.pc]
            partes = linha.split()
            op = partes[0].upper()
            self.instr_count += 1

            if self.instr_count > 10000:
                print("Erro: Execução interrompida (loop infinito detectado).")
                break

            # Ignorar rótulos
            if op.startswith("L") and "NULL" in linha:
                self.pc += 1
                continue

            if self.debug:
                print(f"[{self.pc:03}] {linha:<15} | PILHA: {self.pilha} | MEM[0..10]: {self.memoria[:10]}")

            # === Instruções ===
            try:
                if op == "START":
                    pass
                elif op in ("HLT", "HALT"):
                    print("Execução finalizada.")
                    break
                elif op == "ALLOC":
                    # Pode ser ALLOC <n> ou ALLOC <base> <n>
                    if len(partes) == 2:
                        base = 0
                        n = int(partes[1])
                    else:
                        base = int(partes[1])
                        n = int(partes[2])
                    for i in range(n):
                        self.pilha.append(self.memoria[base + i])
                elif op == "DALLOC":
                    if len(partes) == 2:
                        base = 0
                        n = int(partes[1])
                    else:
                        base = int(partes[1])
                        n = int(partes[2])
                    for i in range(n - 1, -1, -1):
                        self.memoria[base + i] = self.pilha.pop()
                elif op == "LDC":
                    self.pilha.append(int(partes[1]))
                elif op == "LDV":
                    self.pilha.append(self.memoria[int(partes[1])])
                elif op == "STR":
                    endereco = int(partes[1])
                    self.memoria[endereco] = self.pilha.pop()
                elif op == "ADD":
                    b, a = self.pilha.pop(), self.pilha.pop()
                    self.pilha.append(a + b)
                elif op == "SUB":
                    b, a = self.pilha.pop(), self.pilha.pop()
                    self.pilha.append(a - b)
                elif op == "MULT":
                    b, a = self.pilha.pop(), self.pilha.pop()
                    self.pilha.append(a * b)
                elif op in ("DIV", "DIVI"):
                    b, a = self.pilha.pop(), self.pilha.pop()
                    self.pilha.append(a // b if b != 0 else 0)
                elif op == "AND":
                    b, a = self.pilha.pop(), self.pilha.pop()
                    self.pilha.append(1 if a and b else 0)
                elif op == "OR":
                    b, a = self.pilha.pop(), self.pilha.pop()
                    self.pilha.append(1 if a or b else 0)
                elif op == "NOT":
                    a = self.pilha.pop()
                    self.pilha.append(0 if a else 1)
                elif op == "CMA":
                    b, a = self.pilha.pop(), self.pilha.pop()
                    self.pilha.append(1 if a > b else 0)
                elif op == "CME":
                    b, a = self.pilha.pop(), self.pilha.pop()
                    self.pilha.append(1 if a < b else 0)
                elif op == "CMEQ":
                    b, a = self.pilha.pop(), self.pilha.pop()
                    self.pilha.append(1 if a == b else 0)
                elif op == "CMAQ":
                    b, a = self.pilha.pop(), self.pilha.pop()
                    self.pilha.append(1 if a >= b else 0)
                elif op == "CMEE":
                    b, a = self.pilha.pop(), self.pilha.pop()
                    self.pilha.append(1 if a <= b else 0)
                elif op == "JMP":
                    label = partes[1]
                    self.pc = self.rotulos.get(label, self.pc)
                    continue
                elif op == "JMPF":
                    cond = self.pilha.pop()
                    label = partes[1]
                    if cond == 0:
                        self.pc = self.rotulos.get(label, self.pc)
                        continue
                elif op == "RD":
                    valor = self._ler_valor()
                    self.pilha.append(valor)
                elif op == "PRN":
                    if self.pilha:
                        print(self.pilha[-1])
                    else:
                        print("Erro: pilha vazia em PRN")
                else:
                    print(f"Instrução desconhecida: {linha}")
                    break
            except Exception as e:
                print(f"Erro em '{linha}': {e}")
                break

            self.pc += 1


# ============================ MAIN ============================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python maquina_virtual.py <arquivo.mvd> [--debug]")
        sys.exit(1)

    arquivo = sys.argv[1]
    debug = "--debug" in sys.argv
    mv = MaquinaVirtual(arquivo, debug=debug)
    mv.rodar()
