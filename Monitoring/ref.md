# 4 Golden Signals do SRE.

## Monitoramento

    - Latencia
    - Trafego
    - Erros
    - Saturação

## Latencia

É o tempo que leva para responder uma requisição. Separar os resultados das requisições tanto sucesso como erro.

## Trafego

Representa o volume de demandas que a aplicação ou infraestrutura recebe

- Usuários conectados
- Quantidade de operações de leitura e escrita em banco de dados
- Medir o trafego na quantidade de requisiições que sua aplicação recebe em determinado espaço de tempo
- Medir momentos em que se faz necessário escalar a sua infraestrutura(Gera economia)

## Erros

Os erros podem dizer muito sobre a saúde de sua aplicação e infraestrutura.

- Categorizar os erros para saber atuar de forma mais rapida no problema
- Tipods de erros.
  - HTTP-Requests
  - Exeções lançadas pela sua aplicação e saturação.

## Saturação

A saturação mede quanto um serviço está sobrecarregado, ou sobrecarregando os recursos disponibilizados.

- Monitorar metricas de desemprenho de Hardware.
- CPU, Memória, Disco e Serviço
