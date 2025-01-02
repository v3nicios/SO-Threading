import threading
import random
import logging

# Configuração do log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# A classe ContaBancaria representa uma conta bancária individual com saldo e mecanismos de controle de acesso.
class ContaBancaria:
    def __init__(self, id_conta, saldo_inicial):
        self.id_conta = id_conta
        self.saldo = saldo_inicial
        self.lock = threading.Lock()

    def __repr__(self):
        return f"Conta {self.id_conta} - Saldo: {self.saldo}"

class Banco:
    def __init__(self):
        self.contas = []

    def criar_conta(self, id_conta, saldo_inicial):
        conta = ContaBancaria(id_conta, saldo_inicial)
        self.contas.append(conta)

    def transferir(self, conta_origem, conta_destino, valor):
        # Ordenar os locks para evitar deadlock
        contas = sorted([conta_origem, conta_destino], key=lambda c: c.id_conta)

        with contas[0].lock:
            with contas[1].lock:
                if conta_origem.saldo >= valor:
                    conta_origem.saldo -= valor
                    conta_destino.saldo += valor
                    logging.info(f"Transferido {valor} de Conta {conta_origem.id_conta} para Conta {conta_destino.id_conta}")
                    logging.info(f"Saldo final: {conta_origem} | {conta_destino}")
                else:
                    logging.info(f"Falha na transferência: saldo insuficiente na Conta {conta_origem.id_conta}")

    def saldo_total(self):
        return sum(conta.saldo for conta in self.contas)

def operacao_aleatoria(banco, num_operacoes):
    for _ in range(num_operacoes):
        origem = random.choice(banco.contas)
        destino = random.choice(banco.contas)
        while destino == origem:
            destino = random.choice(banco.contas)
        valor = random.randint(1, 100)
        banco.transferir(origem, destino, valor)

# Configuração inicial
def main():
    banco = Banco()

    # Criando contas com saldos iniciais aleatórios
    for i in range(1, 6):  # Exemplo: 5 contas
        banco.criar_conta(i, random.randint(100, 1000))

    logging.info("Estado inicial das contas:")
    for conta in banco.contas:
        logging.info(conta)

    # Criando threads para transferências simultâneas
    threads = []
    for _ in range(10):  # Exemplo: 10 threads
        thread = threading.Thread(target=operacao_aleatoria, args=(banco, 10))  # Cada thread faz 10 transferências
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    logging.info("Estado final das contas:")
    for conta in banco.contas:
        logging.info(conta)

    logging.info(f"Saldo total final: {banco.saldo_total()}")

if __name__ == "__main__":
    main()
