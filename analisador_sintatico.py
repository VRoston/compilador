import sys
import os
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
        print(self.token_atual.lexema)
    
    def analisar(self):
        self.token_atual = self.lexador.proximo_token()
        self._analisar_programa()
        self.lexador.fechar()

    # AQUI DEVE TER CÓDIGO DE GERAÇÃO DE RÓTULO
    def _analisar_programa(self): 
        """Analisa a estrutura principal do programa."""     
        self._consumir("sprograma")
        if not self.erro:
            self.tabela.adicionar_simbolo(self.token_atual.lexema, tipo='programa')
            self._consumir("sidentificador")
            if not self.erro:
                self._consumir("sponto_virgula")
                if not self.erro:
                    self.analisar_bloco(final=True)
        
    def analisar_bloco(self, final=False):
        """Analisa o bloco de declarações e comandos."""
        self._analisa_et_variaveis()
        if not self.erro:
            self._analisa_subrotinas()
            if not self.erro and final:
                self._analisa_comando_final()
            elif not self.erro:
                self._analisa_comandos()

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
        
        while self.token_atual and self.token_atual.simbolo == "sidentificador":
            variaveis_para_declarar.append(self.token_atual.lexema)
            self._consumir("sidentificador")
            if self.token_atual.simbolo == "svirgula" and not self.erro:
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

    def _analisa_comando_final(self):
        if self.token_atual and self.token_atual.simbolo == "sinicio":
            self._consumir("sinicio")
            while self.token_atual and self.token_atual.simbolo != "sfim" and not self.erro:
                self._analisa_comando_simples()
            if not self.erro:
                self._consumir("sfim")
                if not self.erro:
                    self._consumir("sponto")

    def _analisa_comandos(self):
        if self.token_atual and self.token_atual.simbolo == "sinicio":
            self._consumir("sinicio")
            while self.token_atual and self.token_atual.simbolo != "sfim" and not self.erro:
                self._analisa_comando_simples()
            if not self.erro:
                self._consumir("sfim")
                if not self.erro:
                    self._consumir("sponto_virgula")

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
            self._analisa_comandos()
        else:
            print(f"Erro Sintático: Comando inválido ou inesperado '{self.token_atual.lexema}'.")
            self.erro = True

    def _analisa_atrib_chprocedimento(self):
        simbolo = self.token_atual.lexema
        self._consumir("sidentificador")
        if not self.erro:
            if self.token_atual.simbolo == "satribuicao":
                self._consumir("satribuicao")
                self._analisa_atribuicao(simbolo)
            else:
                self._analisa_chamada_procedimento(simbolo)

    def _analisa_leia(self):
        self._consumir("sleia")
        self._consumir("sabre_parenteses")
        if not self.erro:
            if not self.erro and self.token_atual.simbolo == "sidentificador":
                try:
                    self.tabela.buscar_simbolo(self.token_atual.lexema)
                except ValueError as e:
                    print(f"Erro Semântico: {e}")
                    self.erro = True
                self._consumir("sidentificador")
                if not self.erro:
                    self._consumir("sfecha_parenteses")
                    if not self.erro:
                        self._consumir("sponto_virgula")

    def _analisa_escreva(self):
        self._consumir("sescreva")
        self._consumir("sabre_parenteses")
        if not self.erro:
            if not self.erro:
                try:
                    self.tabela.buscar_simbolo(self.token_atual.lexema)
                except ValueError as e:
                    print(f"Erro Semântico: {e}")
                    self.erro = True
                self._consumir("sidentificador")
                if not self.erro:
                    self._consumir("sfecha_parenteses")
                    if not self.erro:
                        self._consumir("sponto_virgula")
    
    # AQUI DEVE TER CÓDIGO DE GERAÇÃO DE RÓTULO
    def _analisa_enquanto(self): 
        self._consumir("senquanto")
        self._analisa_expressao()
        if not self.erro:
            self._consumir("sfaca")
            if not self.erro:
                self._analisa_comando_simples()      

    def _analisa_se(self):
        self._consumir("sse")
        self._analisa_expressao()
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

    def _analisa_declaracao_procedimento(self):
        if self.token_atual.simbolo == "sidentificador":
            try:
                self.tabela.adicionar_simbolo(self.token_atual.lexema, tipo='procedimento')
            except ValueError as e:
                print(f"Erro Semântico: {e}")
                self.erro = True
            if not self.erro:
                self._consumir("sidentificador")
                if not self.erro:
                    self._consumir("sponto_virgula")
                    if not self.erro:
                        self.tabela.entrar_escopo()
                        self.analisar_bloco()
                        self.tabela.sair_escopo()

    def _analisa_declaracao_funcao(self):
        nome_funcao = self.token_atual.lexema
        tipo_retorno = None
        self._consumir("sidentificador")
        if not self.erro:
            self._consumir("sdoispontos")
            if not self.erro:
                if self.token_atual.simbolo in ["sinteiro", "sbooleano"]:
                    tipo_retorno = self.token_atual.lexema
                    self._consumir(self.token_atual.simbolo)
                    if not self.erro:
                        try:
                            self.tabela.adicionar_simbolo(nome_funcao, tipo=f'funcao {tipo_retorno}')
                        except ValueError as e:
                            print(f"Erro Semântico: {e}")
                            self.erro = True
                        if not self.erro:
                            self._consumir("sponto_virgula")
                            if not self.erro:
                                self.tabela.entrar_escopo()
                                self.analisar_bloco()
                                self.tabela.sair_escopo()
                else:
                    print("Erro sintático: Tipo de retorno esperado (inteiro ou booleano)")
                    self.erro = True
    
    def _analisa_expressao(self):
        self._analisa_expressao_simples()
        while self.token_atual and self.token_atual.simbolo in ["smaior", "smaiorigual", "smenor", "smenorigual", "sigual", "sdif"]:
            self._consumir(self.token_atual.simbolo)
            if not self.erro:
                self._analisa_expressao_simples()

    def _analisa_expressao_simples(self):
        if self.token_atual and self.token_atual.simbolo in ["smais", "smenos"]:
            self._consumir(self.token_atual.simbolo)
        
        self._analisa_termo()
        
        while self.token_atual and self.token_atual.simbolo in ["smais", "smenos", "sou", "se"]:
            self._consumir(self.token_atual.simbolo)
            if not self.erro:
                self._analisa_termo()

    def _analisa_termo(self):
        self._analisa_fator()
        while self.token_atual and self.token_atual.simbolo in ["smult", "sdiv", "se", "sou"]:
            self._consumir(self.token_atual.simbolo)
            if not self.erro:
                self._analisa_fator()

    def _analisa_fator(self):
        if self.token_atual.simbolo == "sidentificador":
            try:
                simbolo = self.tabela.buscar_simbolo(self.token_atual.lexema)
            except ValueError as e:
                print(f"Erro Semântico: {e}")
                self.erro = True
            self._consumir("sidentificador")
            if not self.erro and simbolo['tipo'] in ['funcao inteiro', 'funcao booleano']:
                self._analisa_chamada_funcao()
        elif self.token_atual.simbolo == "snumero":
            self._consumir("snumero")
        elif self.token_atual.simbolo in ["sverdadeiro", "sfalso"]:
            self._consumir(self.token_atual.simbolo)
        elif self.token_atual.simbolo == "sabre_parenteses":
            self._consumir("sabre_parenteses")
            if not self.erro:
                self._analisa_expressao()
                if not self.erro:
                    self._consumir("sfecha_parenteses")
        elif self.token_atual.simbolo == "snao":
            self._consumir("snao")
            if not self.erro:
                self._analisa_fator()
        else:
            print(f"Erro Sintático: Fator inválido ou inesperado '{self.token_atual.lexema}'.")
            self.erro = True

    def _analisa_atribuicao(self, simbolo):
        try:
            self.tabela.buscar_simbolo(simbolo)
        except ValueError as e:
            print(f"Erro Semântico: {e}")
            self.erro = True
        if not self.erro:
            self._analisa_expressao()
            if not self.erro:
                self._consumir("sponto_virgula")

    def _analisa_chamada_procedimento(self, simbolo):
        try:
            self.tabela.buscar_simbolo(simbolo)
        except ValueError as e:
            print(f"Erro Semântico: {e}")
            self.erro = True
        if not self.erro:
            self._consumir("sponto_virgula")

    def _analisa_chamada_funcao(self):
        self._consumir("sabre_parenteses")
        if not self.erro:
            self._consumir("sfecha_parenteses")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Erro: Modo de uso incorreto.")
        print("Uso: python analisador_sintatico.py <caminho_para_o_arquivo.jovane>")
        sys.exit(1) 

    caminho_arquivo = sys.argv[1]
    
    nome_base, extensao = os.path.splitext(caminho_arquivo)

    if extensao != '.jovane':
        print(f"Erro: O arquivo '{caminho_arquivo}' não é válido.")
        print("Por favor, forneça um arquivo .jovane")
        sys.exit(1)
    
    try:
        analisador = AnalisadorSintatico(caminho_arquivo)
        analisador.analisar()
    except Exception as e:
        print(f"Ocorreu um erro fatal durante a análise: {e}")