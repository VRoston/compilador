# analisador_lexical.py (VERSÃO FINAL COM DEBUG)

class Token:
    def __init__(self, lexema, simbolo):
        self.lexema = lexema
        self.simbolo = simbolo

    def __repr__(self):
        return f"Token(lexema='{self.lexema}', simbolo='{self.simbolo}')"

class AnalisadorLexical:
    def __init__(self, nome_arquivo):
        try:
            self.file = open(nome_arquivo, 'r')
        except FileNotFoundError:
            raise Exception(f"Erro: Ficheiro '{nome_arquivo}' não encontrado.")
        
        self.keywords = {
            "programa": "sprograma", "se": "sse", "entao": "sentao", "senao": "ssenao",
            "enquanto": "senquanto", "faca": "sfaca", "inicio": "sinicio", "fim": "sfim",
            "escreva": "sescreva", "leia": "sleia", "var": "svar", "inteiro": "sinteiro",
            "booleano": "sbooleano", "verdadeiro": "sverdadeiro", "falso": "sfalso",
            "procedimento": "sprocedimento", "funcao": "sfuncao", "div": "sdiv",
            "e": "se", "ou": "sou", "nao": "snao",
        }

    def proximo_token(self):
        """Versão simplificada e corrigida para ler o próximo token."""
        char = self.file.read(1)
        # 1. Loop para ignorar todos os espaços em branco e comentários
        while char and (char.isspace() or char == '{'):
            if char == '{':
                # Consome tudo até encontrar o '}'
                while char and char != '}':
                    char = self.file.read(1)
            # Lê o próximo caractere após o comentário ou espaço em branco
            char = self.file.read(1)
        
        # 2. Se chegámos ao fim do ficheiro, retorna None
        if not char:
            return None

        # 3. Se temos um caractere válido, retorna o seu token
        return self._get_token(char)

    def fechar(self):
        if self.file:
            self.file.close()

    def _get_token(self, char):
        if char.isdigit():
            return self._handle_digit(char)
        elif char.isalpha():
            return self._handle_identifier_or_keyword(char)
        elif char == ':':
            return self._handle_assignment(char)
        elif char in ['+', '-', '*']:
            return Token(char, {'+': 'smais', '-': 'smenos', '*': 'smult'}.get(char))
        elif char in ['<', '>', '=', '!']:
            return self._handle_relational_operator(char)
        elif char in ['.', ';', ',', '(', ')']:
            return Token(char, {'.': 'sponto', ';': 'sponto_virgula', ',': 'svirgula', '(': 'sabre_parenteses', ')': 'sfecha_parenteses'}.get(char))
        else:
            return Token(char, "serro")

    def _handle_relational_operator(self, char):
        prox_char = self.file.read(1)
        
        if char == '<':
            if prox_char == '=': return Token("<=", "smenorigual")
            if prox_char == '>': return Token("<>", "sdif")
        elif char == '>':
            if prox_char == '=': return Token(">=", "smaiorigual")
        elif char == '!':
            if prox_char == '=': return Token("!=", "sdif")

        # Se não formou um par, devolve o caractere lido a mais
        if prox_char: self.file.seek(self.file.tell() - 1)
        
        if char == '=': return Token("=", "sigual")
        if char == '<': return Token("<", "smenor")
        if char == '>': return Token(">", "smaior")
        return Token(char, "serro") # Caso de '!' sozinho

    def _handle_assignment(self, char):
        prox_char = self.file.read(1)
        if prox_char == '=':
            return Token(":=", "satribuicao")
        else:
            # CORRIGIDO: Lógica de devolução de caractere
            if prox_char: self.file.seek(self.file.tell() - 1)
            return Token(":", "sdoispontos")

    def _handle_identifier_or_keyword(self, char):
        lexema = char
        while True:
            prox_char = self.file.read(1)
            if prox_char and (prox_char.isalnum() or prox_char == '_'):
                lexema += prox_char
            else:
                # CORRIGIDO: Lógica de devolução de caractere
                if prox_char: self.file.seek(self.file.tell() - 1)
                break
        return Token(lexema, self.keywords.get(lexema, "sidentificador"))

    def _handle_digit(self, char):
        lexema = char
        while True:
            prox_char = self.file.read(1)
            if prox_char and prox_char.isdigit():
                lexema += prox_char
            else:
                # CORRIGIDO: Lógica de devolução de caractere
                if prox_char: self.file.seek(self.file.tell() - 1)
                break
        return Token(lexema, "snumero")