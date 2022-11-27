import sys
import socket

from threading import Thread, Timer, Semaphore
from time import sleep

MY_IP = 'localhost' # mudar de acordo com o IP da maquina
INFINITY = 16
SEP = ':'

TAMANHO_MSG = 50

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

sckt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sckt.bind((MY_IP, int(PORTO)))


sem = Semaphore(value=1) # semaforo para sincronizacao da tabela de vizinhos e de roteamento

def adiciona_vizinho(msg):
    '''Adiciona o nome, ip e porto recebidos na lista de vizinhos e na tabela de encaminhamento (com distancia 1)'''
    nome, ip, port = msg[3], msg[1], msg[2]
    sem.acquire()
    tabela_vizinhos.append((nome, ip, port))
    tabela_roteamento[nome] = (nome, 1, nome)
    sem.release()

def remove_vizinho(msg):
    '''Remove o vizinho de ip e porto recebidos da lista de vizinhos e atualiza a distancia para infinito na tabela de roteamento'''
    global tabela_vizinhos

    aux = []
    nome_vizinho = ''

    sem.acquire()  
    # busca o nome do roteador correspondente ao ip e porto informados
    for vizinho in tabela_vizinhos:
        if vizinho[1] != msg[1] or vizinho[2] != msg[2]:
            aux.append(vizinho)
        else:
            nome_vizinho = vizinho[0]
    tabela_vizinhos = aux            
    sem.release()

    sem.acquire()    
    # busca o roteador pelo seu nome na tabela de roteamento, e se encontrar, atualiza a distancia para infinito
    if nome_vizinho in tabela_roteamento.keys():
        tabela_roteamento[nome_vizinho] = (tabela_roteamento[nome_vizinho][0], INFINITY, tabela_roteamento[nome_vizinho][2])
        new_msg = COMMAND_D + SEP + MY_IP + SEP + str(PORTO)
        # envia uma mensagem ao roteador que foi desconectado para que ele possa remover o atual roteador de sua lista de vizinhos também
        sckt.sendto(new_msg.encode("latin-1"),(msg[1], int(msg[2])))
    sem.release()

    sem.acquire()
    # atualiza rotas que possuem o roteador desconectado como "proximo passo" com uma distancia infinita
    for rota in tabela_roteamento.values():
        if nome_vizinho == rota[2]:
            tabela_roteamento[rota[0]] = (rota[0], INFINITY, tabela_roteamento[rota[0]][2])
    sem.release()

def manda_anuncio():
    '''Envia um anuncio de rotas para todos os vizinhos'''
    sleep(1)
    # aguarda um segundo antes de montar a mensagem
    anuncio = monta_anuncio(tabela_roteamento, IDENTIFICADOR)
    sem.acquire()
    for vizinho in tabela_vizinhos:
        if vizinho[0] != IDENTIFICADOR:
            sckt.sendto(anuncio.encode("latin-1"),(vizinho[1], int(vizinho[2])))
    sem.release()

def monta_anuncio(tb_roteamento, nome_roteador):
    '''Constroi a mensagem a ser enviada no anuncio de um roteador'''
    tabela_anuncio = []
    sem.acquire()
    # percorre a tabela de roteamento para montar uma tabela de rotas a serem enviadas no anuncio
    for rota in tb_roteamento.values():
        tabela_anuncio.append((rota[0], rota[1]))
    sem.release()

    # monta a mensagem
    mensagem = '11111' + SEP + nome_roteador + SEP + str(len(tabela_anuncio))
    for (dest, cust) in tabela_anuncio:
        mensagem = mensagem + SEP + dest + SEP + str(cust)

    return mensagem

def encerra_execucao():
    exit(1)

def imprime_tabela():
    '''Imprime a tabela de roteamento do roteador atual'''
    sem.acquire()
    print(IDENTIFICADOR)
    for rota in tabela_roteamento.values():
        print(rota[0], end=" ")
        print(rota[1], end=" ")
        print(rota[2])
    print('\n')
    sem.release()

def envia_mensagem(msg, nome_origem):
    '''Envia diretamente ou encaminha uma mensagem da origem para o roteador destino'''
    mensagem = msg[1]
    nome_destino = msg[2]

    # se for menor que 4 eh pq veio de uma mensagem da interface de controle
    if len(msg) < 4:
        nome_origem = IDENTIFICADOR
    # se nao for, veio de outro roteador
    else:
        nome_origem = msg[3]
    # nome_origem guarda o nome do roteador que enviou a mensagem
    
    sem.acquire()
    # procura o destino pelo nome na tabela de roteamento e se nao encontrar, imprime X
    if nome_destino not in tabela_roteamento.keys():
        print("X " +  mensagem + " de " + nome_origem + " para " + nome_destino)
        return
    # busca o nome do "proximo passo"
    nome_next = tabela_roteamento[nome_destino][2] 
    sem.release()
    
    if nome_destino == IDENTIFICADOR:
        # se o nome do destino for o nome do proprio roteador atual, a mensagem chegou ao destino e imprime-se R
        print("R " +  mensagem + " de " + nome_origem + " para " + nome_destino)
        return
    else:
        # caso contrario, imprime-se E e encaminha a mensagem para o "proximo passo"
        print("E " +  mensagem + " de " + nome_origem + " para " + nome_destino + " através de " + nome_next)

    ip_next = ''
    port_next = None

    sem.acquire()
    # busca o ip e porta do "proximo passo"
    for vizinho in tabela_vizinhos:
        if vizinho[0] == nome_next:
            ip_next = vizinho[1]
            port_next = vizinho[2]
            break
    sem.release()

    if nome_origem != '':
        nome_origem = SEP + nome_origem

    # envia mensagem ao roteador identificado como "proximo passo"
    new_msg = COMMAND_E + SEP + mensagem + SEP + nome_destino + nome_origem
    sckt.sendto(new_msg.encode("latin-1"),(ip_next, int(port_next)))

def recebe_anuncio(msg, emissor):
    '''Recebe uma mensagem de anuncio, a interpreta e chama distance vector para fazer o roteamento'''
    achei = False

    sem.acquire()
    # procura o emissor da mensagem na tabela de vizinhos 
    for vizinho in tabela_vizinhos:
        if vizinho[0] == msg[1]:
            achei = True
    # se nao encontrar o emissor na tabela de vizinhos, ele é adicionado
    if achei == False and msg[1] != IDENTIFICADOR:
        if emissor[1][0] == '127.0.0.1':
            tabela_vizinhos.append((msg[1],'localhost',str(emissor[1][1])))
        else:
            tabela_vizinhos.append((msg[1],str(emissor[1][0]),str(emissor[1][1])))
    sem.release()

    tabela_anuncio = []
    # monta uma tabela de anuncio recebido de acordo com a mensagem que foi recebida
    for i in range(3, len(msg), 2):
        tabela_anuncio.append((msg[i], msg[i+1]))

    # roteamento
    distance_vector(tabela_anuncio, msg[1])

def distance_vector(tabela_anuncio, vizinho):
    '''De acordo com um anuncio, recalcula as distancias das rotas atuais ou adiciona novas rotas, na tabela de roteamento'''
    for anuncio in tabela_anuncio:
        destino = anuncio[0]
        custo = anuncio[1]
        sem.acquire()
        if destino not in tabela_roteamento.keys(): 
            tabela_roteamento[destino] = (destino, int(custo) + 1, vizinho)
        else:
            if int(custo) + 1 < tabela_roteamento[destino][1]:
                tabela_roteamento[destino] = (destino, int(custo) + 1, vizinho)
            else:
                if tabela_roteamento[destino][2] == vizinho:
                    tabela_roteamento[destino] = (destino, int(custo) + 1, tabela_roteamento[destino][2])
        sem.release()

while True:
    # thread de temporização que manda um anuncio aos vizinhos a cada segundo
    t = Timer(interval=1.0, function=manda_anuncio)
    t.start()

    # aguarda por uma mensagem 
    emissor = sckt.recvfrom(TAMANHO_MSG)
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
