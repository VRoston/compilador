from analisador_lexical import get_token  # Ou importe tokens diretamente
from tabela_simbolos import TabelaSimbolos

class AnalisadorSintatico:
    def __init__(self, arquivo_entrada):
        print(f"DEBUG: Inicializando AnalisadorSintatico com arquivo '{arquivo_entrada}'")
        self.tokens = self.gerar_tokens(arquivo_entrada)
        print(f"DEBUG: Tokens gerados: {len(self.tokens)} tokens")
        self.pos = 0
        self.tabela = TabelaSimbolos()
        self.erros = []

    def gerar_tokens(self, arquivo):
        print(f"DEBUG: Gerando tokens para '{arquivo}'")
        tokens = []
        try:
            with open(arquivo, 'r') as file:
                while True:
                    char = file.read(1)
                    if not char:
                        print("DEBUG: Fim do arquivo alcançado")
                        break
                    if char.isspace():
                        continue
                    if char == '{':
                        comentario_fechado = False
                        while True:
                            char = file.read(1)
                            if not char:
                                break
                            if char == '}':
                                comentario_fechado = True
                                break
                        if not comentario_fechado:
                            token = Token("{", "serro")
                            tokens.append(token)
                        continue
                    token = get_token(char, file)
                    print(f"DEBUG: Token gerado: lexema='{token.lexema}', simbolo='{token.simbolo}'")
                    tokens.append(token)
        except Exception as e:
            print(f"DEBUG: Erro ao gerar tokens: {e}")
        return tokens

    def token_atual(self):
        token = self.tokens[self.pos] if self.pos < len(self.tokens) else None
        print(f"DEBUG: Token atual na posição {self.pos}: {token}")
        return token

    def consumir(self, simbolo_esperado):
        token = self.token_atual()
        if token and token.simbolo == simbolo_esperado:
            print(f"DEBUG: Consumindo token: '{simbolo_esperado}'")
            self.pos += 1
        else:
            erro = f"Erro: Esperado '{simbolo_esperado}', encontrado '{token.simbolo if token else 'EOF'}'"
            print(f"DEBUG: {erro}")
            self.erros.append(erro)

    def analisar_programa(self):
        print("DEBUG: Iniciando análise do programa")
        # Skip initial tokens until 'sprograma'
        while self.token_atual() and self.token_atual().simbolo != "sprograma":
            print(f"DEBUG: Pulando token inicial: {self.token_atual().simbolo}")
            self.pos += 1
        self.consumir("sprograma")
        self.consumir("sidentificador")
        self.consumir("sponto_virgula")
        # Skip extra semicolons
        while self.token_atual() and self.token_atual().simbolo == "sponto_virgula":
            self.consumir("sponto_virgula")
        self.analisar_bloco()
        self.consumir("sponto")
        print("DEBUG: Análise do programa concluída")

    def analisar_bloco(self):
        print("DEBUG: Iniciando análise do bloco")
        self.analisar_declaracoes()  # Declarações opcionais (var e procedimentos)
        self.consumir("sinicio")
        self.analisar_comandos()  # Comandos obrigatórios
        self.consumir("sfim")
        print("DEBUG: Análise do bloco concluída")

    def analisar_declaracoes(self):
        print("DEBUG: Iniciando análise de declarações")
        while self.token_atual() and self.token_atual().simbolo != "sinicio":
            if self.token_atual().simbolo == "svar":
                self.analisar_declaracao_var()
            elif self.token_atual().simbolo == "sprocedimento":
                self.analisar_declaracao_procedimento()
            elif self.token_atual().simbolo == "sidentificador":
                self.analisar_declaracao_var_without_var()
            else:
                break
        print("DEBUG: Análise de declarações concluída")

    def analisar_declaracao_var(self):
        print("DEBUG: Iniciando análise de declaração de variável")
        self.consumir("svar")
        ids = self.analisar_lista_ids()
        if self.token_atual() and self.token_atual().simbolo == "sponto_virgula":
            # Handle malformed: var a, x; inteiro;
            self.consumir("sponto_virgula")
            tipo = self.analisar_tipo()
            self.consumir("sponto_virgula")
        else:
            # Standard: var a, x: inteiro;
            self.consumir("sdoispontos")
            tipo = self.analisar_tipo()
            self.consumir("sponto_virgula")
        for id in ids:
            self.tabela.adicionar_simbolo(id, tipo)
        print("DEBUG: Análise de declaração de variável concluída")

    def analisar_declaracao_var_without_var(self):
        print("DEBUG: Iniciando análise de declaração de variável sem 'var'")
        ids = self.analisar_lista_ids()
        self.consumir("sdoispontos")
        tipo = self.analisar_tipo()
        self.consumir("sponto_virgula")
        for id in ids:
            self.tabela.adicionar_simbolo(id, tipo)
        print("DEBUG: Análise de declaração de variável sem 'var' concluída")

    def analisar_lista_ids(self):
        print("DEBUG: Iniciando análise de lista de IDs")
        ids = [self.token_atual().lexema]
        self.consumir("sidentificador")
        while self.token_atual() and self.token_atual().simbolo == "svirgula":
            self.consumir("svirgula")
            ids.append(self.token_atual().lexema)
            self.consumir("sidentificador")
        print(f"DEBUG: Lista de IDs: {ids}")
        return ids

    def analisar_tipo(self):
        print("DEBUG: Iniciando análise de tipo")
        if self.token_atual().simbolo == "sinteiro":
            self.consumir("sinteiro")
            print("DEBUG: Tipo 'inteiro'")
            return "inteiro"
        elif self.token_atual().simbolo == "sbooleano":
            self.consumir("sbooleano")
            print("DEBUG: Tipo 'booleano'")
            return "booleano"
        else:
            erro = "Erro: Tipo esperado (inteiro ou booleano)"
            print(f"DEBUG: {erro}")
            self.erros.append(erro)

    def analisar_declaracao_procedimento(self):
        print("DEBUG: Iniciando análise de declaração de procedimento")
        self.consumir("sprocedimento")
        nome = self.token_atual().lexema
        self.consumir("sidentificador")
        self.consumir("sponto_virgula")
        self.tabela.entrar_escopo()  # Novo escopo para o procedimento
        self.analisar_bloco()  # Bloco recursivo do procedimento
        self.tabela.sair_escopo()
        self.consumir("sponto_virgula")
        print("DEBUG: Análise de declaração de procedimento concluída")

    def analisar_comandos(self):
        print("DEBUG: Iniciando análise de comandos")
        while self.token_atual() and self.token_atual().simbolo not in ["sfim", "sponto"]:
            self.analisar_comando()
            # Assume commands are separated by semicolons; consume if present
            if self.token_atual() and self.token_atual().simbolo == "sponto_virgula":
                self.consumir("sponto_virgula")
        print("DEBUG: Análise de comandos concluída")

    def analisar_comando(self):
        print("DEBUG: Iniciando análise de comando")
        if self.token_atual().simbolo == "sidentificador":
            # Verificar se é atribuição ou chamada de procedimento
            prox_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if prox_token and prox_token.simbolo == "satribuicao":
                self.analisar_atribuicao()
            else:
                self.analisar_chamada_procedimento()
        elif self.token_atual().simbolo == "sse":
            self.analisar_se()
        elif self.token_atual().simbolo == "senquanto":
            self.analisar_enquanto()
        elif self.token_atual().simbolo == "sleia":
            self.analisar_leia()
        elif self.token_atual().simbolo == "sescreva":
            self.analisar_escreva()
        elif self.token_atual().simbolo == "sinicio":
            # Allow blocks as commands (e.g., in enquanto)
            self.analisar_bloco()
        else:
            erro = f"Erro: Comando inesperado '{self.token_atual().simbolo}'"
            print(f"DEBUG: {erro}")
            self.erros.append(erro)
            self.pos += 1  # Avançar para evitar loop infinito
        print("DEBUG: Análise de comando concluída")

    def analisar_atribuicao(self):
        print("DEBUG: Iniciando análise de atribuição")
        var = self.token_atual().lexema
        self.consumir("sidentificador")
        self.consumir("satribuicao")
        self.analisar_expressao()
        print("DEBUG: Análise de atribuição concluída")

    def analisar_chamada_procedimento(self):
        print("DEBUG: Iniciando análise de chamada de procedimento")
        nome = self.token_atual().lexema
        self.consumir("sidentificador")
        print("DEBUG: Análise de chamada de procedimento concluída")

    def analisar_se(self):
        print("DEBUG: Iniciando análise de comando 'se'")
        self.consumir("sse")
        self.analisar_expressao()
        self.consumir("sentao")
        self.analisar_comando()
        if self.token_atual() and self.token_atual().simbolo == "ssenao":
            self.consumir("ssenao")
            self.analisar_comando()
        print("DEBUG: Análise de comando 'se' concluída")

    def analisar_enquanto(self):
        print("DEBUG: Iniciando análise de comando 'enquanto'")
        self.consumir("senquanto")
        self.analisar_expressao()
        self.consumir("sfaca")
        self.analisar_comando()
        print("DEBUG: Análise de comando 'enquanto' concluída")

    def analisar_leia(self):
        print("DEBUG: Iniciando análise de 'leia'")
        self.consumir("sleia")
        self.consumir("sabre_parenteses")
        self.consumir("sidentificador")
        self.consumir("sfecha_parenteses")
        print("DEBUG: Análise de 'leia' concluída")

    def analisar_escreva(self):
        print("DEBUG: Iniciando análise de 'escreva'")
        self.consumir("sescreva")
        self.consumir("sabre_parenteses")
        self.analisar_expressao()
        self.consumir("sfecha_parenteses")
        print("DEBUG: Análise de 'escreva' concluída")

    def analisar_expressao(self):
        print("DEBUG: Iniciando análise de expressão")
        self.analisar_termo()
        while self.token_atual() and self.token_atual().simbolo in ["smais", "smenos", "smult", "sdiv", "smaior", "smenor", "sigual", "sdif", "smenorigual", "smaiorigual", "se", "sou"]:
            self.pos += 1  # Consume operator
            self.analisar_termo()
        print("DEBUG: Análise de expressão concluída")

    def analisar_termo(self):
        print("DEBUG: Iniciando análise de termo")
        if self.token_atual().simbolo == "sabre_parenteses":
            self.consumir("sabre_parenteses")
            self.analisar_expressao()
            self.consumir("sfecha_parenteses")
        elif self.token_atual().simbolo in ["sidentificador", "snumero"]:
            self.pos += 1  # Consume identifier or number
        else:
            erro = "Erro: Termo esperado (identificador, número ou parênteses)"
            print(f"DEBUG: {erro}")
            self.erros.append(erro)
        print("DEBUG: Análise de termo concluída")

    def analisar(self):
        print("DEBUG: Iniciando análise geral")
        self.analisar_programa()
        if self.erros:
            print("Erros sintáticos:", self.erros)
        else:
            print("Análise sintática bem-sucedida.")
        print("DEBUG: Análise geral concluída")

if __name__ == "__main__":
    # Exemplo: analisar sint2.txt
    print("DEBUG: Executando bloco principal")
    analisador = AnalisadorSintatico('./Testes Sintático/sint1.txt')
    analisador.analisar()