class TabelaSimbolos:
    def __init__(self):
        self.escopos = [{}]  # Pilha de escopos, começando com global

    def adicionar_simbolo(self, nome, tipo):
        if nome in self.escopos[-1]:
            raise ValueError(f"Símbolo '{nome}' já declarado no escopo atual.")
        self.escopos[-1][nome] = {'tipo': tipo}

    def buscar_simbolo(self, nome):
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        return None

    def entrar_escopo(self):
        self.escopos.append({})

    def sair_escopo(self):
        if len(self.escopos) > 1:
            self.escopos.pop()