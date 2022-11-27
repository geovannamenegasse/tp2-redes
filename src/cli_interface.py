import socket

from time import sleep

SEP = ':'

COMMAND_C = 'C'
COMMAND_D = 'D'
COMMAND_I = 'I'
COMMAND_F = 'F'
COMMAND_T = 'T'
COMMAND_E = 'E'
COMMAND_S = 'S'

sckt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if __name__ == '__main__':

    while True:
        entrada = input().split(' ')

        if entrada[2] == COMMAND_C:
            end_IP_1 = entrada[0]
            porto_1  = entrada[1]
            end_IP_2 = entrada[3]
            porto_2  = entrada[4]
            nome     = entrada[5]

            msg = entrada[2] + SEP + end_IP_2 + SEP + porto_2 + SEP + nome
            sckt.sendto(msg.encode("latin-1"),(end_IP_1, int(porto_1)))

        if entrada[2] == COMMAND_D:
            end_IP_1 = entrada[0]
            porto_1  = entrada[1]
            end_IP_2 = entrada[3]
            porto_2  = entrada[4]

            msg = entrada[2] + SEP + end_IP_2 + SEP + porto_2
            sckt.sendto(msg.encode("latin-1"),(end_IP_1, int(porto_1)))

        if entrada[2] == COMMAND_I:
            end_IP_1 = entrada[0]
            porto_1  = entrada[1]
            
            msg = entrada[2]
            sckt.sendto(msg.encode("latin-1"),(end_IP_1, int(porto_1)))

        if entrada[2] == COMMAND_F:
            end_IP_1 = entrada[0]
            porto_1  = entrada[1]

            msg = entrada[2]
            sckt.sendto(msg.encode("latin-1"),(end_IP_1, int(porto_1)))
            
        if entrada[2] == COMMAND_T:
            end_IP_1 = entrada[0]
            porto_1  = entrada[1]

            msg = entrada[2]
            sckt.sendto(msg.encode("latin-1"),(end_IP_1, int(porto_1)))
            
        if entrada[2] == COMMAND_E:
            end_IP_1 = entrada[0]
            porto_1  = entrada[1]
            mensagem = entrada[3]
            nome_destino = entrada[4]

            msg = entrada[2] + SEP + mensagem + SEP + nome_destino   
            sckt.sendto(msg.encode("latin-1"),(end_IP_1, int(porto_1)))
            
        if entrada[2] == COMMAND_S:
            sleep(float(entrada[3]))
