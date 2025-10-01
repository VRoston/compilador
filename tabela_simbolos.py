class TabelaSimbolos:
    def __init__(self):
        self.escopos = [{}]  # Stack of scopes
        self.nivel_atual = 0  # Current scope level
        self.endereco_memoria = 0  # Memory address counter

    def adicionar_simbolo(self, nome, tipo=None):
        if nome in self.escopos[-1]:
            raise ValueError(f"símbolo '{nome}' já declarado no escopo atual.")
        memoria = self.endereco_memoria
        self.endereco_memoria += 4  # Assume 4 bytes per variable
        self.escopos[-1][nome] = {
            'nome': nome,
            'escopo': self.nivel_atual,
            'tipo': tipo,
            'memoria': memoria
        }

    def buscar_simbolo(self, nome):
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        raise ValueError(f"símbolo '{nome}' não declarado dentro do escopo.")
        # Traverse from end to start, set type for variables without type
        for escopo in reversed(self.escopos):
            for simbolo in reversed(list(escopo.values())):
                if simbolo['tipo'] is None:
                    simbolo['tipo'] = tipo
                else:
                    break  # Stop at first typed symbol
                    
    def entrar_escopo(self):
        self.escopos.append({})
        self.nivel_atual += 1

    def sair_escopo(self):
        if len(self.escopos) > 1:
            self.escopos.pop()
            self.nivel_atual -= 1