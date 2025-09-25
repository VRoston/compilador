# analisador_lexical.py

class Token:
    def __init__(self, lexema, simbolo):
        self.lexema = lexema
        self.simbolo = simbolo

    def __repr__(self):
        return f"Token(lexema='{self.lexema}', simbolo='{self.simbolo}')"

class AnalisadorLexical:
    """
    Lê um ficheiro de código e retorna um token de cada vez, sob demanda.
    """
    def __init__(self, nome_arquivo):
        try:
            self.file = open(nome_arquivo, 'r')
        except FileNotFoundError:
            raise Exception(f"Error: File '{nome_arquivo}' not found.")
        
        self.keywords = {
            "programa": "sprograma", "se": "sse", "entao": "sentao", "senao": "ssenao",
            "enquanto": "senquanto", "faca": "sfaca", "inicio": "sinicio", "fim": "sfim",
            "escreva": "sescreva", "leia": "sleia", "var": "svar", "inteiro": "sinteiro",
            "booleano": "sbooleano", "verdadeiro": "sverdadeiro", "falso": "sfalso",
            "procedimento": "sprocedimento", "funcao": "sfuncao", "div": "sdiv",
            "e": "se", "ou": "sou", "nao": "snao",
        }

    def proximo_token(self):
        """Lê o ficheiro e retorna o próximo token válido, ou None se for o fim."""
        while True:
            char = self.file.read(1)
            
            if not char:
                return None # Fim do ficheiro

            if char.isspace():
                continue

            if char == '{':
                comentario_fechado = False # CORRIGIDO: Inicializa a variável
                while True:
                    char = self.file.read(1)
                    if not char: # Fim do ficheiro
                        break
                    if char == '}':
                        comentario_fechado = True
                        break
                
                if not comentario_fechado:
                    print("Erro lexical: Comentário não fechado.")
                    return Token("{", "serro")
                continue

            return self._get_token(char)

    def fechar(self):
        """Fecha o ficheiro. Essencial chamar no final da análise."""
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
            return self._handle_arithmetic_operator(char)
        elif char in ['<', '>', '=', '!']:
            # CORRIGIDO: A chamada agora está correta
            return self._handle_relational_operator(char)
        elif char in ['.', ';', ',', '(', ')']:
            return self._handle_punctuation(char)
        else:
            print(f"Erro lexical: Símbolo inválido '{char}'")
            return Token(char, "serro")
    
    def _handle_arithmetic_operator(self, char):
        return Token(char, {'+': 'smais', '-': 'smenos', '*': 'smult'}.get(char))
    
    def _handle_punctuation(self, char):
        return Token(char, {'.': 'sponto', ';': 'sponto_virgula', ',': 'svirgula', '(': 'sabre_parenteses', ')': 'sfecha_parenteses'}.get(char))

    # CORRIGIDO: Assinatura e corpo do método
    def _handle_relational_operator(self, char):
        lexema = char
        prox_char = self.file.read(1)

        def ungetc():
            if prox_char: self.file.seek(self.file.tell() - 1)

        if char == '<':
            if prox_char == '=': return Token("<=", "smenorigual")
            if prox_char == '>': return Token("<>", "sdif")
            ungetc(); return Token("<", "smenor")
        elif char == '>':
            if prox_char == '=': return Token(">=", "smaiorigual")
            ungetc(); return Token(">", "smaior")
        elif char == '=':
            # CORRIGIDO: Um único '=' é o operador de igualdade
            ungetc(); return Token("=", "sigual")
        elif char == '!':
            if prox_char == '=': return Token("!=", "sdif")
            ungetc()
            print(f"Erro lexical: Símbolo '!' inválido. Talvez quisesse dizer '!='?")
            return Token("!", "serro")

    def _handle_assignment(self, char):
        prox_char = self.file.read(1)
        if prox_char == '=':
            return Token(":=", "satribuicao")
        else:
            if prox_char: self.file.seek(self.file.tell() - 1)
            return Token(":", "sdoispontos")

    def _handle_identifier_or_keyword(self, char):
        lexema = char
        while True:
            prox_char = self.file.read(1)
            if prox_char and (prox_char.isalnum() or prox_char == '_'):
                lexema += prox_char
            else:
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
                if prox_char: self.file.seek(self.file.tell() - 1)
                break
        return Token(lexema, "snumero")