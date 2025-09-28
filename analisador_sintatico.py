from analisador_lexical import AnalisadorLexical, Token
from tabela_simbolos import TabelaSimbolos

class AnalisadorSintatico:
    def __init__(self, arquivo_entrada):
        self.lexador = AnalisadorLexical(arquivo_entrada)
        self.token_atual = None
        self.erro = False
        self.tabela = TabelaSimbolos()

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
        if self.token_atual and self.token_atual.simbolo == simbolo_esperado:
            self.token_atual = self.lexador.proximo_token()
        else:
            simbolo_encontrado = self.token_atual.lexema if self.token_atual else 'Fim de arquivo'
            if self.token_atual.simbolo != "serro":
                print(f"Erro sintático: Esperado '{self.keywords[simbolo_esperado]}', mas encontrado '{simbolo_encontrado}'")
            self.erro = True
    
    def analisar(self):
        self.token_atual = self.lexador.proximo_token()
        self._analisar_programa()
        self.lexador.fechar()
        print("DEBUG: Fim da analise")

    # AQUI DEVE TER CÓDIGO DE GERAÇÃO DE RÓTULO
    def _analisar_programa(self): 
        """Analisa a estrutura principal do programa."""     
        self._consumir("sprograma")
        if not self.erro and self.token_atual.simbolo == "sidentificador":
            self.tabela.adicionar_simbolo(self.token_atual.lexema, tipo='programa')
            self._consumir("sidentificador")
            if not self.erro:
                self._consumir("sponto_virgula")
                if not self.erro:
                    self.analisar_bloco()
                    if not self.erro:
                        self._consumir("sfim")
                        if not self.erro:
                            self._consumir("sponto")
        
    def analisar_bloco(self):
        """Analisa o bloco de declarações e comandos."""
        self._analisa_et_variaveis()
        self._analisa_subrotinas()
        self._analisa_comandos()

    def _analisa_et_variaveis(self):
        """Analisa todas as seções de declaração de variáveis."""
        if self.token_atual and self.token_atual.simbolo == "svar":
            self._consumir("svar")

            while self.token_atual and self.token_atual.simbolo == "sidentificador":
                self._analisa_variaveis()

    def _analisa_variaveis(self):
        """Analisa uma linha de declaração como 'a, b, c : inteiro;'"""
        variaveis_para_declarar = []
        
        # 1. Coletar todos os identificadores (ex: 'a', 'b', 'c')
        while self.token_atual and self.token_atual.simbolo == "sidentificador":
            variaveis_para_declarar.append(self.token_atual.lexema)
            self._consumir("sidentificador")
            if self.token_atual.simbolo == "svirgula":
                self._consumir("svirgula")
            else:
                break
        
        # 2. Consumir os dois-pontos e o tipo
        self._consumir("sdoispontos")
        if self.erro:
            return
        
        tipo_das_variaveis = None
        if self.token_atual and self.token_atual.simbolo in ["sinteiro", "sbooleano"]:
            tipo_das_variaveis = self.token_atual.lexema # Guarda o tipo (ex: 'inteiro')
            self._consumir(self.token_atual.simbolo)
        else:
            print("Erro sintático: Tipo esperado (inteiro ou booleano)")
            self.erro = True
            return

        # 3. INSERÇÃO NA TABELA: Inserir cada variável coletada com o tipo encontrado
        if tipo_das_variaveis:
            for nome_var in variaveis_para_declarar:
                try:
                    self.tabela.adicionar_simbolo(nome_var, tipo=tipo_das_variaveis)
                except ValueError as e:
                    print(f"Erro Semântico: {e}")
                    self.erro = True

        self._consumir("sponto_virgula")
    
    def _analisa_comandos(self):
        if self.token_atual and self.token_atual.simbolo == "sinicio":
            self._consumir("sinicio")
            while self.token_atual and self.token_atual.simbolo != "sfim":
                self._analisa_comando_simples()

    def _analisa_comando_simples(self):
        """Analisa um comando simples dentro do bloco de comandos."""
        if self.token_atual.simbolo == "sidentificador":
            self._analisa_atrib_chprocedimento()
        elif self.token_atual.simbolo == "sse":
            self._analisa_se()
        elif self.token_atual.simbolo == "senquanto":
            self._analisa_enquanto()
        elif self.token_atual.simbolo == "sescreva":
            self._analisa_escreva()
        elif self.token_atual.simbolo == "sleia":
            self._analisa_leia()
        elif self.token_atual.simbolo == "sinicio":
            self.analisar_bloco()
        else:
            print(f"Erro Sintático: Comando inválido ou inesperado '{self.token_atual.lexema}'.")
            self.erro = True

    def _analisa_atrib_chprocedimento(self):
        self._consumir("sidentificador")
        if self.token_atual.simbolo == "satribuicao":
            self._consumir("satribuicao")
            self._analisa_atribuicao()
        else:
            self._chamada_procedimento()

    def _analisa_leia(self):
        self._consumir("sleia")
        self._consumir("sabre_parenteses")
        if not self.erro:
            self._consumir("sidentificador")
            if not self.erro:
                try:
                    self.tabela.buscar_simbolo(self.token_atual.lexema)
                except ValueError as e:
                    print(f"Erro Semântico: {e}")
                    self.erro = True
                self._consumir("sfecha_parenteses")
                if not self.erro:
                    self._consumir("sponto_virgula")

    def _analisa_escreva(self):
        self._consumir("sescreva")
        self._consumir("sabre_parenteses")
        if not self.erro:
            self._consumir("sidentificador")
            if not self.erro:
                try:
                    self.tabela.buscar_simbolo(self.token_atual.lexema)
                except ValueError as e:
                    print(f"Erro Semântico: {e}")
                    self.erro = True
                self._consumir("sfecha_parenteses")
                if not self.erro:
                    self._consumir("sponto_virgula")
    
    # AQUI DEVE TER CÓDIGO DE GERAÇÃO DE RÓTULO
    def _analisa_enquanto(self): 
        self._consumir("senquanto")
        self._consumir("sabre_parenteses")
        if not self.erro:
            self._analisa_expressao()
            if not self.erro:
                self._consumir("sfecha_parenteses")
                if not self.erro:
                    self._consumir("sfaca")
                    if not self.erro:
                        self._analisa_comando_simples()      

    def _analisa_se(self):
        self._consumir("sse")
        self._consumir("sabre_parenteses")
        if not self.erro:
            self._analisa_expressao()
            if not self.erro:
                self._consumir("sfecha_parenteses")
                if not self.erro:
                    self._consumir("sentao")
                    if not self.erro:
                        self._analisa_comando_simples()
                        if not self.erro and self.token_atual and self.token_atual.simbolo == "ssenao":
                            self._consumir("ssenao")
                            if not self.erro:
                                self._analisa_comando_simples()

    def _analisa_subrotinas(self):
        while self.token_atual and self.token_atual.simbolo in ["sprocedimento", "sfuncao"]:
            if self.token_atual.simbolo == "sprocedimento":
                self._consumir("sprocedimento")
                self._analisa_declaracao_procedimento()
            elif self.token_atual.simbolo == "sfuncao":
                self._consumir("sfuncao")
                self._analisa_declaracao_funcao()
            self._consumir("sponto_virgula")

    def _analisa_declaracao_procedimento(self):
        pass

    def _analisa_declaracao_funcao(self):
        pass

    def _analisa_atribuicao(self):
        pass

    def _chamada_procedimento(self):
        pass
    
    def _analisa_expressao(self):
        pass

    def _analisa_expressao_simples(self):
        pass

    def _analisa_termo(self):
        pass

if __name__ == "__main__":
    # Exemplo: analisar sint2.txt
    print("DEBUG: Executando bloco principal")
    analisador = AnalisadorSintatico('./Testes Sintático/teste.jovane')
    analisador.analisar()
    