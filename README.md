# Compilador

Este projeto implementa **um compilador completo**, incluindo:

- **Analisador Léxico**
- **Analisador Sintático**
- **Analisador Semântico**
- **Gerador de Código Assembly**
- **Máquina Virtual (MVD)**
- **Interface gráfica**

O objetivo é permitir escrever programas, compilar para um assembly próprio, e executá-lo na MVD.

---

# Estrutura do Projeto

/compilador
analisador_lexical.py
analisador_sintatico.py
analisador_semantico.py
code_generator.py
core.py
gui.py
compilador_interface.py
loader.py
/output

# 1. Analisador Léxico — `analisador_lexical.py`

Responsável por:

- ler o arquivo fonte caractere por caractere
- ignorar espaços e comentários `{ ... }`
- identificar números, identificadores e palavras-reservadas
- reconhecer operadores e delimitadores
- gerar **tokens** com:  
  ➝ `lexema`, `simbolo`, `linha`

### Exemplos de tokens reconhecidos

| Lexema | Símbolo |
|--------|---------|
| `programa` | `sprograma` |
| `var` | `svar` |
| `:=` | `satribuicao` |
| `1` | `snumero` |
| `x` | `sidentificador` |

---

# 2. Analisador Sintático — `analisador_sintatico.py`

Implementa um **parser descendente recursivo**.

Funções principais:

- validar a estrutura do programa
- validar blocos, comandos e sub-rotinas
- organizar escopos
- chamar rotinas semânticas
- **gerar o assembly final** usando `Gera` (gera instruções MVD)

Também controla:

- empilhamento de escopos
- leitura completa das expressões
- conversão para pós-fixa
- geração de instruções antes/depois de loops, condições, funções, return, etc.

---

# 3. Analisador Semântico — `analisador_semantico.py`

Responsável por:

### Tabela de Símbolos
- múltiplos escopos
- empilhamento e desempilhamento
- endereçamento de variáveis
- memória global e local
- declarações duplicadas
- acesso a variáveis não declaradas

### Análise de Tipos
- verifica tipos em expressões pós-fixas
- aceita operadores unários: `+u`, `-u`, `nao`
- aceita `div`, `e`, `ou`
- garante coerência (mas permite continuar, apenas avisando)

---

# 4. Gerador de Código — `code_generator.py`

Classe **Gera** responsável por:

- emitir instruções na sintaxe da MVD
- organizar indentação
- criar rótulos automaticamente
- exportar o `.obj` para `/output/`

### Exemplo de instruções

...
START
ALLOC 0 3
LDC 5
STR 1
CALL L10
HLT
...


---

# 5. Máquina Virtual (MVD) — `core.py` e `gui.py`

Implementa uma máquina virtual **com pilha dinâmica e shadow-stack**, suportando:

### Instruções de Controle
- `START`, `HLT`
- `JMP`, `JMPF`
- `CALL`, `RETURN`

### Manipulação de Pilha
- `ALLOC`, `DALLOC` com shadow-stack seguro
- recursão robusta
- frame de variáveis locais preservado

### Entrada e Saída
- `RD`
- `PRN`

### Aritmética e Operadores
- `ADD`, `SUB`, `MULT`, `DIVI`
- `CME`, `CMA`, `CEQ`, `CDIF`, `CMEQ`, `CMAQ`

### Interface

Arquivo `gui.py` fornece:

- campo para carregar o assembly
- botão de rodar programa
- passo-a-passo (debug)
- exibição de memória, pilha, saída e estado atual da VM

# 6. Interface do Compilador — `compilador_interface.py`

Um editor de texto com:

- números de linha
- abrir/salvar arquivo
- botão “Executar”
- saída com destaque de erros
- clique no erro → navega até a linha no editor

Fluxo:

1. Usuário seleciona o `.obj`.
2. Pressiona **Executar**.
3. O arquivo é compilado via:

   python3 analisador_sintatico.py <arquivo>


4. A saída ou erros aparecem na caixa inferior.
5. Em caso de sucesso, o assembly `.obj` aparece em `/output/`.

# 7. Leitor de Arquivos Assembly — `loader.py`

Interpretador auxiliar usado pela GUI.

Responsabilidades:

- carregar o assembly gerado
- remover comentários
- detectar rótulos
- mapear rótulos → índices
- criar lista linear de instruções para a VM

# 7. Estruturas de Dados Utilizadas no Compilador

## 1. Estruturas de Dados do Analisador Léxico

O léxico trabalha principalmente com uma classe:

### **Token**
Cada token é representado como um objeto:

```python
Token(lexema='x', simbolo='sidentificador', linha=3)
```

O léxico mantém:

- **keywords (dict)** → mapeia palavras reservadas → símbolo interno  
- **linha_atual (int)** → contador de linha  
- **arquivo aberto (file handle)**  

O fluxo é simples:

1. lê um caractere
2. identifica padrão
3. cria um `Token`
4. retorna para o Sintático

Tokens são armazenados apenas **um por vez**, não há fila — o sintático consome conforme necessário.

---

## 2. Estruturas de Dados do Analisador Sintático

O sintático utiliza:

### **Buffer único do token atual**
A cada chamada de função, ele chama `proximo_token()` do léxico.

### **Chamadas recursivas**
Cada não-terminal da gramática vira uma função Python.

### **Acúmulo temporário de instruções**
Quando o Sintático reconhece construções da linguagem, ele chama:

```python
Gera.instrucao("ADD")
```

As instruções são concatenadas em uma lista interna:

```
P = [
  ("START", None, None),
  ("LDC", 5, None),
  ("STR", 1, None),
  ...
]
```

### **Mapeamento de rótulos**
O sintático cria rótulos automaticamente:

```
L10, L20, L21, ...
```

São guardados em uma pilha/lista simples até serem usados.

---

## 3. Estruturas do Analisador Semântico

O semântico usa duas estruturas principais:

---

## A) *Tabela de Símbolos*

Implementada como:

```python
self.escopos = [ {} ]
```

Ou seja:

- cada **escopo** é um dict  
- o topo da lista é o escopo atual  
- identificadores são armazenados assim:

```
{
  'a': { nome: 'a', tipo: 'inteiro', memoria: 3, escopo: 1 },
  'x': { nome: 'x', tipo: 'booleano', memoria: 4, escopo: 1 }
}
```

Quando entra em um bloco:

```
entrar_escopo()
```

é feito:

```
escopos.append({})
nivel_atual++
```

Quando sai:

```
escopos.pop()
restaura endereços de memória
```

---

## B) *Inferência de tipos*
O semântico usa uma **pilha de tipos**:

Exemplo de pós-fixa:

```
a 1 + b >
```

A pilha evolui:

```
['inteiro']
['inteiro', 'inteiro']
['inteiro']
['inteiro', 'inteiro']
['booleano']
```

Sempre checando coerência:

- operadores binários
- operadores unários
- literais (booleano / inteiro)
- chamadas de função
- compatibilidade geral

---

## 4. Estruturas da MVD (Máquina Virtual Didática)

A MVD foi construída para simular uma arquitetura de pilha.

### Principais estruturas:

### **P** → Programa (lista de instruções)  
Cada entrada é uma tupla:

```
("LDC", 5, None)
("STR", 1, None)
("CALL", "L10", None)
```

### **M[]** → Memória da máquina  
Lista dinâmica com inteiros:

```
M = [ None, 10, 20, -3, ... ]
```

### **Registradores**

| Nome | Função |
|------|--------|
| `i` | índice da instrução atual |
| `s` | topo da pilha |
| `H` | modo de parada (HLT) |
| `aguardando_input` | controle do RD |

### **Shadow Stack**
Usado em ALLOC/DALLOC:

- quando entra em função:
  - salva valores antigos
  - aloca variáveis locais
- quando sai:
  - restaura valores
  - desfaz alocação

Isso torna **recursão 100% segura**.

---

# 5. Fluxo Completo da Execução do Compilador

1. **Léxico** → transforma texto em tokens  
2. **Sintático** → valida a gramática  
3. **Semântico** → verifica tipos e escopos  
4. **Gerador** → cria o assembly `.obj`  
5. **Loader** → converte o `.obj` para lista de instruções  
6. **MVD** → executa instrução por instrução  
7. **GUI** (opcional) → controla execução gráfica  
   
---

# Como Rodar o Compilador no Linux (com venv)

A execução do projeto requer **Python 3.10+**.

## 1. Criar ambiente virtual

```bash
python3 -m venv venv
```

Ativar:

```bash
source venv/bin/activate
```

## 2. Instalar dependências

```bash
sudo apt install python3-tk
```

## 3. Rodar o Compilador

Execute:

```bash
python3 compilador_interface.py
```

A interface abrirá com:

- botão **Passo-a-passo**
- botão **Executar**
- botão **Parar**
- botão **Resetar**
- botão para carregar o **.obj**
- área de erros
- acesso à MVD

---

# Como Usar o Compilador

### 1. Escreva um programa
Exemplo:

programa teste;

var a: inteiro;

inicio
a := 10;
fim.

### 2. Gere o `.obj`
- `/output/<arquivo>.obj` será criado.

### 3. Para rodar na Máquina Virtual:

Abra a interface da VM:

Carregue o `.obj` e execute.

# Como Funciona a Máquina Virtual

### Registradores Principais

| Registrador | Função |
|-------------|--------|
| `i` | índice da instrução atual |
| `s` | topo da pilha |
| `M[]` | memória geral |
| `P[]` | programa (assembly) |

### Sobre ALLOC / DALLOC

#### ALLOC m n
1. garante espaço para variáveis locais  
2. salva valores antigos (shadow-stack)  
3. ajusta s corretamente

#### DALLOC m n
1. restaura variáveis do escopo anterior  
2. desempilha shadow-stack  

Isso permite:

- recursão correta  
- reentrada em funções  
- não corromper globais  
- variáveis locais sobrepostas
