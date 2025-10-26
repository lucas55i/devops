#!/bin/bash

echo "Parametro 1: $1"
echo "Parameto 2: $2"

if [ $1 > 10 ]; then
   echo "O parameto 1 é maior que 10"
   echo "Nome arquivo: $0"
   echo "Processo: $#"
fi
