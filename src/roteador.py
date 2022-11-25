import sys
import socket

identificador = sys.argv[1]
porto = sys.argv[2] 

vizinhos = []
tabela_roteamento = [(identificador, 0, identificador)]

print("Roteador " + identificador + " iniciado...")

sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sck.bind((identificador, int(porto)))

while True:
    msg = (sck.recv(40).decode("utf-8")).split(':')

    if msg[0] == 'C': 
        print("Adicionando roteador aos vizinhos...")
        nome = msg[3]
        ip = msg[1]
        port = msg[2]
        vizinhos.append((nome, ip, port))
        print(vizinhos)

    elif msg[0] == 'D':
        aux = []
        print("Removendo roteador dos vizinhos...")
        for vizinho in vizinhos:
            if vizinho[1] != msg[1] or vizinho[2] != msg[2]:
                aux.append(vizinho)
        vizinhos = aux            
        print(vizinhos)
        # atualizar rotas que tem proximo passo como esse vizinho para distancia 16

    elif msg[0] == 'I':
        pass

    elif msg[0] == 'F':
        print("Finalizando execução do roteador " + identificador)
        exit(1)

    elif msg[0] == 'T':
        print("Tabela de Roteamento")
        print(identificador)
        for rota in tabela_roteamento:
            print(rota)
        print('\n')

    elif msg[0] == 'E':
        print(msg)
        mensagem = msg[1]
        ip = msg[2]
        port = msg[3]
        
        sck.sendto(mensagem.encode("latin-1"),(ip, int(port)))

    else:
        print(msg)

