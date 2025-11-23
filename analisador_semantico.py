class TabelaSimbolos:
    def __init__(self):
        self.escopos = [{}]  # lista de escopos (pilha): escopo global começa aqui
        self.nivel_atual = 0  # nível atual do escopo
        self.endereco_memoria = 1  # contador de endereços para variáveis

    def adicionar_simbolo(self, nome, tipo=None, rotulo=None):  # adiciona identificador no escopo atual
        if nome in self.escopos[-1]:
            raise ValueError(f"símbolo '{nome}' já declarado no escopo atual.")
        memoria = self.endereco_memoria
        self.escopos[-1][nome] = {
            'nome': nome,
            'escopo': self.nivel_atual,
            'tipo': tipo,
            'memoria': memoria,
            'rotulo': rotulo
        }
        if self.escopos[-1][nome]['tipo'] in ['inteiro', 'booleano']:   # tipos simples ocupam 1 posição
            self.endereco_memoria += 1

    def buscar_simbolo(self, nome): # busca identificador do escopo atual para trás
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        raise ValueError(f"símbolo '{nome}' não declarado dentro do escopo.")
                    
    def entrar_escopo(self):        # cria um novo escopo (bloco, função, procedimento)
        self.escopos.append({})
        self.nivel_atual += 1

    def sair_escopo(self):          # remove último escopo e devolve símbolos retirados
        pop = []
        dalloc = None
        if len(self.escopos) >= 1:
            dalloc = self.escopos.pop()
            self.nivel_atual -= 1

        for simbolo in dalloc:      # coleta símbolos para desalocar
            pop.append(simbolo)
        
        for simbolo in pop:         # decrementa contador de memória
            dalloc.pop(simbolo)
            self.endereco_memoria -= 1
                
        return dalloc

def tipo_expressao(posfixa, tabela):    # determina o tipo final da expressão pós-fixa
    """
    Determina o tipo de retorno de uma expressão pós-fixa.
    """
    
    # 1. Define os nossos operadores
    # Usar um Set é mais rápido para 'in'
    OPERADORES_UNARIOS = {'+u', '-u', 'nao'}    # operadores que usam 1 operando
    OPERADORES_BINARIOS = {                     # operadores que usam 2 operandos
        '+', '-', '*', 'div', 
        '<', '<=', '>', '>=', '=', '!=', 
        'e', 'ou'
    }
    
    # 2. Cria a nossa pilha (stack) de tipos
    pilha_tipos = []                            # pilha para validar tipos
    
    # 3. Itera pela expressão pós-fixa UMA VEZ
    for token in posfixa:
        
        # Caso 1: O token é um OPERANDO (um literal ou variável)
        if token not in OPERADORES_UNARIOS and token not in OPERADORES_BINARIOS:
            tipo_token = ''
            
            if token in ['verdadeiro', 'falso']:
                tipo_token = 'booleano'         # literal booleano
            elif token.isnumeric():
                tipo_token = 'inteiro'          # literal inteiro
            else:
                # É uma variável, busca na tabela de símbolos
                try:
                    simbolo = tabela.buscar_simbolo(token)  # Ex: buscar 'a'
                    tipo_token = simbolo['tipo']            # Ex: 'inteiro'
                    if tipo_token in ['funcao inteiro', 'funcao booleano']: # funções retornam tipo simples
                        tipo_token = tipo_token.replace('funcao ', '')
                except Exception as e:
                    raise ValueError(f"Erro ao buscar símbolo '{token}': {e}")
            
            # Empilha o TIPO do operando
            pilha_tipos.append(tipo_token)
        
        # Caso 2: O token é um OPERADOR
        else:
            operador = token
            try:
                # --- Lógica para Operadores Unários ---
                if operador in OPERADORES_UNARIOS:
                    tipo1 = pilha_tipos.pop()
                    
                    if operador == 'nao':
                        if tipo1 != 'booleano':
                            raise TypeError(f"Erro de tipo: O operador 'nao' espera 'booleano', mas recebeu '{tipo1}'")
                        pilha_tipos.append('booleano')      # Resultado de 'nao' é booleano
                    
                    else: # +u ou -u (unário)
                        if tipo1 != 'inteiro':
                            raise TypeError(f"Erro de tipo: O operador '{operador}' espera 'inteiro', mas recebeu '{tipo1}'")
                        pilha_tipos.append('inteiro')       # Resultado de '+u' é inteiro

                # --- Lógica para Operadores Binários ---
                elif operador in OPERADORES_BINARIOS:
                    tipo2 = pilha_tipos.pop()
                    tipo1 = pilha_tipos.pop()
                    
                    if operador in ['+', '-', '*', 'div']:
                        if not (tipo1 == 'inteiro' and tipo2 == 'inteiro'):
                            raise TypeError(f"Erro de tipo: Operador '{operador}' inválido entre '{tipo1}' e '{tipo2}'")
                        pilha_tipos.append('inteiro')       # Resultado de aritmética é inteiro
                    
                    elif operador in ['<', '<=', '>', '>=', '=', '!=']:
                        if not (tipo1 == 'inteiro' and tipo2 == 'inteiro'):
                            raise TypeError(f"Erro de tipo: Operador relacional '{operador}' inválido entre '{tipo1}' e '{tipo2}'")
                        pilha_tipos.append('booleano')      # Resultado de comparação é booleano
                    
                    elif operador in ['e', 'ou']:
                        if not (tipo1 == 'booleano' and tipo2 == 'booleano'):
                            raise TypeError(f"Erro de tipo: Operador lógico '{operador}' inválido entre '{tipo1}' e '{tipo2}'")
                        pilha_tipos.append('booleano')      # Resultado de lógica é booleano
            
            except IndexError:
                                                            # Se der .pop() numa pilha vazia, a expressão está mal formada
                raise ValueError(f"Expressão pós-fixa mal formada. Faltam operandos para o operador '{operador}'.")

    # 4. Verificação Final
    if len(pilha_tipos) != 1:
        raise ValueError(f"Expressão final mal formada. Sobraram tipos na pilha: {pilha_tipos}")
    
    # O único item que sobrou na pilha é o tipo final!
    return pilha_tipos[0]

def posfix(expressao):  # converte infixa → pós-fixa (shunting-yard adaptado)
    order = {'*': 1, 'div': 1,                                  # Multiplicação e Divisão têm precedência 1
             '+': 2, '-': 2,                                    # Adição e Subtração têm precedência 2
             '<': 3, '<=': 3, '>': 3, '>=': 3, '=': 3, '!=': 3, # Relações têm precedência 3
             'nao': 4,                                          # Negação tem precedência 4
             'e': 5,                                            # Conjunção tem precedência 5
             'ou': 6}                                           # Disjunção tem precedência 6
    
    stack = []      # pilha de operadores
    posfixa = []    # saída pós-fixa

    for i in range(len(expressao)):                                         # varre expressão token por token
        if expressao[i] not in order and expressao[i] not in ['(', ')']:
            posfixa.append(expressao[i])                                    # token simples vai direto para saída
            if stack and stack[-1] in ['+u', '-u']:                         # resolve unários imediatamente
                posfixa.append(stack.pop())
        
        if expressao[i] == '(':
            stack.append(expressao[i])                      # empilha parênteses

        if expressao[i] == ')':                             # desempilha até achar '('
            while stack and stack[-1] != '(':
                posfixa.append(stack.pop())
            stack.pop()
            if stack and stack[-1] == 'nao':                # resolve NOT
                posfixa.append(stack.pop())
            if stack and stack[-1] in ['+u', '-u']:         # resolve unário
                posfixa.append(stack.pop())

        if expressao[i] in ['+', '-']:
            if expressao[i-1] in ['+', '-', '*', 'div', '<', '<=', '>', '>=', '=', '!=', 'e', 'ou', '(', None]:
                stack.append(f'{expressao[i]}u')            # Operador unário
            else:
                while stack and stack[-1] != '(' and order[expressao[i]] >= order[stack[-1]]:
                    posfixa.append(stack.pop())
                stack.append(expressao[i])  
        
        elif expressao[i] in ['*', 'div', '<', '<=', '>', '>=', '=', '!=', 'e', 'ou', 'nao']:
            while stack and stack[-1] != '(' and order[expressao[i]] >= order[stack[-1]]:
                posfixa.append(stack.pop())
            stack.append(expressao[i])

    while stack:                                            # esvazia pilha
        posfixa.append(stack.pop())

    if None in posfixa:                                     # remove marcadores auxiliares
        posfixa.remove(None)
    return posfixa

