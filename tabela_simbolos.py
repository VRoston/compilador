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
                    
    def entrar_escopo(self):
        self.escopos.append({})
        self.nivel_atual += 1

    def sair_escopo(self):
        if len(self.escopos) > 1:
            self.escopos.pop()
            self.nivel_atual -= 1

def posfix(expressao):
    order = {'*': 1, 'div': 1,                                  # Multiplicação e Divisão têm precedência 1
             '+': 2, '-': 2,                                    # Adição e Subtração têm precedência 2
             '<': 3, '<=': 3, '>': 3, '>=': 3, '=': 3, '!=': 3, # Relações têm precedência 3
             'nao': 4,                                          # Negação tem precedência 4
             'e': 5,                                            # Conjunção tem precedência 5
             'ou': 6}                                           # Disjunção tem precedência 6
    
    stack = []
    posfixa = []

    for i in range(len(expressao)):
        if expressao[i] not in order and expressao[i] not in ['(', ')']:
            posfixa.append(expressao[i])
            if stack and stack[-1] in ['+u', '-u']:
                posfixa.append(stack.pop())
        
        if expressao[i] == '(':
            stack.append(expressao[i])

        if expressao[i] == ')':
            while stack and stack[-1] != '(':
                posfixa.append(stack.pop())
            stack.pop()
            if stack and stack[-1] == 'nao':
                posfixa.append(stack.pop())
            if stack and stack[-1] in ['+u', '-u']:
                posfixa.append(stack.pop())

        if expressao[i] in ['+', '-']:
            if expressao[i-1] in ['+', '-', '*', 'div', '<', '<=', '>', '>=', '=', '!=', 'e', 'ou', '(', None]:
                stack.append(f'{expressao[i]}u')  # Operador unário
            else:
                while stack and stack[-1] != '(' and order[expressao[i]] >= order[stack[-1]]:
                    posfixa.append(stack.pop())
                stack.append(expressao[i])
        
        elif expressao[i] in ['*', 'div', '<', '<=', '>', '>=', '=', '!=', 'e', 'ou', 'nao']:
            while stack and stack[-1] != '(' and order[expressao[i]] >= order[stack[-1]]:
                posfixa.append(stack.pop())
            stack.append(expressao[i])

    while stack:
        posfixa.append(stack.pop())

    if None in posfixa:
        posfixa.remove(None)
    
    return posfixa

