import sys
import os
from analisador_lexical import AnalisadorLexical, Token
from tabela_simbolos import TabelaSimbolos
from code_generator import GeradorCodigoMVD # <<< IMPORTADO

class AnalisadorSintatico:
    def __init__(self, arquivo_entrada):
        self.lexador = AnalisadorLexical(arquivo_entrada)
        self.token_atual = None
        self.erro = False
        self.tabela = TabelaSimbolos()
        self.gerador = GeradorCodigoMVD() # <<< INSTANCIADO
        self.dealloc_stack = [] # <<< Pilha para DALLOCs

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

            if self.token_atual:
                # Opcional: Descomente para depurar
                # print(self.token_atual.lexema) 
                pass
        else:
            print(f"Erro sintático: Esperado '{self.keywords[simbolo_esperado]}', mas encontrado 'EOF'")
    
    def analisar(self):
        self.token_atual = self.lexador.proximo_token()
        self._analisar_programa()
        self.lexador.fechar()

    def _analisar_programa(self): 
        """Analisa a estrutura principal do programa."""     
        self.gerador.gera("START") # <<< GERAÇÃO
        self._consumir("sprograma")
        if not self.erro:
            self.tabela.adicionar_simbolo(self.token_atual.lexema, tipo='programa')
            self._consumir("sidentificador")
            if not self.erro:
                self._consumir("sponto_virgula")
                if not self.erro:
                    self.analisar_bloco(final=True)
                    if not self.erro:
                        # Desaloca variáveis globais na ordem inversa
                        while self.dealloc_stack:
                            self.gerador.gera("DALLOC", self.dealloc_stack.pop())
                        self.gerador.gera("HLT") # <<< GERAÇÃO
        
    def analisar_bloco(self, final=False):
        """Analisa o bloco de declarações e comandos."""
        self._analisa_et_variaveis()
        if not self.erro:
            self._analisa_subrotinas()
            if not self.erro:
                self._analisa_comandos(final=final)

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

        # <<< GERAÇÃO
        num_vars = len(variaveis_para_declarar)
        if num_vars > 0:
            # O PDF (pág 71) gera um ALLOC por linha de 'var'
            self.gerador.gera("ALLOC", num_vars) 
            self.dealloc_stack.append(num_vars) # Empilha para DALLOC no fim
        # FIM GERAÇÃO >>>

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
            if not self.erro and self.token_atual.simbolo == "sidentificador":
                simbolo_obj = None
                try:
                    simbolo_obj = self.tabela.buscar_simbolo(self.token_atual.lexema)
                except ValueError as e:
                    print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
                    self.erro = True
                
                if not self.erro:
                    self.gerador.gera("RD") # <<< GERAÇÃO
                    self.gerador.gera("STR", simbolo_obj['memoria']) # <<< GERAÇÃO
                    self._consumir("sidentificador")
                    if not self.erro:
                        self._consumir("sfecha_parenteses")

    def _analisa_escreva(self):
        self._consumir("sescreva")
        self._consumir("sabre_parenteses")
        if not self.erro:
            if not self.erro:
                simbolo_obj = None
                try:
                    simbolo_obj = self.tabela.buscar_simbolo(self.token_atual.lexema)
                except ValueError as e:
                    print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
                    self.erro = True

                if not self.erro:
                    self.gerador.gera("LDV", simbolo_obj['memoria']) # <<< GERAÇÃO
                    self.gerador.gera("PRN") # <<< GERAÇÃO
                
                self._consumir("sidentificador")
                if not self.erro:
                    self._consumir("sfecha_parenteses")
    
    def _analisa_enquanto(self): 
        # [cite_start]Segue o padrão da pág 67 [cite: 2264-2276]
        
        rotulo_inicio = self.gerador.novo_rotulo()
        self.gerador.gera_rotulo(rotulo_inicio) # <<< GERAÇÃO
        
        self._consumir("senquanto")
        self._analisa_expressao()
        
        if not self.erro:
            rotulo_fim = self.gerador.novo_rotulo()
            self.gerador.gera("JMPF", rotulo_fim) # <<< GERAÇÃO

            self._consumir("sfaca")
            if not self.erro:
                self._analisa_comando_simples()
                self.gerador.gera("JMP", rotulo_inicio) # <<< GERAÇÃO
                self.gerador.gera_rotulo(rotulo_fim) # <<< GERAÇÃO

    def _analisa_se(self):
        # [cite_start]Segue o padrão da pág 67 [cite: 2235-2262]
        self._consumir("sse")
        self._analisa_expressao()
        
        if not self.erro:
            rotulo_falso = self.gerador.novo_rotulo()
            self.gerador.gera("JMPF", rotulo_falso) # <<< GERAÇÃO

            self._consumir("sentao")
            if not self.erro:
                self._analisa_comando_simples(sentao_ssenao=True)
                
                if not self.erro and self.token_atual and self.token_atual.simbolo == "ssenao":
                    rotulo_fim_se = self.gerador.novo_rotulo()
                    self.gerador.gera("JMP", rotulo_fim_se) # <<< GERAÇÃO
                    self.gerador.gera_rotulo(rotulo_falso) # <<< GERAÇÃO
                    
                    self._consumir("ssenao")
                    if not self.erro:
                        self._analisa_comando_simples(sentao_ssenao=True)
                        self.gerador.gera_rotulo(rotulo_fim_se) # <<< GERAÇÃO
                else:
                    # 'se' sem 'senao'
                    self.gerador.gera_rotulo(rotulo_falso) # <<< GERAÇÃO

    def _analisa_subrotinas(self):
        # [cite_start]Segue Algoritmo Analisa_Subrotinas [cite: 1594-1619]
        flag = 0
        auxrot = None
        if self.token_atual and self.token_atual.simbolo in ["sprocedimento", "sfuncao"]:
            auxrot = self.gerador.novo_rotulo()
            self.gerador.gera("JMP", auxrot) # <<< GERAÇÃO (Pula a definição das subrotinas)
            flag = 1

        while self.token_atual and self.token_atual.simbolo in ["sprocedimento", "sfuncao"]:
            if self.token_atual.simbolo == "sprocedimento":
                self._consumir("sprocedimento")
                self._analisa_declaracao_procedimento()
            elif self.token_atual.simbolo == "sfuncao":
                self._consumir("sfuncao")
                self._analisa_declaracao_funcao()

        if flag == 1:
            self.gerador.gera_rotulo(auxrot) # <<< GERAÇÃO (Ponto de início do código principal)

    def _analisa_declaracao_procedimento(self):
        if self.token_atual.simbolo == "sidentificador":
            nome_proc = self.token_atual.lexema
            rotulo_proc = self.gerador.novo_rotulo()
            
            try:
                # Adiciona à tabela com seu rótulo
                self.tabela.adicionar_simbolo(nome_proc, tipo='procedimento', rotulo=rotulo_proc)
            except ValueError as e:
                print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
                self.erro = True
            
            if not self.erro:
                self.gerador.gera_rotulo(rotulo_proc) # <<< GERAÇÃO (Define o início do proc)
                self._consumir("sidentificador")
                
                if not self.erro:
                    self._consumir("sponto_virgula")
                    if not self.erro:
                        self.tabela.entrar_escopo()
                        self.analisar_bloco()
                        vars_locais = self.tabela.sair_escopo()
                        # self.gerador.gera("DALLOC", vars_locais) # Desalocação de locais
                        self.gerador.gera("RETURN") # <<< GERAÇÃO

    def _analisa_declaracao_funcao(self):
        nome_funcao = self.token_atual.lexema
        tipo_retorno = None
        rotulo_func = self.gerador.novo_rotulo()
        
        self._consumir("sidentificador")
        if not self.erro:
            self._consumir("sdoispontos")
            if not self.erro:
                if self.token_atual.simbolo in ["sinteiro", "sbooleano"]:
                    tipo_retorno = self.token_atual.lexema
                    tipo_completo = f'funcao {tipo_retorno}'
                    self._consumir(self.token_atual.simbolo)
                    
                    if not self.erro:
                        try:
                            self.tabela.adicionar_simbolo(nome_funcao, tipo=tipo_completo, rotulo=rotulo_func)
                        except ValueError as e:
                            print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
                            self.erro = True
                        
                        if not self.erro:
                            self.gerador.gera_rotulo(rotulo_func) # <<< GERAÇÃO
                            self._consumir("sponto_virgula")
                            if not self.erro:
                                self.tabela.entrar_escopo()
                                self.analisar_bloco()
                                vars_locais = self.tabela.sair_escopo()
                                # self.gerador.gera("DALLOC", vars_locais)
                                self.gerador.gera("RETURN") # <<< GERAÇÃO
                else:
                    print(f"Erro sintático na linha {self.token_atual.linha}: Tipo de retorno esperado (inteiro ou booleano)")
                    self.erro = True
    
    def _analisa_expressao(self):
        self._analisa_expressao_simples()
        
        op_map = {
            "smaior": "CMA",
            "smaiorigual": "CMAQ",
            "smenor": "CME",
            "smenorigual": "CMEQ",
            "sigual": "CEQ",
            "sdif": "CDIF"
        }
        
        while self.token_atual and self.token_atual.simbolo in op_map:
            op_simbolo = self.token_atual.simbolo
            if not self.erro:
                self._consumir(op_simbolo)
                if not self.erro:
                    self._analisa_expressao_simples()
                    self.gerador.gera(op_map[op_simbolo]) # <<< GERAÇÃO
            else:
                break

    def _analisa_expressao_simples(self):
        sinal_unario = None
        if self.token_atual and self.token_atual.simbolo in ["smais", "smenos"]:
            if self.token_atual.simbolo == "smenos":
                sinal_unario = "smenos"
            self._consumir(self.token_atual.simbolo)
        
        if sinal_unario == "smenos":
             self.gerador.gera("LDC", 0) # Empilha 0 para fazer "0 - termo"

        self._analisa_termo()

        if sinal_unario == "smenos":
            self.gerador.gera("SUB") # <<< GERAÇÃO (Negação unária)

        op_map = {
            "smais": "ADD",
            "smenos": "SUB",
            "sou": "OR"
        }
        
        while self.token_atual and self.token_atual.simbolo in op_map:
            op_simbolo = self.token_atual.simbolo
            self._consumir(op_simbolo)
            if not self.erro:
                self._analisa_termo()
                self.gerador.gera(op_map[op_simbolo]) # <<< GERAÇÃO

    def _analisa_termo(self):
        self._analisa_fator()
        
        op_map = {
            "smult": "MULT",
            "sdiv": "DIVI",
            "se": "AND"
        }

        while self.token_atual and self.token_atual.simbolo in op_map:
            op_simbolo = self.token_atual.simbolo
            self._consumir(op_simbolo)
            if not self.erro:
                self._analisa_fator()
                self.gerador.gera(op_map[op_simbolo]) # <<< GERAÇÃO

    def _analisa_fator(self):
        if self.token_atual.simbolo == "sidentificador":
            simbolo = None
            try:
                simbolo = self.tabela.buscar_simbolo(self.token_atual.lexema)
            except ValueError as e:
                print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
                self.erro = True
            
            if not self.erro:    
                if simbolo['tipo'] in ['funcao inteiro', 'funcao booleano']:
                    self._consumir("sidentificador")
                    self._analisa_chamada_funcao(simbolo)
                else:
                    # É uma variável
                    self.gerador.gera("LDV", simbolo['memoria']) # <<< GERAÇÃO
                    self._consumir("sidentificador")

        elif self.token_atual.simbolo == "snumero":
            self.gerador.gera("LDC", self.token_atual.lexema) # <<< GERAÇÃO
            self._consumir("snumero")
        elif self.token_atual.simbolo == "sverdadeiro":
            self.gerador.gera("LDC", 1) # <<< GERAÇÃO
            self._consumir("sverdadeiro")
        elif self.token_atual.simbolo == "sfalso":
            self.gerador.gera("LDC", 0) # <<< GERAÇÃO
            self._consumir("sfalso")
        elif self.token_atual.simbolo == "sabre_parenteses":
            self._consumir("sabre_parenteses")
            if not self.erro:
                self._analisa_expressao()
                if not self.erro:
                    self._consumir("sfecha_parenteses")
        elif self.token_atual.simbolo == "snao":
            self._consumir("snao")
            if not self.erro:
                self._analisa_fator()
                self.gerador.gera("NEG") # <<< GERAÇÃO
        else:
            print(f"Erro Sintático na linha {self.token_atual.linha}: Fator inválido ou inesperado '{self.token_atual.lexema}'.")
            self.erro = True

    def _analisa_atribuicao(self, simbolo):
        simbolo_obj = None
        try:
            simbolo_obj = self.tabela.buscar_simbolo(simbolo)
        except ValueError as e:
            print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
            self.erro = True
        
        if not self.erro:
            self._analisa_expressao()
            
            if simbolo_obj['tipo'] in ['inteiro', 'booleano']:
                self.gerador.gera("STR", simbolo_obj['memoria']) # <<< GERAÇÃO
            elif simbolo_obj['tipo'] in ['funcao inteiro', 'funcao booleano']:
                 # A sintaxe LPD define "NomedaFunção := ValordeRetorno"
                 # O valor da expressão já está no topo da pilha.
                 # A geração de código para isso precisaria de um endereço
                 # de retorno, o que não foi totalmente especificado no PDF.
                 # Por simplicidade, assumimos que o valor fica na pilha
                 # e o 'RETURN' no final da função cuidará disso.
                 pass
            

    def _analisa_chamada_procedimento(self, simbolo):
        simbolo_obj = None
        try:
            simbolo_obj = self.tabela.buscar_simbolo(simbolo)
        except ValueError as e:
            print(f"Erro Semântico na linha {self.token_atual.linha}: {e}")
            self.erro = True
        
        if not self.erro and simbolo_obj['tipo'] == 'procedimento':
            self.gerador.gera("CALL", simbolo_obj['rotulo']) # <<< GERAÇÃO
        elif not self.erro:
             print(f"Erro Semântico na linha {self.token_atual.linha}: '{simbolo}' não é um procedimento.")
             self.erro = True

    def _analisa_chamada_funcao(self, simbolo_obj):
        self._consumir("sabre_parenteses")
        if not self.erro:
            # Lógica para argumentos iria aqui, mas LPD não tem
            self._consumir("sfecha_parenteses")
            if not self.erro:
                self.gerador.gera("CALL", simbolo_obj['rotulo']) # <<< GERAÇÃO


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Erro: Modo de uso incorreto.")
        print("Uso: python analisador_sintatico.py <caminho_para_o_arquivo.jovane>")
        sys.exit(1) 

    caminho_arquivo = sys.argv[1]
    
    nome_base, extensao = os.path.splitext(caminho_arquivo)

    if extensao != '.jovane':
        print(f"Erro: O arquivo '{caminho_arquivo}' não é válido.")
        print("Por favor, forneça um arquivo .jovane")
        sys.exit(1)
    
    try:
        analisador = AnalisadorSintatico(caminho_arquivo)
        analisador.analisar()

        # <<< BLOCO MODIFICADO
        if not analisador.erro:
            arquivo_saida = nome_base + ".mvd"
            analisador.gerador.escrever_arquivo(arquivo_saida)
            print(f"Compilação bem-sucedida.")
            print(f"Código MVD gerado em: {arquivo_saida}")
        else:
            # Os erros já foram impressos durante a análise
            pass 
        # FIM BLOCO MODIFICADO >>>

    except Exception as e:
        print(f"Ocorreu um erro fatal durante a análise: {e}")