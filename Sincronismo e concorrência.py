import random
import logging
import time

# Configuração do log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class Semaforo:
    #Implementação simples de semáforo para controlar acesso
    def __init__(self):
        self.locked = False

    def acquire(self):
        while self.locked:
            time.sleep(0.01)  # Aguarda até que seja liberado
        self.locked = True

    def release(self):
        self.locked = False

class ContaBancaria:
   #Representa uma conta bancária com saldo 
    def __init__(self, id_conta, saldo_inicial):
        self.id_conta = id_conta
        self.saldo = saldo_inicial
        self.semaforo = Semaforo()

    def __repr__(self):
        return f"Conta {self.id_conta} - Saldo: {self.saldo}"

class Banco:
    #Gerencia contas e permite transferências seguras entre elas
    def __init__(self):
        self.contas = []
        self.log_transacoes = []  # Lista para armazenar logs das transações

    def criar_conta(self, id_conta, saldo_inicial):
        conta = ContaBancaria(id_conta, saldo_inicial)
        self.contas.append(conta)

    def transferir(self, conta_origem, conta_destino, valor):
        # Ordena as contas por ID para evitar deadlocks
        contas = sorted([conta_origem, conta_destino], key=lambda c: c.id_conta)

        # Adquire os locks na ordem dos IDs
        contas[0].semaforo.acquire()
        contas[1].semaforo.acquire()

        try:
            # Verifica saldo e realiza a transferência
            if conta_origem.saldo >= valor:
                conta_origem.saldo -= valor
                conta_destino.saldo += valor

                # Registra a transação no log
                mensagem = (
                    f"Transferido {valor} de Conta {conta_origem.id_conta} "
                    f"para Conta {conta_destino.id_conta}."
                    f" Saldos finais: {conta_origem} | {conta_destino}"
                )
                self.log_transacoes.append(mensagem)
                logging.info(mensagem)
            else:
                mensagem = (
                    f"Falha na transferência: saldo insuficiente na Conta {conta_origem.id_conta}. "
                    f"Saldo atual: {conta_origem.saldo}, Valor tentado: {valor}"
                )
                self.log_transacoes.append(mensagem)
                logging.info(mensagem)
        finally:
            # Controle os locks
            contas[1].semaforo.release()
            contas[0].semaforo.release()

    def saldo_total(self):
        #Calcula o saldo total de todas as contas
        return sum(conta.saldo for conta in self.contas)

def operacao_aleatoria(banco, num_operacoes):
    #Realiza transferências aleatórias entre contas
    for _ in range(num_operacoes):
        origem = random.choice(banco.contas)
        destino = random.choice(banco.contas)
        while destino == origem:
            destino = random.choice(banco.contas)
        valor = random.randint(1, 100)
        banco.transferir(origem, destino, valor)

def simulador_concorrente(banco, num_operacoes_por_trabalhador, num_trabalhadores):
    #Simula concorrência manualmente alternando entre trabalhadores
    trabalhadores = [
        lambda: operacao_aleatoria(banco, num_operacoes_por_trabalhador)
        for _ in range(num_trabalhadores)
    ]

    while trabalhadores:
        trabalhador = trabalhadores.pop(0)  # Obtém o próximo
        trabalhador()  

# Configuração inicial
def main():
    banco = Banco()

    # Criando contas com saldos iniciais aleatórios
    for i in range(1, 6):  
        banco.criar_conta(i, random.randint(100, 1000))

    logging.info("Estado inicial das contas:")
    for conta in banco.contas:
        logging.info(conta)
        
    logging.info(f"Saldo total inicial: {banco.saldo_total()}")

    # Simulando múltiplas operações concorrentes
    simulador_concorrente(banco, 100, 1)

    logging.info("Estado final das contas:")
    for conta in banco.contas:
        logging.info(conta)

    logging.info(f"Saldo total final: {banco.saldo_total()}")

    # Exibindo log das transações
    logging.info("Todos os LoGS")
    for log in banco.log_transacoes:
        logging.info(log)

if __name__ == "__main__":
    main()
