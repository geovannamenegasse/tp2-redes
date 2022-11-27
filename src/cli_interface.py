import sys
import socket
from time import sleep

sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if __name__ == '__main__':

    while True:
        entrada = input().split(' ')

        if entrada[2] == 'C':
            end_IP_1 = entrada[0]
            porto_1  = entrada[1]
            end_IP_2 = entrada[3]
            porto_2  = entrada[4]
            nome     = entrada[5]

            msg = entrada[2] + ':' + end_IP_2 + ':' + porto_2 + ':' + nome
            sck.sendto(msg.encode("latin-1"),(end_IP_1, int(porto_1)))

        if entrada[2] == 'D':
            end_IP_1 = entrada[0]
            porto_1  = entrada[1]
            end_IP_2 = entrada[3]
            porto_2  = entrada[4]

            msg = entrada[2] + ':' + end_IP_2 + ':' + porto_2
            sck.sendto(msg.encode("latin-1"),(end_IP_1, int(porto_1)))

        if entrada[2] == 'I':
            end_IP_1 = entrada[0]
            porto_1  = entrada[1]
            
            msg = entrada[2]
            sck.sendto(msg.encode("latin-1"),(end_IP_1, int(porto_1)))

        if entrada[2] == 'F':
            end_IP_1 = entrada[0]
            porto_1  = entrada[1]

            msg = entrada[2]
            sck.sendto(msg.encode("latin-1"),(end_IP_1, int(porto_1)))
            
        if entrada[2] == 'T':
            end_IP_1 = entrada[0]
            porto_1  = entrada[1]

            msg = entrada[2]
            sck.sendto(msg.encode("latin-1"),(end_IP_1, int(porto_1)))
            
        if entrada[2] == 'E':
            end_IP_1 = entrada[0]
            porto_1  = entrada[1]
            mensagem = entrada[3]
            end_IP_2 = entrada[4]
            porto_2  = entrada[5]

            msg = entrada[2] + ':' + mensagem + ':' + end_IP_2 + ':' + porto_2   
            sck.sendto(msg.encode("latin-1"),(end_IP_1, int(porto_1)))
            
        if entrada[2] == 'S':
            sleep(float(entrada[3]))
