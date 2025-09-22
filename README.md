# compilador

## Como executar em ambiente Linux (WSL/Ubuntu)

### 1. Instale o Python (caso necessário)

Abra o terminal e execute:

```bash
sudo apt update
sudo apt install python3
```

Verifique a instalação com:

```bash
python3 --version
```

### 2. Execute o analisador léxico

Certifique-se de que o arquivo `test.txt` está presente na mesma pasta do projeto.

Para rodar o analisador léxico e gerar a tabela de símbolos, execute:

```bash
python3 analisador_lexical.py
```

O resultado será salvo no arquivo `tabela_simbolos.txt`.

---

Este projeto foi desenvolvido para fins de estudos