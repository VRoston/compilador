pos = 0

class Token:
    def __init__(self, lexema, simbolo):
        self.lexema = lexema
        self.simbolo = simbolo

def main():
    try:
        nome_arquivo_entrada = './compilador/test.txt'
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

                token = get_token(char, file)
     
                out.write(f"{token.lexema:<20} | {token.simbolo:<20}\n")

            print(f"Análise concluída! Tabela de símbolos salva em '{nome_arquivo_saida}'.")

    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo_entrada}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

    print("Fim do arquivo")

def get_token(char, file):
    if isdigit(char):
        return handdle_digit(char, file)

def handdle_digit(char, file):
    lexema = char
    char = file.read(1)
    while char.isdigit():
        lexema += char
        char = file.read(1)
    global pos
    pos += len(lexema)
    file.seek(pos)
    return Token(lexema, "num")

if __name__ == "__main__":
    main()