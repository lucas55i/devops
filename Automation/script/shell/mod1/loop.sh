#!/bin/bash

echo "FOR 1 ======"

for (( i = 0; i < 10; i++ )); do
   echo $i
done

echo "FOR 2 ======"
for i in $(seq 10); do
  echo $i
done


echo "==== For 3 (array)"
Frutas=(
'Laranja'
'Ameixa'
'Abacaxi'
)

for i in "${Frutas[@]}"; do
  echo $i
done


echo "===== While"
contador=0
while [ $contador -lt ${#Frutas[@]} ]; do
  echo $contador
  contador=$(($contador+1))
done
