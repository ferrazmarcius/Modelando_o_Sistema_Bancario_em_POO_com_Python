import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime
import functools # Importar para usar @functools.wraps no decorador


# ============ Decorador de Log ============
def log_transacao(func):
    """
    Decorador para registrar a data, hora e tipo de transação
    das funções decoradas.
    """
    @functools.wraps(func) # Ajuda a manter metadados da função original
    def wrapper(*args, **kwargs):
        resultado = func(*args, **kwargs) # Executa a função original
        data_hora = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print(f"[{data_hora}] Função '{func.__name__}' executada.")
        return resultado
    return wrapper


# ============ Iterador Personalizado ============
class ContaIterador:
    """
    Iterador personalizado para percorrer uma coleção de contas,
    retornando informações básicas de cada uma.
    """
    def __init__(self, contas):
        self._contas = contas
        self._index = 0

    def __iter__(self):
        # Retorna o próprio iterador (self)
        return self

    def __next__(self):
        # Verifica se ainda há contas para iterar
        try:
            conta = self._contas[self._index]
            self._index += 1
            # Retorna informações básicas da conta
            return f"Agência: {conta.agencia}, C/C: {conta.numero}, Saldo: R$ {conta.saldo:.2f}"
        except IndexError:
            # Levanta StopIteration quando não há mais elementos
            raise StopIteration


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        # Adiciona a data/hora da transação ao log ao registrar
        # O decorador log_transacao vai registrar a execução desta função (realizar_transacao)
        # mas também queremos o log da transação em si
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico() # Instância de Historico

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
        elif valor <= 0: # Validação de valor inválido adicionada aqui
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
        else:
            self._saldo -= valor
            print("\n=== Saque realizado com sucesso! ===")
            return True
        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n=== Depósito realizado com sucesso! ===")
            return True
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    # Adicionando propriedades para _limite e _limite_saques
    @property
    def limite(self):
        return self._limite

    @property
    def limite_saques(self):
        return self._limite_saques

    def sacar(self, valor):
        # Validação de saque múltiplo de R$ 5,00 (cédulas)
        if valor % 5 != 0:
            print("\n@@@ Operação falhou! O valor do saque deve ser múltiplo de R$ 5,00. @@@")
            return False

        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            print(f"\n@@@ Operação falhou! O valor do saque excede o limite de R$ {self.limite:.2f}. @@@")
        elif excedeu_saques:
            print(f"\n@@@ Operação falhou! Número máximo de saques ({self.limite_saques}) excedido. @@@")
        else:
            return super().sacar(valor) # Chama o sacar da classe pai (Conta)

        return False

    def __str__(self):
        return f"""\
            Agência:\t\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t\t{self.cliente.nome}
            CPF do Titular:\t{self.cliente.cpf}
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        # Correção da formatação de segundos para %S
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"), # Corrigido para %S
            }
        )
    
    # ============ Gerador de Relatórios ============
    def gerar_relatorio(self, tipo_transacao=None):
        """
        Gerador que itera sobre as transações e as retorna uma a uma.
        Pode filtrar por tipo de transação (ex: "Saque", "Deposito").
        """
        for transacao in self._transacoes:
            if tipo_transacao is None or transacao["tipo"] == tipo_transacao:
                yield transacao # 'yield' faz esta função um gerador


class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


# ============ Funções de Interface do Usuário ============

def menu():
    menu_texto = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu_texto))


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return None

    # Melhoria: Permitir que o cliente escolha qual conta operar
    if len(cliente.contas) == 1:
        return cliente.contas[0] # Retorna a única conta se houver apenas uma
    
    # Se tiver múltiplas contas, lista e pede para o usuário escolher
    print("\nContas do Cliente:")
    for i, conta in enumerate(cliente.contas):
        print(f"  {i+1}. Agência: {conta.agencia}, C/C: {conta.numero}, Saldo: R$ {conta.saldo:.2f}")
    
    while True:
        try:
            indice_conta = int(input("Informe o número da conta desejada (ou 0 para cancelar): ")) - 1
            if indice_conta == -1: # Usuário digitou 0 para cancelar
                print("\nOperação cancelada.")
                return None
            if 0 <= indice_conta < len(cliente.contas):
                return cliente.contas[indice_conta]
            else:
                print("@@@ Índice de conta inválido. Tente novamente. @@@")
        except ValueError:
            print("@@@ Entrada inválida. Por favor, digite um número. @@@")


@log_transacao
def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


@log_transacao
def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


@log_transacao
def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    # TODO: atualizar a implementação para utilizar o gerador definido em Historico
    # Usando o gerador para iterar sobre as transações
    transacoes_geradas = conta.historico.gerar_relatorio() 
    
    extrato_str = "" # Alterei o nome para evitar conflito com a variável interna do loop
    tem_transacao = False
    for transacao in transacoes_geradas:
        tem_transacao = True
        extrato_str += (
            f"\n{transacao['tipo']}:\n"
            f"\tR$ {transacao['valor']:.2f}\n"
            f"\tData: {transacao['data']}"
        )

    if not tem_transacao:
        extrato_str = "Não foram realizadas movimentações."
    
    print(extrato_str)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")


@log_transacao
def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente número): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")


@log_transacao
def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    
    # Verifica se o cliente já possui uma conta com o mesmo número
    if any(c.numero == conta.numero for c in cliente.contas):
        print("\n@@@ O cliente já possui uma conta com este número. @@@")
        return

    contas.append(conta)
    cliente.contas.append(conta) # Adiciona a conta à lista de contas do cliente

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    # TODO: alterar implementação, para utilizar a classe ContaIterador
    if not contas:
        print("\n@@@ Nenhuma conta cadastrada ainda. @@@")
        return
        
    print("\n================ LISTA DE CONTAS ================")
    # Utilizando o iterador personalizado para listar as contas
    for conta_info in ContaIterador(contas):
        print(textwrap.dedent(conta_info))
        print("-" * 50) # Separador
    print("==========================================")


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1 # Gerar número da conta automaticamente
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            print("\nSaindo do sistema. Obrigado por usar nosso banco!")
            break

        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")


if __name__ == "__main__":
    main()