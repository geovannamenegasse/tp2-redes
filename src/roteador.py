import sys
import socket

from threading import Thread, Timer
from time import sleep

MY_IP = 'localhost'
INFINITY = 16
SEP = ':'

COMMAND_C = 'C'
COMMAND_D = 'D'
COMMAND_I = 'I'
COMMAND_F = 'F'
COMMAND_T = 'T'
COMMAND_E = 'E'

IDENTIFICADOR = sys.argv[1]
PORTO = sys.argv[2] 

tabela_vizinhos = []
tabela_roteamento = {IDENTIFICADOR : (IDENTIFICADOR, 0, IDENTIFICADOR)}

# print("Roteador " + identificador + " iniciado...")

sckt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sckt.bind((MY_IP, int(PORTO)))


def adiciona_vizinho(msg):
    nome, ip, port = msg[3], msg[1], msg[2]
    tabela_vizinhos.append((nome, ip, port))
    tabela_roteamento[nome] = (nome, 1, nome)

def remove_vizinho(msg):
    global tabela_vizinhos

    aux = []
    nome_vizinho = ''

    for vizinho in tabela_vizinhos:
        if vizinho[1] != msg[1] or vizinho[2] != msg[2]:
            aux.append(vizinho)
        else:
            nome_vizinho = vizinho[0]

    tabela_vizinhos = aux            

    if nome_vizinho in tabela_roteamento.keys():
        tabela_roteamento[nome_vizinho] = (tabela_roteamento[nome_vizinho][0], INFINITY, tabela_roteamento[nome_vizinho][2])
        new_msg = COMMAND_D + SEP + MY_IP + SEP + str(PORTO)
        sckt.sendto(new_msg.encode("latin-1"),(msg[1], int(msg[2])))
    
    for rota in tabela_roteamento.values():
        if nome_vizinho == rota[2]:
            tabela_roteamento[rota[0]] = (rota[0], INFINITY, tabela_roteamento[rota[0]][2])

def manda_anuncio():
    sleep(1)
    anuncio = monta_anuncio(tabela_roteamento, IDENTIFICADOR)
    for vizinho in tabela_vizinhos:
        if vizinho[0] != IDENTIFICADOR:
            sckt.sendto(anuncio.encode("latin-1"),(vizinho[1], int(vizinho[2])))

def monta_anuncio(tb_roteamento, nome_roteador):
    tabela_anuncio = []
    for rota in tb_roteamento.values():
        tabela_anuncio.append((rota[0], rota[1]))

    mensagem = '11111' + SEP + nome_roteador + SEP + str(len(tabela_anuncio))
    for (dest, cust) in tabela_anuncio:
        mensagem = mensagem + SEP + dest + SEP + str(cust)
    
    return mensagem

def encerra_execucao():
    exit(1)

def imprime_tabela():
    print(IDENTIFICADOR)
    for rota in tabela_roteamento.values():
        print(rota[0], end=" ")
        print(rota[1], end=" ")
        print(rota[2])
    print('\n')

def envia_mensagem(msg, nome_origem):
    mensagem = msg[1]
    nome_destino = msg[2]
    
    if len(msg) < 4:
        nome_origem = IDENTIFICADOR
    else:
        nome_origem = msg[3]

    if nome_destino not in tabela_roteamento.keys():
        print("X " +  mensagem + " de " + nome_origem + " para " + nome_destino)
        return

    nome_next = tabela_roteamento[nome_destino][2] 

    if nome_destino == IDENTIFICADOR:
        print("R " +  mensagem + " de " + nome_origem + " para " + nome_destino)
        return
    else:
        print("E " +  mensagem + " de " + nome_origem + " para " + nome_destino + " através de " + nome_next)
        
    ip_next = ''
    port_next = None

    for vizinho in tabela_vizinhos:
        if vizinho[0] == nome_next:
            ip_next = vizinho[1]
            port_next = vizinho[2]
            break

    if nome_origem != '':
        nome_origem = SEP + nome_origem

    new_msg = COMMAND_E + SEP + mensagem + SEP + nome_destino + nome_origem
    sckt.sendto(new_msg.encode("latin-1"),(ip_next, int(port_next)))

def recebe_anuncio(msg, emissor):
    achei = False
    for vizinho in tabela_vizinhos:
        if vizinho[0] == msg[1]:
            achei = True
    if achei == False and msg[1] != IDENTIFICADOR:
        if emissor[1][0] == '127.0.0.1':
            tabela_vizinhos.append((msg[1],'localhost',str(emissor[1][1])))
        else:
            tabela_vizinhos.append((msg[1],str(emissor[1][0]),str(emissor[1][1])))

    tabela_anuncio = []
    for i in range(3, len(msg), 2):
        tabela_anuncio.append((msg[i], msg[i+1]))

    distance_vector(tabela_anuncio, msg[1])

def distance_vector(tabela_anuncio, vizinho):
    for anuncio in tabela_anuncio:
        destino = anuncio[0]
        custo = anuncio[1]
        if destino not in tabela_roteamento.keys(): 
            tabela_roteamento[destino] = (destino, int(custo) + 1, vizinho)
        else:
            if int(custo) + 1 < tabela_roteamento[destino][1]:
                tabela_roteamento[destino] = (destino, int(custo) + 1, vizinho)
            else:
                if tabela_roteamento[destino][2] == vizinho:
                    tabela_roteamento[destino] = (destino, int(custo) + 1, tabela_roteamento[destino][2])


while True:
    t = Timer(1.0, manda_anuncio)
    t.start()

    emissor = sckt.recvfrom(50)
    msg = (emissor[0].decode("utf-8")).split(SEP)

    if msg[0] == COMMAND_C: 
        adiciona_vizinho(msg)

    elif msg[0] == COMMAND_D:
        remove_vizinho(msg)

    elif msg[0] == COMMAND_I:
        manda_anuncio()

    elif msg[0] == COMMAND_F:
        encerra_execucao()

    elif msg[0] == COMMAND_T:
        imprime_tabela()

    elif msg[0] == COMMAND_E:
        envia_mensagem(msg, '')

    else:
        recebe_anuncio(msg, emissor)
    
    t.cancel()
