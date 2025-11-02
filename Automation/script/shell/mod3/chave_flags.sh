#!/bin/bash
#
# listaUsuarios.sh - Extrai usuários do /etc/passwd
#
# Site:             https://seusite.com.br
# Autor:            Lucas Silva Correa de Jesus
# Manutenção:       Lucas Silva Correa de Jesus
#
# ------------------------------------------------------------------------ #
#  Irá extrair usuários do /etc/passwd, havendo a possibilidade de colocar
#  em maiúsculo e em ordem alfabética.
#
#  Exemplos:
#    $ ./listaUsuarios.sh -s -m
#    Neste exemplo ficará em maiúsculo e em ordem alfabética.
# ------------------------------------------------------------------------ #
# Histórico:
#
#   v1.0 02/11/2025, Lucas:
#     - Adicionando -s, -h & -v
#   v1.1 02/11/2025, Lucas:
#     - Melhorias no código e formatação
# ------------------------------------------------------------------------ #
# Testado em:
#   bash 4.4.19
# ------------------------------------------------------------------------ #

# ---------------------------------- VARIÁVEIS ---------------------------------- #
USUARIOS="$(cut -d : -f 1 /etc/passwd)"
MENSAGEM_USO="
$(basename "$0") - [OPÇÕES]

  -h  - Menu de ajuda
  -v  - Versão
  -s  - Ordenar a saída
  -m  - Converter para maiúsculo
"

VERSAO="v1.3"
CHAVE_ORDENA=0
CHAVE_MAIUSCULO=0

# ---------------------------------- EXECUÇÃO ----------------------------------- #
while test -n "$1"; do
  case "$1" in
    -h) echo "$MENSAGEM_USO" && exit 0 ;;
    -v) echo "$VERSAO" && exit 0 ;;
    -s) CHAVE_ORDENA=1 ;;
    -m) CHAVE_MAIUSCULO=1 ;;
     *) echo "Opção inválida! Use -h para ajuda." && exit 1 ;;
  esac
  shift
done

# Ordenação e transformação em maiúsculas
[ $CHAVE_ORDENA -eq 1 ] && USUARIOS=$(echo "$USUARIOS" | sort)
[ $CHAVE_MAIUSCULO -eq 1 ] && USUARIOS=$(echo "$USUARIOS" | tr '[:lower:]' '[:upper:]')

# Exibe resultado final
echo "$USUARIOS"
