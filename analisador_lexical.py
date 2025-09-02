import re

class Token:
    def __init__(self, lex, symbol):
        self.lexema = lex
        self.simbolo = symbol

def __main__():
  arquivo = read_file('./compilador/test.txt')
  if arquivo is None:
      return

  pos = 0
  tamanho_arquivo = len(arquivo)

  while pos < tamanho_arquivo:
      char_atual = arquivo[pos]

      if char_atual in (' ', '\n', '\t', '\b'):
          pos += 1

      elif char_atual == '{':
          pos += 1 

          while pos < tamanho_arquivo and arquivo[pos] != '}':
              pos += 1

          if pos < tamanho_arquivo and arquivo[pos] == '}':
              pos += 1
          
      else:
          pos += 1

  print("Fim do arquivo")
#
__main__()