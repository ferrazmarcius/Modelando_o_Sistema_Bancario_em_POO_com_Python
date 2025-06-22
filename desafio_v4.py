import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime, date # Importar 'date' para comparar apenas a data


# ============ Decorador de Log (Corrigido para @functools.wraps e mensagem) ============
import functools

def log_transacao(func):
    """
    Decorador para registrar a data, hora e nome da função executada.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Captura o horário ANTES da execução da função
        data_hora = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print(f"[{data_hora}] Função '{func.__name__}' executada.")
        resultado = func(*args, **kwargs) # Executa a função original
        return resultado
    return wrapper


# ============ Iterador Personalizado (Ajustado para o que já estava funcionando) ============
class ContasIterador: # Renomeei de ContaIterador para ContasIterador como no seu código
    def __init__(self, contas):
        self.contas = contas
        self._index = 0

    def __iter__(self):
        self._index = 0 # Reinicia o índice a cada nova iteração
        return self

    def __next__(self):
        try:
            conta = self.contas[self._index]
            self._index += 1 # Incrementa ANTES de retornar para próxima chamada
            return f"""\
            Agência:\t{conta.agencia}
            Número:\t\t{conta.numero}
            Titular:\t{conta.cliente.nome}
            Saldo:\t\tR$ {conta.saldo:.2f}
        """
        except IndexError:
            raise StopIteration


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
        # self.indice_conta = 0 # Este atributo não é utilizado aqui diretamente para o desafio

    def realizar_transacao(self, conta, transacao):
        # TODO: validar o número de transações e invalidar a operação se for necessário
        # IMPLEMENTAÇÃO DO LIMITE DE TRANSAÇÕES DIÁRIAS
        
        # Obter o número de transações da conta para o dia atual
        # A nova implementação de Historico.transacoes_do_dia será usada aqui
        transacoes_hoje = list(conta.historico.transacoes_do_dia()) # Converte gerador para lista para contar
        
        # Definir um limite padrão para transações diárias (pode ser uma constante em ContaCorrente, por exemplo)
        LIMITE_TRANSACOES_DIARIAS = 10 # Limite de 10 transações diárias, conforme o desafio
        
        if len(transacoes_hoje) >= LIMITE_TRANSACOES_DIARIAS:
            print(f"\n@@@ Você excedeu o número de {LIMITE_TRANSACOES_DIARIAS} transações permitidas para hoje! @@@")
            return False # Impede a transação
        
        sucesso = transacao.registrar(conta) # transacao.registrar agora retorna True/False
        
        if sucesso:
            # O histórico é atualizado DENTRO do registrar das classes Saque/Deposito
            return True
        return False


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
        self._historico = Historico()

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
        elif valor <= 0: # Validação de valor inválido
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
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False
        return True


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

    # NOTA: O método nova_conta da ContaCorrente não precisa mais de todos os argumentos
    # se os limites forem fixos no construtor.
    # Se você quiser que o limite e limite_saques sejam definidos na criação,
    # remova o valor padrão do construtor e use eles no nova_conta.
    # Por agora, mantenho o seu nova_conta como estava.
    @classmethod
    def nova_conta(cls, cliente, numero, limite, limite_saques):
        return cls(numero, cliente, limite, limite_saques)


    def sacar(self, valor):
        # Validação de saque múltiplo de R$ 5,00 (cédulas)
        if valor % 5 != 0:
            print("\n@@@ Operação falhou! O valor do saque deve ser múltiplo de R$ 5,00. @@@")
            return False

        numero_saques_diarios = len(
            [transacao for transacao in self.historico.transacoes_do_dia() if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite_valor = valor > self.limite # Limite por transacao
        excedeu_saques = numero_saques_diarios >= self.limite_saques # Limite de saques diários

        if excedeu_limite_valor:
            print(f"\n@@@ Operação falhou! O valor do saque excede o limite de R$ {self.limite:.2f}. @@@")
        elif excedeu_saques:
            print(f"\n@@@ Operação falhou! Número máximo de saques diários ({self.limite_saques}) excedido. @@@")
        else:
            # Chama o sacar da classe pai (Conta). Se super().sacar(valor) for True, então o saque foi bem-sucedido.
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
            CPF do Titular:\t{self.cliente.cpf}
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"), # Corrigido para %S
            }
        )

    def gerar_relatorio(self, tipo_transacao=None):
        for transacao in self._transacoes:
            if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
                yield transacao

    # TODO: filtrar todas as transações realizadas no dia
    def transacoes_do_dia(self):
        """
        Retorna um gerador com todas as transações realizadas no dia atual.
        """
        hoje = date.today() # Pega apenas a data atual
        for transacao in self._transacoes:
            # Converte a string de data da transação de volta para um objeto date para comparação
            data_transacao_str = transacao["data"].split(" ")[0] # Pega apenas a parte da data "DD-MM-AAAA"
            data_transacao_obj = datetime.strptime(data_transacao_str, "%d-%m-%Y").date()
            
            if data_transacao_obj == hoje:
                yield transacao


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
        # Retorna o resultado do sacar para que Cliente.realizar_transacao possa validá-lo
        sucesso_transacao = conta.sacar(self.valor) 

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
        return sucesso_transacao # Retorna True/False


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        # Retorna o resultado do depositar para que Cliente.realizar_transacao possa validá-lo
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
        return sucesso_transacao # Retorna True/False


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

    if len(cliente.contas) == 1:
        return cliente.contas[0]
    
    print("\nContas do Cliente:")
    for i, conta in enumerate(cliente.contas):
        print(f"  {i+1}. Agência: {conta.agencia}, C/C: {conta.numero}, Saldo: R$ {conta.saldo:.2f}")
    
    while True:
        try:
            indice_conta_str = input("Informe o número da conta desejada (ou 0 para cancelar): ")
            if not indice_conta_str.isdigit():
                raise ValueError
            
            indice_conta = int(indice_conta_str) - 1
            
            if indice_conta == -1:
                print("\nOperação cancelada.")
                return None
            if 0 <= indice_conta < len(cliente.contas):
                return cliente.contas[indice_conta]
            else:
                print("@@@ Índice de conta inválido. Tente novamente. @@@")
        except ValueError:
            print("@@@ Entrada inválida. Por favor, digite um número válido. @@@")


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

    # A validação do limite diário acontece aqui, em Cliente.realizar_transacao
    cliente.realizar_transacao(conta, transacao)


@log_transacao
def sacar(clientes):
    cpf = input("Informe o CPF do CPF: ") # Corrigi para "CPF do cliente"
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    # A validação do limite diário acontece aqui, em Cliente.realizar_transacao
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
    # Usando o gerador para iterar sobre as transações (incluindo data e hora)
    # Podemos usar gerar_relatorio para ver todas ou transacoes_do_dia para as do dia
    
    # Para mostrar a data e hora de TODAS as transações no extrato:
    extrato_str = ""
    tem_transacao = False
    
    for transacao in conta.historico.gerar_relatorio(): # Usa o gerador sem filtro
        tem_transacao = True
        extrato_str += (
            f"\n{transacao['tipo']}:\n"
            f"\tR$ {transacao['valor']:.2f}\n"
            f"\tData: {transacao['data']}" # Adiciona a data/hora aqui
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

    # Verificar se o cliente já possui uma conta com esse número
    # No seu código, numero_conta é gerado automaticamente (len(contas) + 1),
    # então a chance de duplicidade para o mesmo cliente é baixa se ele sempre
    # criar contas novas, mas pode ser útil se o número_conta fosse manual.
    # Por simplicidade e para o desafio, manteremos o número automático.
    
    # NOTE: O valor padrão de limite de saques foi alterado para 50 saques
    # (Removi do nova_conta se você quiser usar os valores padrão do __init__)
    # Se você quiser passar os valores explícitos como 500 e 50, mantenha os argumentos:
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta, limite=500, limite_saques=3) # Usando limite_saques=3 para o desafio original (Saques Diários)
    
    # Adicionar a conta à lista de contas do cliente
    cliente.adicionar_conta(conta) # Use o método adicionar_conta do cliente
    contas.append(conta) # Adiciona à lista global de contas

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    if not contas:
        print("\n@@@ Nenhuma conta cadastrada ainda. @@@")
        return
        
    print("\n================ LISTA DE CONTAS ================")
    # Utilizando o iterador personalizado para listar as contas
    for conta_info in ContasIterador(contas):
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
            numero_conta = len(contas) + 1
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