import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime, date
import functools # Necessário para @functools.wraps


# ============ Decorador de Log em Arquivo ============
def log_transacao(func):
    """
    Decorador para registrar informações detalhadas de cada chamada de função
    em um arquivo de log chamado 'log.txt'.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 1. Data e hora atuais
        data_hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 2. Nome da função
        nome_funcao = func.__name__
        
        # 3. Argumentos da função
        # Representa os argumentos posicionais e nomeados de forma legível
        args_str = ", ".join(map(repr, args))
        kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())
        
        if args_str and kwargs_str:
            argumentos_str = f"({args_str}, {kwargs_str})"
        elif args_str:
            argumentos_str = f"({args_str})"
        elif kwargs_str:
            argumentos_str = f"({kwargs_str})"
        else:
            argumentos_str = "()"

        # Executa a função original para obter o resultado
        try:
            resultado = func(*args, **kwargs)
            # 4. Valor retornado pela função (ou representação do resultado)
            valor_retornado = repr(resultado) # repr() para uma representação fiel
        except Exception as e:
            resultado = None # Em caso de erro, a função não retorna um valor normal
            valor_retornado = f"Exceção levantada: {type(e).__name__}: {e}"
            # Re-levantar a exceção para que o programa se comporte como esperado
            # raise # Se quiser que a exceção interrompa o fluxo após o log

        log_entry = (
            f"[{data_hora_atual}] Função: {nome_funcao}\n"
            f"  Args: {argumentos_str}\n"
            f"  Retorno: {valor_retornado}\n"
            f"----------------------------------------\n" # Separador para cada entrada
        )
        
        with open("log.txt", "a") as f: # 'a' para append (adicionar ao final)
            f.write(log_entry)
            
        return resultado
    return wrapper


# ============ Iterador Personalizado (ContasIterador) ============
class ContasIterador:
    def __init__(self, contas):
        self.contas = contas
        self._index = 0

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        try:
            conta = self.contas[self._index]
            self._index += 1
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

    def realizar_transacao(self, conta, transacao):
        # A validação do limite de transações diárias foi movida para ContaCorrente.sacar
        # para que o limite seja por CONTA, não por CLIENTE.
        # Se o limite de transações diárias for para o cliente (todas as contas dele),
        # esta lógica ficaria aqui. Por agora, mantém-se por conta.
        
        # O método registrar agora retorna True/False, então podemos verificar o sucesso.
        sucesso_registro = transacao.registrar(conta)
        if not sucesso_registro:
            # A mensagem de erro já é impressa dentro de sacar/depositar/validacao de limite
            return False
        return True


    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: ('{self.cpf}')>"


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
        elif valor <= 0:
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
        # Inclui um atributo para o limite de transações diárias, se o requisito for por CONTA
        self.limite_transacoes_diarias = 10 

    @property
    def limite(self):
        return self._limite

    @property
    def limite_saques(self):
        return self._limite_saques # Limite de saques diários, já existente

    @classmethod
    def nova_conta(cls, cliente, numero, limite, limite_saques):
        return cls(numero, cliente, limite, limite_saques)

    def sacar(self, valor):
        # Validação de saque múltiplo de R$ 5,00 (cédulas)
        if valor % 5 != 0:
            print("\n@@@ Operação falhou! O valor do saque deve ser múltiplo de R$ 5,00. @@@")
            return False

        # Validação de Limite de Transações Diárias por CONTA (MOVIDA PARA CÁ)
        transacoes_hoje = list(self.historico.transacoes_do_dia())
        if len(transacoes_hoje) >= self.limite_transacoes_diarias:
            print(f"\n@@@ Você excedeu o número de {self.limite_transacoes_diarias} transações permitidas para hoje nesta conta! @@@")
            return False


        numero_saques_diarios = len(
            [transacao for transacao in transacoes_hoje if transacao["tipo"] == Saque.__name__]
        )
        
        excedeu_limite_valor = valor > self.limite
        excedeu_saques = numero_saques_diarios >= self.limite_saques

        if excedeu_limite_valor:
            print(f"\n@@@ Operação falhou! O valor do saque excede o limite de R$ {self.limite:.2f}. @@@")
        elif excedeu_saques:
            print(f"\n@@@ Operação falhou! Número máximo de saques diários ({self.limite_saques}) excedido. @@@")
        else:
            # Chama o sacar da classe pai (Conta). Se super().sacar(valor) for True, então o saque foi bem-sucedido.
            return super().sacar(valor)

        return False

    def __repr__(self):
        return f"<{self.__class__.__name__}: ('{self.agencia}', '{self.numero}', '{self.cliente.nome}')>"

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
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

    def gerar_relatorio(self, tipo_transacao=None):
        for transacao in self._transacoes:
            if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
                yield transacao

    def transacoes_do_dia(self):
        """
        Retorna um gerador com todas as transações realizadas no dia atual.
        """
        hoje = datetime.now().date() # Pega apenas a data atual
        for transacao in self._transacoes:
            # Converte a string de data da transação de volta para um objeto date para comparação
            # Garante que a string de data tenha o formato esperado antes de fatiar
            try:
                data_transacao_obj = datetime.strptime(transacao["data"], "%d-%m-%Y %H:%M:%S").date()
                if data_transacao_obj == hoje:
                    yield transacao
            except ValueError:
                # Ignorar transações com formato de data inválido, ou logar o erro
                print(f"@@@ Erro ao converter data de transação para filtro diário: {transacao['data']} @@@")


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
        # A validação do limite diário foi movida para ContaCorrente.sacar
        sucesso_transacao = conta.sacar(self.valor) 

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
        return sucesso_transacao


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        # A validação do limite diário foi movida para ContaCorrente.depositar
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
        return sucesso_transacao


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
                raise ValueError("Entrada inválida.")
            
            indice_conta = int(indice_conta_str) - 1
            
            if indice_conta == -1:
                print("\nOperação cancelada.")
                return None
            if 0 <= indice_conta < len(cliente.contas):
                return cliente.contas[indice_conta]
            else:
                print("@@@ Índice de conta inválido. Tente novamente. @@@")
        except ValueError as e:
            print(f"@@@ Entrada inválida: {e}. Por favor, digite um número válido. @@@")


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

    # A validação de limite diário agora é feita dentro de ContaCorrente.depositar
    # ou ContaCorrente.sacar, e Cliente.realizar_transacao verifica o retorno.
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

    # A validação de limite diário agora é feita dentro de ContaCorrente.sacar
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
    extrato_str = "" # Usado para construir a string do extrato
    tem_transacao = False
    
    # Gerar relatório para exibir todas as transações, incluindo data e hora
    for transacao in conta.historico.gerar_relatorio():
        tem_transacao = True
        extrato_str += (
            f"\n{transacao['tipo']}:\n"
            f"\tR$ {transacao['valor']:.2f}\n"
            f"\tData: {transacao['data']}\n" # Adiciona a data/hora aqui
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

    # Adiciona a nova conta à lista de contas do cliente
    # e à lista global de contas
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta, limite=500, limite_saques=3) # Usando limite_saques=3 para o desafio (saques diários)
    
    cliente.adicionar_conta(conta) # Adiciona ao cliente
    contas.append(conta) # Adiciona à lista global

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    if not contas:
        print("\n@@@ Nenhuma conta cadastrada ainda. @@@")
        return
        
    print("\n================ LISTA DE CONTAS ================")
    # Utilizando o iterador personalizado para listar as contas
    # e o textwrap para formatar cada string retornada pelo iterador
    for conta_info in ContasIterador(contas):
        print(textwrap.dedent(conta_info))
        print("-" * 50)
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