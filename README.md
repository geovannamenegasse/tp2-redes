# tp2-redes

1. Não precisa tratar falhas do UDP
2. Não é preciso implementar qualquer técnica especial para determinar quando um nó ou um link falham. Isso será simulado explicitamente por um comando da interface de controle. Quando um nó ou link falham, a rota deve ser marcada como com distância infinita. No nosso caso, vamos adotar infinito igual a 16.



Dúvidas:
1. Tudo no localhost ou usar interface de redes? Pode ser tudo no localhost mas tem que funcionar em redes diferentes
2. Preciso verificar e descartar distancias 16?
3. o inteiro curto (short int) com o número do comando que identifica a mensagem deverá ter o valor 11111
4. O anuncio vai ser a tabela de roteamento?
5. custo = distancia?

Falta:
1. Threads (mutex)
2. Corrigir strings de localhost
3. Algumas validações
4. Por short int na msg


Relatório:
https://docs.google.com/document/d/1u4hqjuvOlH_eSNmpN5gu1MQ2tTDb-EBfz5Jbw6VziOQ/edit?usp=sharing