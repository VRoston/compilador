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

def main():
    try:
        nome_arquivo_entrada = './test.txt'
        nome_arquivo_saida = "tabela_simbolos.txt"

        with open(nome_arquivo_entrada, 'r') as file, open(nome_arquivo_saida, 'w') as out:
            print("Arquivo de entrada aberto com sucesso!")
            
            out.write("Tabela de Símbolos:\n")
            out.write(f"{'Lexema':<20} | {'Simbolo':<20}\n")
            out.write("-" * 20 + "-+-" + "-" * 21 + "\n")
 
            while True:
                char = file.read(1)
 
                if not char:
                    break

                if char.isspace():
                    continue

                if char == '{':
                    while char != '}' and char:
                        char = file.read(1)
                    continue

                token = get_token(char, file)
     
                out.write(f"{token.lexema:<20} | {token.simbolo:<20}\n")

            print(f"Análise concluída! Tabela de símbolos salva em '{nome_arquivo_saida}'.")

    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo_entrada}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

    print("Fim do arquivo")

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

if __name__ == "__main__":
    main()