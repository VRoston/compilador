class TabelaSimbolos:
    def __init__(self):
        self.escopos = [{}]  # Stack of scopes
        self.nivel_atual = 0  # Current scope level
        self.endereco_memoria = 0  # Memory address counter (início em 0 [cite: 2419, 2643])
        self.rotulos_subrotinas = {} # Para guardar rótulos de JMP de subrotinas

    def adicionar_simbolo(self, nome, tipo=None, rotulo=None):
        if nome in self.escopos[-1]:
            raise ValueError(f"símbolo '{nome}' já declarado no escopo atual.")
        
        memoria = None
        if tipo in ['inteiro', 'booleano']:
            memoria = self.endereco_memoria
            self.endereco_memoria += 1  # Aloca 1 "palavra" por variável 
        
        if tipo in ['procedimento', 'funcao inteiro', 'funcao booleano']:
             self.rotulos_subrotinas[nome] = rotulo

        self.escopos[-1][nome] = {
            'nome': nome,
            'escopo': self.nivel_atual,
            'tipo': tipo,
            'memoria': memoria, # Endereço da variável (ex: 0, 1, 2...)
            'rotulo': rotulo    # Rótulo de início da sub-rotina (ex: L1)
        }

    def buscar_simbolo(self, nome):
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        raise ValueError(f"símbolo '{nome}' não declarado dentro do escopo.")
        # O código abaixo estava inalcançável no seu arquivo original
        # for escopo in reversed(self.escopos):
        #    ...
                    
    def entrar_escopo(self):
        self.escopos.append({})
        self.nivel_atual += 1
        # Zerar o endereço de memória local? O PDF sugere endereçamento contínuo [cite: 2642]
        # Vamos manter contínuo por enquanto, como no exemplo da Fig 8.5 [cite: 2641]

    def sair_escopo(self):
        if len(self.escopos) > 1:
            # Precisamos saber quantas variáveis locais foram alocadas para desalocar
            vars_locais = sum(1 for simbolo in self.escopos[-1].values() if simbolo['tipo'] in ['inteiro', 'booleano'])
            
            # Ajusta o ponteiro de memória global para reutilizar endereços
            self.endereco_memoria -= vars_locais

            self.escopos.pop()
            self.nivel_atual -= 1
            return vars_locais # Retorna o número de vars a desalocar
        return 0

    def get_memoria_offset_local(self):
        """Retorna o endereço base para variáveis locais do escopo atual."""
        # No modelo do PDF (pág 73 [cite: 2642]), o endereçamento é contínuo.
        # A variável 'z' (local) tem endereço 2, após 'x' (global) ser 0 e 'y' (global) ser 1.
        return self.endereco_memoria