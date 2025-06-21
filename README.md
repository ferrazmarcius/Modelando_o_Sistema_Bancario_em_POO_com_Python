# Sistema Bancário Orientado a Objetos em Python

Este projeto é uma evolução de um sistema bancário simples, refatorado para aplicar e demonstrar os princípios da **Programação Orientada a Objetos (POO)** em Python. Ele foi desenvolvido seguindo um diagrama de classes UML para estruturar as entidades do domínio bancário.

##  UML do Projeto

A arquitetura do sistema é baseada no seguinte diagrama de classes UML, que guiou a criação das entidades e suas relações:

![Diagrama UML do Sistema Bancário](https://raw.githubusercontent.com/ferrazmarcius/Modelando_o_Sistema_Bancario_em_POO_com_Python/main/assets/diagrama_uml_banco.png)

## Funcionalidades Atuais

As principais funcionalidades do sistema, agora estruturadas em classes, incluem:

* **Clientes e Pessoas Físicas:** Gerenciamento de clientes, com `PessoaFisica` herdando características básicas de um `Cliente`.
* **Contas Bancárias:** Criação e gestão de `Contas`, com especialização para `ContaCorrente`, que aplica limites de saque e número máximo de operações.
* **Transações:** Modelagem de operações como `Depósito` e `Saque` como transações que interagem com as contas.
* **Histórico de Transações:** Cada conta possui um histórico detalhado de todas as suas movimentações.

## Conceitos de POO Aplicados

Este projeto é uma demonstração prática dos seguintes conceitos de POO em Python:

* **Classes e Objetos:** Definição de classes como `Cliente`, `PessoaFisica`, `Conta`, `ContaCorrente`, `Historico`, `Transacao`, `Deposito` e `Saque` para representar entidades do mundo real.
* **Herança:** `PessoaFisica` herda de `Cliente`, e `ContaCorrente` herda de `Conta`, promovendo a reutilização de código e a especialização.
* **Polimorfismo:** As transações (`Deposito`, `Saque`) são tipos de `Transacao` (interface/classe abstrata), permitindo que sejam tratadas de forma uniforme.
* **Encapsulamento:** Utilização de propriedades (`@property`) para controlar o acesso aos atributos internos das classes (`_saldo`, `_numero`, etc.), garantindo a integridade dos dados.
* **Abstração:** Definição de uma interface (`Transacao`) com métodos abstratos (`registrar`) que devem ser implementados pelas subclasses.

## 🧑‍💻 Desenvolvedor

* **Marcius Silva Ferraz Filho**
* **Meu LinkedIn:** [linkedin.com/in/marcius-ferraz](https://www.linkedin.com/in/marcius-ferraz)
* **Meu usuário na DIO:** [dio.me/users/mferraz_xml](https://www.dio.me/users/mferraz_xml)

---

**Nota:** Este projeto foi desenvolvido como parte de um desafio de Python no bootcamp da DIO, em parceria com a Santander Open Academy, focado na aplicação de conceitos de Programação Orientada a Objetos e modelagem UML.
