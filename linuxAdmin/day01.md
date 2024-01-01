## Day 1

- História
- Instalação do Virtual-box
- Instalação do Debian
  - dowload da imagem no site do debian
  - configurações basicas para funcionamento
  - Instalação deve ser feita no modo texto.

## Day 2

- Acesso ao Linux via SSH
- Conhecendo o shell do Linux.

  - ls, ls -a, ls -lha
  - arquivos que comoçam com . são arquvios ocultos.

  ```bash
      drwx------  6 root root 4,0K out  4 12:29 .
      drwxr-xr-x 19 root root 4,0K set  8 13:41 ..
      -rw-r--r--  1 root root 3,1K out 17  2022 .bashrc
      drwx------  2 root root 4,0K abr 18 17:34 .cache
      -rw-------  1 root root   20 out  4 12:29 .lesshst
      drwxr-xr-x  4 root root 4,0K set  8 15:49 .npm
      -rw-r--r--  1 root root  161 out 17  2022 .profile
      drwx------  5 root root 4,0K set  8 13:42 snap
      drwx------  2 root root 4,0K set  8 13:42 .ssh
  ```

  - cat visualizar conteudo de arquivos.
  - ctrl + l = clear.
  - shell [bash], existem varios tipos interação com linux.
  - history mostra o histórico de comandos digitados.
  - cd / leva para o diretório raiz.
  - pwd mostra a onde estou.
  - estrutura de diretórios FHS
    - Norma para as distribuições linux.
    - FHS(Filesystem Hierarchy Standard).
      - Hierarquia de sistemas de arquivos.
    - cd /bin binarios do sistema(executaveis).
    - cd /boot arquivos fundamentais para inicialização so sistema(onde fica o knell linux).
    - /bin - Binários de usuários, essenciais no boot
    - /sbin - Binários do superusuário, essenciais no boot
    - /boot - Arquivo do gerenciador de partida e kernel, símbolos
    - /dev - Dispositivos do sistema
    - /etc - Arquivos de configuração globais
      - /etc/opt - Arquivos de configuração para aplicativos em /opt
      - /etc/X11 - Arquivos de configuração para o X Window System 11
    - /home - Armazenamento de dados de contas de usuários normais
    - /root - Armazenamento de dados de contas do superusuário
    - /lib - Bibliotecas essenciais do sistema, de binários localizados em /bin e /sbin
    - /mnt - Sistema de arquivos montado temporariamente
    - /media - Ponto de montagem de mídias removíveis (como pen-drives, cd-rom)
    - /opt - Pacotes estático de aplicações
    - /proc - systema de arquivos virtual, onde pode fazer a interação com o kernel e processos do sistema
    - /tmp - Arquivos temporários. Conteúdo geralmente apagado no reboot nas distribuições
    - /usr - (unix system resources) - Hierarquia secundária (não essenciais no boot) para dados compartilhados de usuários
    - /usr/bin - O mesmo que a hierarquia /bin, mas contém binários não essenciais ao funcionamento da máquina ou para o recovery
      - /usr/include - Diretório padrãod para headers
      - /usr/lib - O mesmo que a hierarquia /lib, mas não essenciais ao boot
      - /usr/sbin - O emsmo que o /sbin, mas não essenciais ao boot da máquina
      - /usr/share - Dados compartilhados independentes de arquitetura
      - /usr/src - Armazenamento de código fonte da máquina
      - /usr/X11R6 - - X Window Sysem, versão 11R6
      - /usr/local - Armazenamento de binários não distribuidos na instalação principal da máquina, ou seja, fora do sistema de empacotamento. Também é o local de armazenamento terciário de dados
    - /var - Arquivos que são gravados comf requencia (logs, páginas web, email, imagens, etc)
      - /var/lock - Arquivos de lock, usados para controlar corretamente os recursos em uso
      - /var/log - Arquivos de log, usado para logs em geral
      - /var/mail - Caixas de e-mail dos usuários do sistema em formato mailbox
      - /var/run - Contém dados sobre a execução do sistema desde seu primeiro boot (daemons e usuários)
      - /var/spool - Spooling de tarefas (fila de impressão, cache de pacotes, proxy, etc)
      - /var/spool/mail - Antigo local da caixa de correio de usuários (deve ser usado /var/mail)
      - /var/tmp - Arquivos temporários. Quando usado em modo multi-usuário.

## Day 3

- Comandos Internos(são comando contidos dentro do interpretador de comandos proprio shel) e Externos.
- which, indentifica se o binario está na sua maquina
  ```bash
    lucas@mymaxLca:~/Dev/devops/linuxAdmin$ which docker
    /usr/bin/docker
  ```
- Comando sobre manipulação de diretórios.
  - ls

    - É possivel listar o conteudo de duas pastas ao mesmo tempo ls [dir] [dir]

      ```bash
          lucas@mymaxLca:~/Dev/devops$ ls linuxAdmin/ kubernetes/
          kubernetes/:
          descomplicandoKub

          linuxAdmin/:
          day01.md
      ```

    - ls -l [dir] -d, lista dados do diretorio.
    - ls -f lista por orden de criação e alteração.
    - ls -n lista em formato númerico.
    - ls -l -o lista apenas o dono.
    - ls -l -g lista apenas o grupos.
    - ls -t lista por data de criação.
    - ls -latr lista os mais recentes.
    - ls -lac lista por hora de criação.
    - ls -lax lista pela extensão do arquivo
    - ls -lar lista de forma recursiva.
    - ls -la

  - cd caminha entre pastas.
  - pwd me diz onde estou exatamente no terminal
    ```bash
    lucas@mymaxLca:~/Dev/devops$ pwd
    /home/lucas/Dev/devops
    ```
- Comando para manipulação de arquvios.
  - cat visualizar o conteudo dos arquivos.
  - tac visualiza de forma invertida.
  - cp serve para copiar arquvios
    - cp -u copia arquivos da origem
    - cp -x copia pastas e subpastas de outras partições.
  - mv move arquivos.