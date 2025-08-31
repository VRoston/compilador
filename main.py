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

def clean(file):
  file = file.replace('\n', '').replace(' ', '')

  return file

def handle_text(file):
  pass
def handle_attr(file):
  pass

arquivo = read_file('./test.txt')
print(arquivo)