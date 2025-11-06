# maquina_virtual.py
import sys

class MaquinaVirtual:
    def __init__(self, arquivo, debug=False, cpu_limit=10000, mem_limit=1000):
        self.debug = debug
        self.cpu_limit = cpu_limit
        self.mem_limit = mem_limit
        self.ciclos = 0

        with open(arquivo, 'r') as f:
            self.codigo = [linha.strip() for linha in f if linha.strip()]

        self.memoria = [0] * self.mem_limit
        self.pilha = []
        self.pc = 0
        self.rotulos = self._mapear_rotulos()

    def _mapear_rotulos(self):
        rotulos = {}
        for i, linha in enumerate(self.codigo):
            partes = linha.split()
            if partes[0].endswith(':'):
                rotulos[partes[0][:-1]] = i
            elif len(partes) == 2 and partes[1] == "NULL":
                rotulos[partes[0]] = i
        return rotulos

    def rodar(self):
        while self.pc < len(self.codigo):
            if self.ciclos > self.cpu_limit:
                print("\n⛔ ERRO: Limite de CPU excedido! (possível loop infinito)")
                break

            instrucao = self.codigo[self.pc]
            partes = instrucao.split()
            op = partes[0].upper()

            # pula labels
            if op.endswith(":") or (len(partes) == 2 and partes[1] == "NULL"):
                self.pc += 1
                continue

            if self.debug:
                print(f"[{self.pc:03}] {instrucao:<15} | PILHA: {self.pilha} | MEM[0..10]: {self.memoria[:10]}")

            if op == 'START':
                pass
            elif op == 'LDC':
                self.pilha.append(int(partes[1]))
            elif op == 'LDV':
                addr = int(partes[1])
                self._checar_mem(addr)
                self.pilha.append(self.memoria[addr])
            elif op == 'STR':
                addr = int(partes[1])
                self._checar_mem(addr)
                val = self.pilha.pop()
                self.memoria[addr] = val
            elif op == 'ADD':
                b, a = self.pilha.pop(), self.pilha.pop()
                self.pilha.append(a + b)
            elif op == 'SUB':
                b, a = self.pilha.pop(), self.pilha.pop()
                self.pilha.append(a - b)
            elif op == 'MULT':
                b, a = self.pilha.pop(), self.pilha.pop()
                self.pilha.append(a * b)
            elif op in ['DIV', 'DIVI']:
                b, a = self.pilha.pop(), self.pilha.pop()
                self.pilha.append(a // b if b != 0 else 0)
            elif op == 'RD':
                val = int(input("Digite um valor: "))
                self.pilha.append(val)
            elif op == 'PRN':
                print(self.pilha[-1] if self.pilha else 0)
            elif op == 'JMP':
                self.pc = self.rotulos.get(partes[1], self.pc)
                continue
            elif op == 'JMPF':
                cond = self.pilha.pop()
                if cond == 0:
                    self.pc = self.rotulos.get(partes[1], self.pc)
                    continue
            elif op == 'ALLOC':
                base = int(partes[1])
                n = int(partes[2]) if len(partes) > 2 else 1
                for i in range(n):
                    self.pilha.append(self.memoria[base + i])
            elif op == 'DALLOC':
                base = int(partes[1])
                n = int(partes[2]) if len(partes) > 2 else 1
                for i in range(n - 1, -1, -1):
                    self._checar_mem(base + i)
                    self.memoria[base + i] = self.pilha.pop()
            elif op in ['CMA', 'CME', 'CMAQ', 'CMEQ', 'CMEQ_EQ', 'CMEQ_EQ_NOT']:
                b, a = self.pilha.pop(), self.pilha.pop()
                if op == 'CMA': self.pilha.append(1 if a > b else 0)
                elif op == 'CME': self.pilha.append(1 if a < b else 0)
                elif op == 'CMAQ': self.pilha.append(1 if a >= b else 0)
                elif op == 'CMEQ': self.pilha.append(1 if a <= b else 0)
                elif op == 'CMEQ_EQ': self.pilha.append(1 if a == b else 0)
                elif op == 'CMEQ_EQ_NOT': self.pilha.append(1 if a != b else 0)
            elif op == 'AND':
                b, a = self.pilha.pop(), self.pilha.pop()
                self.pilha.append(1 if (a and b) else 0)
            elif op == 'OR':
                b, a = self.pilha.pop(), self.pilha.pop()
                self.pilha.append(1 if (a or b) else 0)
            elif op == 'NOT':
                a = self.pilha.pop()
                self.pilha.append(0 if a else 1)
            elif op in ['HLT', 'HALT']:
                print("✅ Execução finalizada com sucesso.")
                break
            else:
                print(f"Instrução desconhecida: {instrucao}")
                break

            self.pc += 1
            self.ciclos += 1

    def _checar_mem(self, addr):
        if addr < 0 or addr >= self.mem_limit:
            raise RuntimeError(f"Endereço de memória inválido: {addr}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python maquina_virtual.py <arquivo.mvd> [--debug]")
        sys.exit(1)

    debug = "--debug" in sys.argv
    mv = MaquinaVirtual(sys.argv[1], debug=debug)
    mv.rodar()