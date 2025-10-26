#!/bin/bash

NOME="Lucas Silva"

echo $NOME

NUMERO_1=24
NUMERO_2=45

TOTAL=$(($NUMERO_1+$NUMERO_2))

echo $TOTAL

SAIDA_CAT=$(cat /etc/passwd | grep Lucas )
echo $SAIDA_CAT

echo "------------------------------------"

echo "Parametro 1: $1"
echo "Parametro 2: $2"

echo "Todos os parametos: $*"
echo "Quantos parametros?: $#"


echo "Saida do último comando: $?"

echo "PID $$"

echo "$0"
