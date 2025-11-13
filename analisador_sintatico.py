import sys
import os
from analisador_lexical import AnalisadorLexical, Token
from tabela_simbolos import TabelaSimbolos
from code_generator import CodeGenerator


class AnalisadorSintatico:
    def __init__(self, arquivo_entrada):
        self.lexador = AnalisadorLexical(arquivo_entrada)
        self.token_atual = None
        self.erro = False
        self.tabela = TabelaSimbolos()
        self.codegen = CodeGenerator("output.mvd")

        self.keywords = {
            "sprograma": "programa",
            "sinicio": "inicio",
            "sfim": "fim",
            "sprocedimento": "procedimento",
            "sfuncao": "funcao",
            "sse": "se",
            "sentao": "entao",
            "ssenao": "senao",
            "senquanto": "enquanto",
            "sfaca": "faca",
            "satribuicao": ":=",
            "sescreva": "escreva",
            "sleia": "leia",
            "svar": "var",
            "sinteiro": "inteiro",
            "sbooleano": "booleano",
            "sidentificador": "identificador",
            "snumero": "numero",
            "sponto": ".",
            "sponto_virgula": ";",
            "svirgula": ",",
            "sabre_parenteses": "(",
            "sfecha_parenteses": ")",
            "smaior": ">",
            "smaiorigual": ">=",
            "sigual": "=",
            "smenor": "<",
            "smenorigual": "<=",
            "sdif": "!=",
            "smais": "+",
            "smenos": "-",
            "smult": "*",
            "sdiv": "div",
            "se": "e",
            "sou": "ou",
            "snao": "nao",
            "sdoispontos": ":",
            "sverdadeiro": "verdadeiro",
            "sfalso": "falso",
            "serro": "erro",
        }

    def _consumir(self, simbolo_esperado):
        """Verifica o token atual e avança para o próximo."""
        if self.token_atual:
            simbolo_anterior = self.token_atual.simbolo
            if self.token_atual.simbolo == simbolo_esperado:
                self.token_atual = self.lexador.proximo_token()
            else:
                simbolo_encontrado = self.token_atual.lexema
                if self.token_atual.simbolo != "serro":
                    print(f"Erro sintático na linha {self.token_atual.linha}: Esperado '{self.keywords[simbolo_esperado]}', mas encontrado '{simbolo_encontrado}'")
                self.erro = True
                return

            if self.token_atual:
                if simbolo_anterior == self.token_atual.simbolo and simbolo_anterior not in ["sinicio"]:
                    print(f"Erro Sintático na linha {self.token_atual.linha}: Símbolo '{self.token_atual.lexema}' duplicado.")
                    self.erro = True
                    return

        else:
            print(f"Erro sintático: Esperado '{self.keywords[simbolo_esperado]}', mas encontrado 'EOF'")

    def analisar(self):
        self.token_atual = self.lexador.proximo_token()
        self._analisar_programa()
        self.lexador.fechar()
        if not self.erro:
            nivel = 0
            num_vars = len(self.tabela.escopos[nivel]) if nivel in self.tabela.escopos else 0
            if num_vars > 0:
                self.codegen.daloc(num_vars)

            self.codegen.halt()
            self.codegen.write_file()
            print(f"Código gerado em: {self.codegen.filename}")

    def _analisar_programa(self):
        """Analisa a estrutura principal do programa."""
        self._consumir("sprograma")
        if not self.erro:
            self.tabela.adicionar_simbolo(self.token_atual.lexema, tipo='programa')
            self._consumir("sidentificador")
            if not self.erro:
                self._consumir("sponto_virgula")
                self.codegen.start_program()

                self.label_main = self.codegen.new_label()
                self.codegen.jmp(self.label_main)

                self._analisa_subrotinas()

                self.codegen.place_label(self.label_main)
                if not self.erro:
                    self.analisar_bloco(final=True)

    def analisar_bloco(self, final=False):
        self._analisa_et_variaveis()
        nivel = self.tabela.nivel_atual
        num_vars = len(self.tabela.escopos[nivel])
        if num_vars > 0:
            self.codegen.alloc(num_vars)

        if not self.erro:
            self._analisa_subrotinas()
            if not self.erro:
                self._analisa_comandos(final=final)

        if not self.erro and not final and num_vars > 0:
            self.codegen.daloc(num_vars)
        # Inicializa todas as variáveis globais com 0 no início do programa
        if nivel == 0 and num_vars > 0:
            for var in self.tabela.escopos[nivel]:
                self.codegen.ldc(0)
                self.codegen.str_(self.tabela.escopos[nivel][var]['memoria'])


    def _analisa_et_variaveis(self):
        """Analisa todas as seções de declaração de variáveis."""
        if self.token_atual and self.token_atual.simbolo == "svar":
            self._consumir("svar")
            if not self.erro:
                while self.token_atual and self.token_atual.simbolo == "sidentificador":
                    self._analisa_variaveis()

    def _analisa_variaveis(self):
        """Analisa uma linha de declaração como 'a, b, c : inteiro;'"""
        variaveis_para_declarar = []

        if self.token_atual and self.token_atual.simbolo == "sidentificador" and not self.erro:
            variaveis_para_declarar.append(self.token_atual.lexema)
            self._consumir("sidentificador")

        while self.token_atual and self.token_atual.simbolo == "svirgula" and not self.erro:
            self._consumir("svirgula")

            variavel = self.token_atual.lexema
            self._consumir("sidentificador")
            if not self.erro:
                variaveis_para_declarar.append(variavel)

        # 2. Consumir os dois-pontos e o tipo
        self._consumir("sdoispontos")
        if self.erro:
            return

        tipo_das_variaveis = None
        if self.token_atual and self.token_atual.simbolo in ["sinteiro", "sbooleano"]:
            tipo_das_variaveis = self.token_atual.lexema # Guarda o tipo (ex: 'inteiro')
            self._consumir(self.token_atual.simbolo)
        else:
            print(f"Erro sintático na linha {self.token_atual.linha}: Tipo esperado (inteiro ou booleano)")
            self.erro = True
            return

        # 3. INSERÇÃO NA TABELA: Inserir cada variável coletada com o tipo encontrado
        if tipo_das_variaveis:
            for nome_var in variaveis_para_declarar:
                try:
                    self.tabela.adicionar_simbolo(nome_var, tipo=tipo_das_variaveis)
                except ValueError as e:
                    print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
                    self.erro = True

        self._consumir("sponto_virgula")

    def _analisa_comandos(self, final=False):
        if self.token_atual and self.token_atual.simbolo == "sinicio":
            self._consumir("sinicio")
            while self.token_atual and self.token_atual.simbolo != "sfim" and not self.erro:
                self._analisa_comando_simples()

            if not self.erro:
                self._consumir("sfim")
                if not self.erro and final:
                    self._consumir("sponto")

                if not self.erro and not final:
                    self._consumir("sponto_virgula")
        else:
            print(f"Erro sintático na linha {self.token_atual.linha}: Esperado 'inicio' para iniciar o bloco de comandos.")
            self.erro = True


    def _analisa_comando_simples(self, sentao_ssenao = False):
        """Analisa um comando simples dentro do bloco de comandos."""
        if self.token_atual.simbolo == "sidentificador":
            self._analisa_atrib_chprocedimento()
            if self.token_atual.simbolo == "sfim":
                return
            elif not self.erro and sentao_ssenao:
                if self.token_atual.simbolo == "sponto_virgula":
                    self._consumir("sponto_virgula")
                return
            elif not self.erro:
                self._consumir("sponto_virgula")

        elif self.token_atual.simbolo == "sse":
            self._analisa_se()

        elif self.token_atual.simbolo == "senquanto":
            self._analisa_enquanto()

        elif self.token_atual.simbolo == "sescreva":
            self._analisa_escreva()
            if self.token_atual.simbolo == "sfim":
                return
            elif not self.erro and sentao_ssenao:
                if self.token_atual.simbolo == "sponto_virgula":
                    self._consumir("sponto_virgula")
                return
            elif not self.erro:
                self._consumir("sponto_virgula")

        elif self.token_atual.simbolo == "sleia":
            self._analisa_leia()
            if self.token_atual.simbolo == "sfim":
                return
            elif not self.erro and sentao_ssenao:
                if self.token_atual.simbolo == "sponto_virgula":
                    self._consumir("sponto_virgula")
                return
            elif not self.erro:
                self._consumir("sponto_virgula")

        elif self.token_atual.simbolo == "sinicio":
            self._analisa_comandos()
        else:
            print(f"Erro Sintático na linha {self.token_atual.linha}: Comando inválido ou inesperado '{self.token_atual.lexema}'.")
            self.erro = True

    def _analisa_atrib_chprocedimento(self):
        simbolo = self.token_atual.lexema
        self._consumir("sidentificador")
        if not self.erro:
            if self.token_atual.simbolo == "satribuicao":
                self._consumir("satribuicao")
                self._analisa_atribuicao(simbolo)
            else:
                self._analisa_chamada_procedimento(simbolo)

    def _analisa_leia(self):
        self._consumir("sleia")
        self._consumir("sabre_parenteses")
        if not self.erro:
            if self.token_atual and self.token_atual.simbolo == "sidentificador":
                try:
                    simbolo = self.tabela.buscar_simbolo(self.token_atual.lexema)
                except ValueError as e:
                    print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
                    self.erro = True
                    return
                # Emissão: RD ; STR endereco
                self.codegen.rd()
                self.codegen.str_(simbolo['memoria'])
                self._consumir("sidentificador")
                if not self.erro:
                    self._consumir("sfecha_parenteses")

    def _analisa_escreva(self):
        self._consumir("sescreva")
        self._consumir("sabre_parenteses")
        if not self.erro:
            if self.token_atual and self.token_atual.simbolo == "sidentificador":
                try:
                    simbolo = self.tabela.buscar_simbolo(self.token_atual.lexema)
                except ValueError as e:
                    print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
                    self.erro = True
                    return
                # Emissão: LDV endereco ; PRN
                self.codegen.ldv(simbolo['memoria'])
                self.codegen.prn()
                self._consumir("sidentificador")
                if not self.erro:
                    self._consumir("sfecha_parenteses")

    # AQUI DEVE TER CÓDIGO DE GERAÇÃO DE RÓTULO
    def _analisa_enquanto(self):
        self._consumir("senquanto")
        start_label = self.codegen.new_label()
        end_label = self.codegen.new_label()
        # posição inicial do loop
        self.codegen.place_label(start_label)

        self._analisa_expressao()
        if not self.erro:
            # se expressão é falsa -> pular para end_label
            self.codegen.jmpf(end_label)
            self._consumir("sfaca")
            if not self.erro:
                self._analisa_comando_simples()
                # após corpo, voltar ao início
                self.codegen.jmp(start_label)
                # colocar label de fim
                self.codegen.place_label(end_label)

    def _analisa_se(self):
        self._consumir("sse")
        else_label = self.codegen.new_label()
        end_label = self.codegen.new_label()

        self._analisa_expressao()
        if not self.erro:
            # se falso -> pular para else_label
            self.codegen.jmpf(else_label)
            self._consumir("sentao")
            if not self.erro:
                self._analisa_comando_simples(sentao_ssenao=True)
                # quando terminar 'entao' pula para end (pulando else)
                self.codegen.jmp(end_label)
                # marca inicio do else
                self.codegen.place_label(else_label)

                if not self.erro and self.token_atual and self.token_atual.simbolo == "ssenao":
                    self._consumir("ssenao")
                    if not self.erro:
                        self._analisa_comando_simples(sentao_ssenao=True)

                # fim do if
                self.codegen.place_label(end_label)

    def _analisa_subrotinas(self):
        while self.token_atual and self.token_atual.simbolo in ["sprocedimento", "sfuncao"]:
            if self.token_atual.simbolo == "sprocedimento":
                self._consumir("sprocedimento")
                self._analisa_declaracao_procedimento()
            elif self.token_atual.simbolo == "sfuncao":
                self._consumir("sfuncao")
                self._analisa_declaracao_funcao()

    def _analisa_declaracao_procedimento(self):
        if self.token_atual.simbolo == "sidentificador":
            try:
                self.tabela.adicionar_simbolo(self.token_atual.lexema, tipo='procedimento')
            except ValueError as e:
                print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
                self.erro = True
            if not self.erro:
                self._consumir("sidentificador")
                if not self.erro:
                    self._consumir("sponto_virgula")
                    if not self.erro:
                        label_proc = self.codegen.new_label()
                        self.codegen.place_label(label_proc)
                        self.tabela.entrar_escopo()
                        self.analisar_bloco()

                        # desaloca variáveis locais do procedimento
                        num_vars = len(self.tabela.escopos[self.tabela.nivel_atual])
                        if num_vars > 0:
                            self.codegen.daloc(num_vars)

                        self.tabela.sair_escopo()

    def _analisa_declaracao_funcao(self):
        nome_funcao = self.token_atual.lexema
        tipo_retorno = None
        self._consumir("sidentificador")
        if not self.erro:
            self._consumir("sdoispontos")
            if not self.erro:
                if self.token_atual.simbolo in ["sinteiro", "sbooleano"]:
                    tipo_retorno = self.token_atual.lexema
                    self._consumir(self.token_atual.simbolo)
                    if not self.erro:
                        try:
                            self.tabela.adicionar_simbolo(nome_funcao, tipo=f'funcao {tipo_retorno}')
                        except ValueError as e:
                            print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
                            self.erro = True
                        if not self.erro:
                            self._consumir("sponto_virgula")
                            if not self.erro:
                                self.tabela.entrar_escopo()
                                self.analisar_bloco()
                                self.tabela.sair_escopo()
                else:
                    print(f"Erro sintático na linha {self.token_atual.linha}: Tipo de retorno esperado (inteiro ou booleano)")
                    self.erro = True

    def _analisa_expressao(self):
        # expressão possivelmente com operador relacional
        self._analisa_expressao_simples()
        while self.token_atual and self.token_atual.simbolo in ["smaior", "smaiorigual", "smenor", "smenorigual", "sigual", "sdif"]:
            op = self.token_atual.simbolo
            self._consumir(op)
            if not self.erro:
                self._analisa_expressao_simples()
                # conforme o operador, emite instrução de comparação adequada
                if op == "smaior":
                    self.codegen.cma()       # >
                elif op == "smenor":
                    self.codegen.cme()       # <
                elif op == "smaiorigual":
                    self.codegen.cmae()      # >=
                elif op == "smenorigual":
                    self.codegen.cmee()      # <=
                elif op == "sigual":
                    self.codegen.cmeq_eq()   # ==
                elif op == "sdif":
                    self.codegen.cmeq_eq()   # ==
                    self.codegen.not_()      # NOT para !=

    def _analisa_expressao_simples(self):
        # suporte para +/- unário
        sign = None
        if self.token_atual and self.token_atual.simbolo in ["smais", "smenos"]:
            sign = self.token_atual.simbolo
            self._consumir(self.token_atual.simbolo)

        self._analisa_termo()

        # se tinha sinal unário negativo, multiplicar por -1 (LDC -1; MULT)
        if sign == "smenos":
            self.codegen.ldc(-1)
            self.codegen.mult()

        while self.token_atual and self.token_atual.simbolo in ["smais", "smenos", "sou", "se"]:
            op = self.token_atual.simbolo
            self._consumir(op)
            if not self.erro:
                self._analisa_termo()
                if op == "smais":
                    self.codegen.add()
                elif op == "smenos":
                    self.codegen.sub()
                elif op == "sou":
                    self.codegen.or_()
                elif op == "se":
                    self.codegen.and_()

    def _analisa_termo(self):
        self._analisa_fator()
        while self.token_atual and self.token_atual.simbolo in ["smult", "sdiv", "se", "sou"]:
            op = self.token_atual.simbolo
            self._consumir(op)
            if not self.erro:
                # analisa o próximo fator (o resultado ficará na pilha) e então emite a operação
                self._analisa_fator()
                if op == "smult":
                    self.codegen.mult()
                elif op == "sdiv":
                    self.codegen.div()
                elif op == "se":  # 'e' (and)
                    self.codegen.and_()
                elif op == "sou":  # 'ou'
                    self.codegen.or_()

    def _analisa_fator(self):
        # fator -> identificador | numero | verdadeiro/falso | (expressao) | nao fator
        if self.token_atual.simbolo == "sidentificador":
            try:
                simbolo = self.tabela.buscar_simbolo(self.token_atual.lexema)
            except ValueError as e:
                print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
                self.erro = True
                return
            # Emite carregamento do valor da variável (LDV endereco)
            self.codegen.ldv(simbolo['memoria'])
            self._consumir("sidentificador")
            if not self.erro and simbolo['tipo'] in ['funcao inteiro', 'funcao booleano']:
                self._analisa_chamada_funcao()

        elif self.token_atual.simbolo == "snumero":
            valor = self.token_atual.lexema
            self.codegen.ldc(valor)
            self._consumir("snumero")

        elif self.token_atual.simbolo in ["sverdadeiro", "sfalso"]:
            val = 1 if self.token_atual.simbolo == "sverdadeiro" else 0
            self.codegen.ldc(val)
            self._consumir(self.token_atual.simbolo)

        elif self.token_atual.simbolo == "sabre_parenteses":
            self._consumir("sabre_parenteses")
            if not self.erro:
                self._analisa_expressao()
                if not self.erro:
                    self._consumir("sfecha_parenteses")

        elif self.token_atual.simbolo == "snao":
            # 'nao' é unário: gera código do fator e aplica NOT
            self._consumir("snao")
            if not self.erro:
                self._analisa_fator()
                self.codegen.not_()
        else:
            print(f"Erro Sintático na linha {self.token_atual.linha}: Fator inválido ou inesperado '{self.token_atual.lexema}'.")
            self.erro = True

    def _analisa_atribuicao(self, simbolo):
        # verifica semantica primeiro
        try:
            entrada = self.tabela.buscar_simbolo(simbolo)
        except ValueError as e:
            print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
            self.erro = True
            return

        # Analisa a expressão do lado direito — isso vai gerar o valor na pilha
        self._analisa_expressao()
        if not self.erro:
            # após gerar valor, armazena na variavel (endereco conhecido)
            self.codegen.str_(entrada['memoria'])

    def _analisa_chamada_procedimento(self, simbolo):
        try:
            self.tabela.buscar_simbolo(simbolo)
        except ValueError as e:
            print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
            self.erro = True

    def _analisa_chamada_funcao(self):
        self._consumir("sabre_parenteses")
        if not self.erro:
            self._consumir("sfecha_parenteses")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Erro: Modo de uso incorreto.")
        print("Uso: python analisador_sintatico.py <caminho_para_o_arquivo.txt>")
        sys.exit(1)

    caminho_arquivo = sys.argv[1]

    nome_base, extensao = os.path.splitext(caminho_arquivo)

    if extensao != '.txt':
        print(f"Erro: O arquivo '{caminho_arquivo}' não é válido.")
        print("Por favor, forneça um arquivo .txt")
        sys.exit(1)

    try:
        analisador = AnalisadorSintatico(caminho_arquivo)
        analisador.analisar()
    except Exception as e:
        print(f"Ocorreu um erro fatal durante a análise: {e}")