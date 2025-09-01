import re

def __main__():
  arquivo = read_file('./test.txt')
  arquivo = clean(arquivo)
  print(arquivo)

# FUNÇÕES DO PROGRAMA  
  # Lê o arquivo e retorna o conteúdo
def read_file(file):
  try:
    with open(file, 'r') as file:
      conteudo = file.read()
      return conteudo

  except FileNotFoundError:
      print("O arquivo não foi encontrado.")
      return None

  except Exception as e:
      print(f"Ocorreu um erro: {e}")
      return None

  # Limpa o arquivo
def clean(file):
  file = file.replace('\n', '').replace(' ', '').replace('\t', '')
  file = re.sub(r'\{.*?\}', '', file) 
  return file

def handle_text(file):
  pass

def handle():
  pass

__main__()