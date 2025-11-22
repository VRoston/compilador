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










