# file to create code generation logic

class GeradorCodigoMVD:
    def __init__(self):
        self.codigo = []  # Lista de strings, cada uma é uma instrução MVD
        self.rotulo_atual = 0

    def novo_rotulo(self):
        """Cria e retorna um novo rótulo único (ex: L1, L2)."""
        self.rotulo_atual += 1
        return f"L{self.rotulo_atual}"

    def gera_rotulo(self, rotulo):
        """Adiciona um rótulo (ex: 'L1 NULL') ao código."""
        # A instrução NULL é usada como um "no-op" para ancorar um rótulo [cite: 2234]
        self.codigo.append(f"{rotulo} NULL")

    def gera(self, comando, param1=None, param2=None):
        """
        Adiciona uma instrução ao código.
        Ex: gera("LDC", 1) -> "LDC 1"
            gera("JMP", "L1") -> "JMP L1"
            gera("ALLOC", 0, 2) -> "ALLOC 0, 2"
        """
        if param1 is None and param2 is None:
            instrucao = f"    {comando}"
        elif param2 is None:
            instrucao = f"    {comando} {param1}"
        else:
            instrucao = f"    {comando} {param1}, {param2}"
        
        self.codigo.append(instrucao)

    def escrever_arquivo(self, nome_arquivo):
        """Escreve o código MVD gerado em um arquivo."""
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            for linha in self.codigo:
                f.write(linha + '\n')
