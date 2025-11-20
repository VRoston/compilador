import sys
import os
from analisador_lexical import AnalisadorLexical
from analisador_semantico import TabelaSimbolos, posfix, tipo_expressao
from code_generator import Gera

class Rotulo:
    contador = 1

    def __new__(cls):
        rotulo = f"L{cls.contador}"
        cls.contador += 1
        return rotulo

    @classmethod
    def go_back_i_want_to_be_monke(cls):
        cls.contador = cls.contador - 1

class AnalisadorSintatico:
    def __init__(self, arquivo_entrada, arquivo_saida):
        self.token_atual = None
        self.erro = False
        self.expressao = []
        self.qtd_var = 0
        self.nome_programa = ""

        self.escopos_dalloc = [[]]
        self.escopo_atual = 0

        self.allocs_pendentes = [[]]

        self.lexador = AnalisadorLexical(arquivo_entrada)
        self.tabela = TabelaSimbolos()
        self.gera = Gera(filename = arquivo_saida)

        self.keywords = {
            "sprograma": "programa",
            "sinicio": "inicio",
            "sfim": "fim",
            "sprocedimento": "procedimento",
            "sfuncao": "funcao",
            "sse": "se",
            "sentao": "entao",
            "ssenao": "senao",
            "senquanto": "enquanto",
            "sfaca": "faca",
            "satribuicao": ":=",
            "sescreva": "escreva",
            "sleia": "leia",
            "svar": "var",
            "sinteiro": "inteiro",
            "sbooleano": "booleano",
            "sidentificador": "identificador",
            "snumero": "numero",
            "sponto": ".",
            "sponto_virgula": ";",
            "svirgula": ",",
            "sabre_parenteses": "(",
            "sfecha_parenteses": ")",
            "smaior": ">",
            "smaiorigual": ">=",
            "sigual": "=",
            "smenor": "<",
            "smenorigual": "<=",
            "sdif": "!=",
            "smais": "+",
            "smenos": "-",
            "smult": "*",
            "sdiv": "div",
            "se": "e",
            "sou": "ou",
            "snao": "nao",
            "sdoispontos": ":",
            "sverdadeiro": "verdadeiro",
            "sfalso": "falso",
            "serro": "erro",
        }

    def _consumir(self, simbolo_esperado):
        """Verifica o token atual e avança para o próximo."""
        if self.token_atual:
            simbolo_anterior = self.token_atual.simbolo

            if self.token_atual.simbolo == simbolo_esperado:
                self.token_atual = self.lexador.proximo_token()
            else:
                simbolo_encontrado = self.token_atual.lexema
                if self.token_atual.simbolo != "serro":
                    print(f"Erro sintático na linha {self.token_atual.linha}: Esperado '{self.keywords[simbolo_esperado]}', mas encontrado '{simbolo_encontrado}'")
                self.erro = True
                return

            if self.token_atual:
                if simbolo_anterior == self.token_atual.simbolo and simbolo_anterior not in ["sinicio", "sfim", "sabre_parenteses", "sfecha_parenteses"]:
                    print(f"Erro Sintático na linha {self.token_atual.linha}: Símbolo '{self.token_atual.lexema}' duplicado.")
                    self.erro = True
                    return

        else:
            print(f"Erro sintático: Esperado '{self.keywords[simbolo_esperado]}', mas encontrado 'EOF'")
    
    def analisar(self):
        self.token_atual = self.lexador.proximo_token()
        self._analisar_programa()
        self.gera.escreve()
        self.lexador.fechar()

    # AQUI DEVE TER CÓDIGO DE GERAÇÃO DE RÓTULO
    def _analisar_programa(self): 
        """Analisa a estrutura principal do programa."""     
        self._consumir("sprograma")
        self.gera("", "START", "", "")
        if not self.erro:

            self.tabela.adicionar_simbolo(self.token_atual.lexema, tipo='programa', rotulo=Rotulo())
            self.nome_programa = self.token_atual.lexema
            self._consumir("sidentificador")
            if not self.erro:
                self._consumir("sponto_virgula")
                if not self.erro:
                    rotulo_skip = self.tabela.buscar_simbolo(self.nome_programa)['rotulo']
                    self.analisar_bloco(rotulo_skip, final=True)
                    self.gera("", "HLT", "", "")
        
    def analisar_bloco(self, rotulo_skip, final=False):
        self.allocs_pendentes.append([])
        vars_dalloc = None
        self._analisa_et_variaveis()
        if not self.erro:
            func_proc = self._analisa_subrotinas(rotulo_skip)
            if not self.erro:
                self._analisa_comandos(rotulo_skip, func_proc=func_proc, final=final)
                self.tabela.sair_escopo()

                self._gera_dalloc()
        self.allocs_pendentes.pop()

    def _gera_dalloc(self):
        """Gera as instruções de DALLOC para o escopo atual."""
        if self.escopos_dalloc and len(self.escopos_dalloc) > self.escopo_atual:
            for var_range in reversed(self.escopos_dalloc[self.escopo_atual]):
                inicio, tamanho = var_range
                self.gera("", "DALLOC", inicio, tamanho)
            self.escopos_dalloc.pop()
            self.escopo_atual -= 1

    def _analisa_et_variaveis(self):
        """Analisa todas as seções de declaração de variáveis."""
        if self.token_atual and self.token_atual.simbolo == "svar":
            self._consumir("svar")
            if not self.erro:
                while self.token_atual and self.token_atual.simbolo == "sidentificador":
                    self._analisa_variaveis()

    def _analisa_variaveis(self):
        """Analisa uma linha de declaração como 'a, b, c : inteiro;'"""
        variaveis_para_declarar = []
        end_inicial_var = self.qtd_var 

        if self.token_atual and self.token_atual.simbolo == "sidentificador" and not self.erro:
            variaveis_para_declarar.append(self.token_atual.lexema)
            self._consumir("sidentificador")

        while self.token_atual and self.token_atual.simbolo == "svirgula" and not self.erro:
            self._consumir("svirgula")
            variavel = self.token_atual.lexema
            self._consumir("sidentificador")
            if not self.erro:
                variaveis_para_declarar.append(variavel)
        
        # 2. Consumir os dois-pontos e o tipo
        self._consumir("sdoispontos")
        if self.erro:
            return
        
        tipo_das_variaveis = None
        if self.token_atual and self.token_atual.simbolo in ["sinteiro", "sbooleano"]:
            tipo_das_variaveis = self.token_atual.lexema # Guarda o tipo (ex: 'inteiro')
            self._consumir(self.token_atual.simbolo)
        else:
            print(f"Erro sintático na linha {self.token_atual.linha}: Tipo esperado (inteiro ou booleano)")
            self.erro = True
            return

        # 3. INSERÇÃO NA TABELA: Inserir cada variável coletada com o tipo encontrado
        if tipo_das_variaveis:
            for nome_var in variaveis_para_declarar:
                try:
                    self.tabela.adicionar_simbolo(nome_var, tipo=tipo_das_variaveis)
                except ValueError as e:
                    print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
                    self.erro = True
                self.qtd_var += 1

        self._consumir("sponto_virgula")
        self.gera("", "ALLOC", end_inicial_var, self.qtd_var - end_inicial_var)
        self.escopos_dalloc[-1].append((end_inicial_var, self.qtd_var - end_inicial_var))

    def _analisa_comandos(self, rotulo_skip, func_proc, final=False):
        if self.token_atual and self.token_atual.simbolo == "sinicio":
            if rotulo_skip != None:
                # Se houve sub-rotinas (func_proc >= 1), o JMP lá em cima pulou pra cá.
                # Se não houve, o fluxo seguiu normal e esse rótulo é apenas um marcador.
                if func_proc >= 1:
                    self.gera(rotulo_skip, "NULL", "", "")
                
                # NOVO: Agora que estamos no fluxo de execução do bloco (após pular definições),
                # geramos os ALLOCs das variáveis de retorno das funções declaradas acima.
                for alloc in self.allocs_pendentes[-1]:
                    self.gera("", "ALLOC", alloc[0], alloc[1])
                
                # Limpa para não gerar novamente
                self.allocs_pendentes[-1] = []

            self._consumir("sinicio")
            while self.token_atual and self.token_atual.simbolo != "sfim" and not self.erro:
                self._analisa_comando_simples()
            
            if not self.erro:
                self._consumir("sfim")
                if not self.erro and final:
                    self._consumir("sponto")

                if not self.erro and not final:
                    self._consumir("sponto_virgula")
        else:
            print(f"Erro sintático na linha {self.token_atual.linha}: Esperado 'inicio' para iniciar o bloco de comandos.")
            self.erro = True
                    

    def _analisa_comando_simples(self, sentao_ssenao = False):
        """Analisa um comando simples dentro do bloco de comandos."""
        if self.token_atual.simbolo == "sidentificador":
            self._analisa_atrib_chprocedimento()
            if self.token_atual.simbolo == "sfim":
                return
            elif not self.erro and sentao_ssenao:
                if self.token_atual.simbolo == "sponto_virgula":
                    self._consumir("sponto_virgula")
                return
            elif not self.erro:
                self._consumir("sponto_virgula")

        elif self.token_atual.simbolo == "sse":
            self._analisa_se()

        elif self.token_atual.simbolo == "senquanto":
            self._analisa_enquanto()

        elif self.token_atual.simbolo == "sescreva":
            self._analisa_escreva()
            if self.token_atual.simbolo == "sfim":
                return
            elif not self.erro and sentao_ssenao:
                if self.token_atual.simbolo == "sponto_virgula":
                    self._consumir("sponto_virgula")
                return
            elif not self.erro:
                self._consumir("sponto_virgula")

        elif self.token_atual.simbolo == "sleia":
            self._analisa_leia()
            if self.token_atual.simbolo == "sfim":
                return
            elif not self.erro and sentao_ssenao:
                if self.token_atual.simbolo == "sponto_virgula":
                    self._consumir("sponto_virgula")
                return
            elif not self.erro:
                self._consumir("sponto_virgula")

        elif self.token_atual.simbolo == "sinicio":
            self._analisa_comandos(None, func_proc=True)
        else:
            print(f"Erro Sintático na linha {self.token_atual.linha}: Comando inválido ou inesperado '{self.token_atual.lexema}'.")
            self.erro = True

    def _analisa_atrib_chprocedimento(self):
        simbolo = self.token_atual.lexema
        self._consumir("sidentificador")
        if not self.erro:
            if self.token_atual.simbolo == "satribuicao":
                self._consumir("satribuicao")
                self._analisa_atribuicao(simbolo)
            else:
                self.gera("", "CALL", self.tabela.buscar_simbolo(simbolo)['rotulo'], "")
                self._analisa_chamada_procedimento(simbolo)

    def _analisa_leia(self):
        simbolo = None
        self._consumir("sleia")
        self._consumir("sabre_parenteses")
        if not self.erro:
            if not self.erro and self.token_atual.simbolo == "sidentificador":
                try:
                    simbolo = self.tabela.buscar_simbolo(self.token_atual.lexema)
                except ValueError as e:
                    print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
                    self.erro = True
                self.gera("", "RD", "", "")
                self.gera("", "STR", simbolo['memoria'], "")
                if not self.erro:
                    self._consumir("sidentificador")
                    if not self.erro:
                        self._consumir("sfecha_parenteses")

    def _analisa_escreva(self):
        simbolo = None
        self._consumir("sescreva")
        self._consumir("sabre_parenteses")
        if not self.erro:
            if not self.erro:
                try:
                    simbolo = self.tabela.buscar_simbolo(self.token_atual.lexema)
                except ValueError as e:
                    print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
                    self.erro = True
                self.gera("", "LDV", simbolo['memoria'], "")
                self.gera("", "PRN", "", "")
                self._consumir("sidentificador")
                if not self.erro:
                    self._consumir("sfecha_parenteses")
    
    def _analisa_enquanto(self): 
        rotulo_inicio = Rotulo()
        rotulo_sair = Rotulo()
        self._consumir("senquanto")
        self.gera(rotulo_inicio, "NULL", "", "")
        if not self.erro and self._expressao() == 'booleano':
            self.gera("", "JMPF", rotulo_sair, "")
            self._consumir("sfaca")
            if not self.erro:
                self._analisa_comando_simples() 
                self.gera("", "JMP", rotulo_inicio, "")
                self.gera(rotulo_sair, "NULL", "", "")
        elif not self.erro:
            print(f"Erro Semântico na linha {self.token_atual.linha}: Expressão do 'enquanto' deve ser do tipo booleano.")
            self.erro = True     

    def _analisa_se(self):
        rotulo_se = Rotulo()
        rotulo_pula_senao = Rotulo()
        self._consumir("sse")
        if not self.erro and self._expressao() == 'booleano':
            self.gera("", "JMPF", rotulo_se, "")
            self._consumir("sentao")
            if not self.erro:
                self._analisa_comando_simples(sentao_ssenao=True)
                if not self.erro and self.token_atual and self.token_atual.simbolo == "ssenao":
                    self.gera("", "JMP", rotulo_pula_senao, "")
                self.gera(rotulo_se, "NULL","", "")
                if not self.erro and self.token_atual and self.token_atual.simbolo == "ssenao":
                    self._consumir("ssenao")
                    if not self.erro:
                        self._analisa_comando_simples(sentao_ssenao=True)
                        self.gera(rotulo_pula_senao, "NULL","", "")
        elif not self.erro:
            print(f"Erro Semântico na linha {self.token_atual.linha}: Expressão do 'se' deve ser do tipo booleano.")
            self.erro = True

    def _analisa_subrotinas(self, rotulo_skip):
        subrotinas = 0
        flag_jump_gerado = False # Controle para gerar o JMP apenas uma vez

        # Verifica se o próximo token inicia uma sub-rotina para gerar o pulo
        if self.token_atual and self.token_atual.simbolo in ["sprocedimento", "sfuncao"]:
            self.gera("", "JMP", rotulo_skip, "")
            flag_jump_gerado = True

        while self.token_atual and self.token_atual.simbolo in ["sprocedimento", "sfuncao"]:
            if self.token_atual.simbolo == "sprocedimento":
                subrotinas += 1
                self._consumir("sprocedimento")
                # Não passamos mais rotulo_skip para dentro, pois o pulo já foi feito
                self._analisa_declaracao_procedimento() 
            elif self.token_atual.simbolo == "sfuncao":
                subrotinas += 1
                self._consumir("sfuncao")
                self._analisa_declaracao_funcao()
        
        # Se não houve sub-rotinas, o contador de rótulos pode ser ajustado (seu código original)
        if subrotinas == 0:
            Rotulo.go_back_i_want_to_be_monke()
        
        return subrotinas

    def _analisa_declaracao_procedimento(self):
        rotulo_procedimento = Rotulo()
        rotulo_skip = Rotulo() # Rótulo para o bloco interno deste procedimento
        
        # REMOVIDO: self.gera("", "JMP", skippar, "") <--- O pai já pulou tudo

        if self.token_atual.simbolo == "sidentificador":
            try:
                self.tabela.adicionar_simbolo(self.token_atual.lexema, tipo='procedimento', rotulo=rotulo_procedimento)
            except ValueError as e:
                print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
                self.erro = True
            
            # Gera o rótulo de entrada do procedimento
            self.gera(self.tabela.buscar_simbolo(self.token_atual.lexema)['rotulo'], "NULL", "", "")
            
            if not self.erro:
                self._consumir("sidentificador")
                if not self.erro:
                    self._consumir("sponto_virgula")
                    if not self.erro:
                        self.escopo_atual += 1
                        self.escopos_dalloc.append([])
                        self.tabela.entrar_escopo()
                        self.analisar_bloco(rotulo_skip) # Recursão normal
                        self.gera("", "RETURN", "", "")

    def _analisa_declaracao_funcao(self):
        rotulo_funcao = Rotulo()
        rotulo_skip = Rotulo()
        nome_funcao = self.token_atual.lexema
        tipo_retorno = None

        # ALTERAÇÃO: Não geramos ALLOC agora. Apenas registramos que ele é necessário.
        # O ALLOC será gerado quando o 'inicio' do pai for processado.
        self.allocs_pendentes[-1].append((self.qtd_var, 1))
        
        # Mantemos o registro no DALLOC para desalocar no final do pai
        self.escopos_dalloc[-1].append((self.qtd_var, 1))
        self.qtd_var += 1
        
        # REMOVIDO: self.gera("", "JMP", skippar, "")

        self._consumir("sidentificador")
        if not self.erro:
            self._consumir("sdoispontos")
            if not self.erro:
                if self.token_atual.simbolo in ["sinteiro", "sbooleano"]:
                    tipo_retorno = self.token_atual.lexema
                    self._consumir(self.token_atual.simbolo)
                    if not self.erro:
                        try:
                            self.tabela.adicionar_simbolo(nome_funcao, tipo=f'funcao {tipo_retorno}', rotulo=rotulo_funcao)
                        except ValueError as e:
                            print(f"Erro Semântico: {e}")
                            self.erro = True
                        
                        self.gera(self.tabela.buscar_simbolo(nome_funcao)['rotulo'], "NULL", "", "")
                        
                        if not self.erro:
                            self._consumir("sponto_virgula")
                            if not self.erro:
                                self.escopo_atual += 1
                                self.escopos_dalloc.append([])
                                self.tabela.entrar_escopo()
                                self.analisar_bloco(rotulo_skip)
                                self.gera("", "RETURN", "", "")
                else:
                    print(f"Erro sintático na linha {self.token_atual.linha}: Tipo de retorno esperado (inteiro ou booleano)")
                    self.erro = True
                    
    def _expressao(self):
        posfixa = None
        tipo = None
        self._analisa_expressao()
        self.expressao.append(None)
        if not self.erro:
            posfixa = posfix(self.expressao)
            try:
                tipo = tipo_expressao(posfixa, self.tabela)
            except TypeError as e:
                print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
                self.erro = True
        
        for token in posfixa:
            if token.isnumeric():
                self.gera("", "LDC", token, "")
            elif token in ["verdadeiro", "falso"]:
                valor = 1 if token == "verdadeiro" else 0
                self.gera("", "LDC", valor, "")
            elif token.isalpha() and token not in ['e', 'ou', 'nao', 'div']:
                if self.tabela.buscar_simbolo(token)['tipo'] in ['funcao inteiro', 'funcao booleano']:
                    self.gera("", "CALL", self.tabela.buscar_simbolo(token)['rotulo'], "")
                self.gera("", "LDV", self.tabela.buscar_simbolo(token)['memoria'], "")
            elif token == '+':
                self.gera("", "ADD", "", "")
            elif token == '-':
                self.gera("", "SUB", "", "")
            elif token == '*':
                self.gera("", "MULT", "", "")
            elif token == 'div':
                self.gera("", "DIVI", "", "")
            elif token == '<':
                self.gera("", "CME", "", "")
            elif token == '<=':
                self.gera("", "CMEQ", "", "")
            elif token == '>':
                self.gera("", "CMA", "", "")
            elif token == '>=':
                self.gera("", "CMAQ", "", "")
            elif token == '=':
                self.gera("", "CEQ", "", "")
            elif token == '!=':
                self.gera("", "CDIF", "", "")
            elif token == 'e':
                self.gera("", "AND", "", "")
            elif token == 'ou':
                self.gera("", "OR", "", "")
            elif token == 'nao':
                self.gera("", "NEG", "", "")
            elif token == '-u':
                self.gera("", "INV", "", "")
            elif token == '+u':
                pass

        self.expressao = []
        return tipo

    def _analisa_expressao(self):
        self._analisa_expressao_simples()
        while self.token_atual and self.token_atual.simbolo in ["smaior", "smaiorigual", "smenor", "smenorigual", "sigual", "sdif"]:
            if not self.erro:
                self.expressao.append(self.token_atual.lexema)
                self._consumir(self.token_atual.simbolo)
                if not self.erro:
                    self._analisa_expressao_simples()
            else:
                break

    def _analisa_expressao_simples(self):
        if self.token_atual and self.token_atual.simbolo in ["smais", "smenos"]:
            self.expressao.append(self.token_atual.lexema)
            self._consumir(self.token_atual.simbolo)
        
        self._analisa_termo()
        
        while self.token_atual and self.token_atual.simbolo in ["smais", "smenos", "sou", "se"]:
            self.expressao.append(self.token_atual.lexema)
            self._consumir(self.token_atual.simbolo)
            if not self.erro:
                self._analisa_termo()

    def _analisa_termo(self):
        self._analisa_fator()
        while self.token_atual and self.token_atual.simbolo in ["smult", "sdiv", "se", "sou"]:
            self.expressao.append(self.token_atual.lexema)
            self._consumir(self.token_atual.simbolo)
            if not self.erro:
                self._analisa_fator()

    def _analisa_fator(self):
        if self.token_atual.simbolo == "sidentificador":
            try:
                simbolo = self.tabela.buscar_simbolo(self.token_atual.lexema)
            except ValueError as e:
                print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
                self.erro = True
            if not self.erro:
                self.expressao.append(self.token_atual.lexema)    
                self._consumir("sidentificador")
                if not self.erro and simbolo['tipo'] in ['funcao inteiro', 'funcao booleano']:
                    self._analisa_chamada_funcao(simbolo['nome'])

        elif self.token_atual.simbolo == "snumero":
            self.expressao.append(self.token_atual.lexema)
            self._consumir("snumero")
        elif self.token_atual.simbolo in ["sverdadeiro", "sfalso"]:
            self.expressao.append(self.token_atual.lexema)
            self._consumir(self.token_atual.simbolo)
        elif self.token_atual.simbolo == "sabre_parenteses":
            self.expressao.append(self.token_atual.lexema)
            self._consumir("sabre_parenteses")
            if not self.erro:
                self._analisa_expressao()
                if not self.erro:
                    self.expressao.append(self.token_atual.lexema)
                    self._consumir("sfecha_parenteses")
        elif self.token_atual.simbolo == "snao":
            self.expressao.append(self.token_atual.lexema)
            self._consumir("snao")
            if not self.erro:
                self._analisa_fator()
        else:
            print(f"Erro Sintático na linha {self.token_atual.linha}: Fator inválido ou inesperado '{self.token_atual.lexema}'.")
            self.erro = True

    def _analisa_atribuicao(self, simbolo):
        tipo = None
        try:
            tipo = self.tabela.buscar_simbolo(simbolo)['tipo']
        except ValueError as e:
            print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
            self.erro = True

        if tipo in ['funcao inteiro', 'funcao booleano']:
            tipo = tipo.replace('funcao ', '')

        if not self.erro:
            if self._expressao() != tipo:
                print(f"Erro Semântico na linha {self.token_atual.linha}: Tipo incompatível na atribuição para '{simbolo}'. Esperado '{tipo}'.")
                self.erro = True
            else:
                self.gera("", "STR", self.tabela.buscar_simbolo(simbolo)['memoria'], "")
            
    def _analisa_chamada_procedimento(self, simbolo):
        try:
            self.tabela.buscar_simbolo(simbolo)
        except ValueError as e:
            print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
            self.erro = True

    def _analisa_chamada_funcao(self, simbolo):
        try:
            self.tabela.buscar_simbolo(simbolo)
        except ValueError as e:
            print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
            self.erro = True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Erro: Modo de uso incorreto.")
        print("Uso: python analisador_sintatico.py <caminho_para_o_arquivo.txt>")
        sys.exit(1) 

    caminho_arquivo = sys.argv[1]
    
    nome_base, extensao = os.path.splitext(caminho_arquivo)
    _, _, nome_arquivo = nome_base.rpartition(os.sep)

    if extensao != '.txt':
        print(f"Erro: O arquivo '{caminho_arquivo}' não é válido.")
        print("Por favor, forneça um arquivo .txt")
        sys.exit(1)
    
    analisador = AnalisadorSintatico(caminho_arquivo, nome_arquivo)
    analisador.analisar()