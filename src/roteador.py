import sys
import socket
from threading import Thread, Timer
from time import sleep

identificador = sys.argv[1]
porto = sys.argv[2] 
vizinhos = []
tabela_roteamento = {identificador : (identificador, 0, identificador)}

print("Roteador " + identificador + " iniciado...")

sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sck.bind(('localhost', int(porto)))

def distance_vector(tabela_anuncio, vizinho):
    for anuncio in tabela_anuncio:
        destino = anuncio[0]
        custo = anuncio[1]
        if destino not in tabela_roteamento.keys(): # dar um jeito de chavear a tabela
            tabela_roteamento[destino] = (destino, int(custo) + 1, vizinho)
        else:
            if int(custo) + 1 < tabela_roteamento[destino][1]:
                tabela_roteamento[destino] = (destino, int(custo) + 1, vizinho)
            else:
                if tabela_roteamento[destino][2] == vizinho:
                    tabela_roteamento[destino] = (destino, int(custo) + 1, tabela_roteamento[destino][2])

def monta_anuncio(tb_roteamento, nome_roteador):
    tabela_anuncio = []
    for rota in tb_roteamento.values():
        tabela_anuncio.append((rota[0], rota[1]))
    # print("Montando anuncio do roteador " + identificador)
    # print(tabela_anuncio)

    mensagem = '11111' + ':' + nome_roteador + ':' + str(len(tabela_anuncio))
    for (dest, cust) in tabela_anuncio:
        mensagem = mensagem + ':' + dest + ':' + str(cust)
    
    # print(mensagem)
    return mensagem

def manda_anuncio():
    sleep(1)
    anuncio = monta_anuncio(tabela_roteamento, identificador)

    for vizinho in vizinhos:
        if vizinho[0] != identificador:
            # print("Enviando anuncio ao roteador " + vizinho[0])
            sck.sendto(anuncio.encode("latin-1"),(vizinho[1], int(vizinho[2])))

def imprime_tabela(identificador):
    print("Tabela de Roteamento de " + identificador)
    for rota in tabela_roteamento.values():
        print(rota)
    print('\n')

def adiciona_vizinho(msg):
    # print("Adicionando roteador aos vizinhos...")
    nome, ip, port = msg[3], msg[1], msg[2]
    vizinhos.append((nome, ip, port))
    tabela_roteamento[nome] = (nome, 1, nome)
    # print(vizinhos)

def remove_vizinho(msg):
    aux = []
    # print("Removendo roteador dos vizinhos...")
    for vizinho in vizinhos:
        if vizinho[1] != msg[1] or vizinho[2] != msg[2]:
            aux.append(vizinho)
    vizinhos = aux            
    # print(vizinhos)
    # atualizar rotas que tem proximo passo como esse vizinho para distancia 16


def encerra_execucao():
    # print("Finalizando execução do roteador " + identificador)
    exit(1)

def envia_mensagem(msg):
    # print(msg)
    mensagem = msg[1]
    ip = msg[2]
    port = msg[3]        
    sck.sendto(mensagem.encode("latin-1"),(ip, int(port)))

def recebe_anuncio(msg, recvd):
    # print(msg)
    
    achei = False
    for vizinho in vizinhos:
        if vizinho[0] == msg[1]:
            achei = True
    if achei == False and msg[1] != identificador:
        vizinhos.append((msg[1],str(recvd[1][0]),str(recvd[1][1])))

    tabela_anuncio = []
    for i in range(3, len(msg), 2):
        tabela_anuncio.append((msg[i], msg[i+1]))

    # print("Tabela anuncio vindo de " + msg[1])
    # print(tabela_anuncio)
    # print("\n")

    distance_vector(tabela_anuncio, msg[1])
    # imprime_tabela(identificador)


while True:
    t = Timer(1.0, manda_anuncio)
    t.start()

    recvd = sck.recvfrom(50)
    msg = (recvd[0].decode("utf-8")).split(':')

    if msg[0] == 'C': 
        adiciona_vizinho(msg)

    elif msg[0] == 'D':
        remove_vizinho(msg)

    elif msg[0] == 'I':
        manda_anuncio()

    elif msg[0] == 'F':
        encerra_execucao()

    elif msg[0] == 'T':
        imprime_tabela(identificador)

    elif msg[0] == 'E':
        envia_mensagem(msg)

    else:
        recebe_anuncio(msg, recvd)
    
    t.cancel()
