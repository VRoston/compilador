class Token:
    def __init__(self, lexema, simbolo):
        self.lexema = lexema
        self.simbolo = simbolo

KEYWORDS = {
    "programa": "sprograma",
    "se": "sse",
    "entao": "sentao",
    "senao": "ssenao",
    "enquanto": "senquanto",
    "faca": "sfaca",
    "inicio": "sinicio",
    "fim": "sfim",
    "escreva": "sescreva",
    "leia": "sleia",
    "var": "svar",
    "inteiro": "sinteiro",
    "booleano": "sbooleano",
    "verdadeiro": "sverdadeiro",
    "falso": "sfalso",
    "procedimento": "sprocedimento",
    "funcao": "sfuncao",
    "div": "sdiv",
    "e": "se",
    "ou": "sou",
    "nao": "snao",
}

def gerar_tokens(arquivo):
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

def get_token(char, file):
    if char.isdigit():
        return handle_digit(char, file)
    elif char.isalpha():
        return handle_identifier_or_keyword(char, file)
    elif char == ':':
        return handle_assignment(char, file)
    elif char in ['+', '-', '*']:
        return handle_arithmetic_operator(char)
    elif char in ['<', '>', '=', '!']:
        return handle_relational_operator(char, file)
    elif char in ['.', ';', ',', '(', ')']:
        return handle_punctuation(char)
    else:
        return Token(char, "serro")

def handle_punctuation(char):
    lexema = char
    simbolo_map = {
        '.': 'sponto',
        ';': 'sponto_virgula',
        ',': 'svirgula',
        '(': 'sabre_parenteses',
        ')': 'sfecha_parenteses'
    }
    simbolo = simbolo_map.get(char, 'serro')
    return Token(lexema, simbolo)
    
def handle_relational_operator(char, file):
    lexema = char
    prox_char = file.read(1)
    if char == '<':
        if prox_char == '=':
            lexema += prox_char
            return Token(lexema, "smenorigual")
        elif prox_char == '>':
            lexema += prox_char
            return Token(lexema, "sdif")
        else:
            if prox_char:
                file.seek(file.tell() - 1)
            return Token(lexema, "smenor")
    elif char == '>':
        if prox_char == '=':
            lexema += prox_char
            return Token(lexema, "smaiorigual")
        else:
            if prox_char:
                file.seek(file.tell() - 1)
            return Token(lexema, "smaior")
    elif char == '=':
        if prox_char == '=':
            lexema += prox_char
            return Token(lexema, "sigual")
        else:
            if prox_char:
                file.seek(file.tell() - 1)
            return Token(lexema, "serro")
    elif char == '!':
        if prox_char == '=':
            lexema += prox_char
            return Token(lexema, "sdif")
        else:
            if prox_char:
                file.seek(file.tell() - 1)
            return Token(lexema, "serro")
    else:
        return Token(lexema, "serro")

def handle_arithmetic_operator(char):
    lexema = char
    simbolo_map = {
        '+': 'smais',
        '-': 'smenos',
        '*': 'smult'
    }
    simbolo = simbolo_map.get(char, 'serro')
    return Token(lexema, simbolo)

def handle_assignment(char, file):
    lexema = char
    prox_char = file.read(1)
    if prox_char == '=':
        lexema += prox_char
        return Token(lexema, "satribuicao")
    else:
        if prox_char:
            file.seek(file.tell() - 1)
        return Token(lexema, "sdoispontos")


def handle_identifier_or_keyword(char, file):
    lexema = char
    while True:
        prox_char = file.read(1)
        if prox_char.isalnum() or prox_char == '_':
            lexema += prox_char
        else:
            if prox_char:
                file.seek(file.tell() - 1)
            break

    simbolo = KEYWORDS.get(lexema, "sidentificador")
    return Token(lexema, simbolo)

def handle_digit(char, file):
    lexema = char
    while True:
        prox_char = file.read(1)
        if prox_char.isdigit():
            lexema += prox_char
        else:
            if prox_char:
                file.seek(file.tell() - 1)
            break
    return Token(lexema, "snumero")