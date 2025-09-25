from analisador_lexical import lexical, Token  # Import Token class
from tabela_simbolos import TabelaSimbolos

class AnalisadorSintatico:
    def __init__(self, arquivo_entrada):
        self.lexador = AnalisadorLexical(arquivo_entrada)
        self.token_atual = None
        self.erro = False
        self.tabela = TabelaSimbolos() # Descomente quando tiver o ficheiro da tabela

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

    def _analisar_programa(self):
        """Analisa a estrutura principal do programa."""     
        self._consumir("sprograma")
        if not self.erro:
            self._consumir("sidentificador")
            if not self.erro:
                self.tabela.adicionar_simbolo(self.token_atual.lexema, tipo='programa')
                self._consumir("sponto_virgula")
                if not self.erro:
                    self.analisar_bloco()
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
            self.consumir("svar")

            while self.token_atual and self.token_atual.simbolo == "sidentificador":
                self._analisa_variaveis()


    def _analisa_variaveis(self):
        """Analisa uma linha de declaração como 'a, b, c : inteiro;'"""
        variaveis_para_declarar = []
        
        # 1. Coletar todos os identificadores (ex: 'a', 'b', 'c')
        while self.token_atual and self.token_atual.simbolo == "sidentificador":
            variaveis_para_declarar.append(self.token_atual.lexema)
            self.consumir("sidentificador")
            if self.token_atual.simbolo == "svirgula":
                self.consumir("svirgula")
            else:
                break
        
        # 2. Consumir os dois-pontos e o tipo
        self.consumir("sdoispontos")
        
        tipo_das_variaveis = None
        if self.token_atual and self.token_atual.simbolo in ["sinteiro", "sbooleano"]:
            tipo_das_variaveis = self.token_atual.lexema # Guarda o tipo (ex: 'inteiro')
            self.consumir(self.token_atual.simbolo)
        else:
            print("Erro sintático: Tipo esperado (inteiro ou booleano)")
            self.erro = True
            return

        # 3. INSERÇÃO NA TABELA: Inserir cada variável coletada com o tipo encontrado
        if tipo_das_variaveis:
            for nome_var in variaveis_para_declarar:
                try:
                    self.tabela.adicionar_simbolo(nome_var, tipo=tipo_das_variaveis)
                    print(f"DEBUG: Inserida variável '{nome_var}' do tipo '{tipo_das_variaveis}' na tabela.")
                except ValueError as e:
                    print(f"Erro Semântico: {e}")
                    self.erro = True

        self.consumir("sponto_virgula")
    
    def _analisa_subrotinas(self):
        pass

    def _analisa_comandos(self):
        pass

if __name__ == "__main__":
    # Exemplo: analisar sint2.txt
    print("DEBUG: Executando bloco principal")
    analisador = AnalisadorSintatico('./Testes Sintático/sint1.txt')
    analisador.analisar()
    