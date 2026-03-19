# Resumo

## Request & Limits na prática

Caso você receba o erro:

```bash
error: Metrics API not available
```

Significa que o **Metrics Server** não está instalado.

Você pode instalar seguindo a documentação oficial.

---

## Goldilocks: Como descobrir o request/limits ideal para a aplicação

**Goldilocks** é uma ferramenta fantástica para definir o request/limits ideal para a aplicação.

### Guia de instalação do Goldilocks

Consulte o guia oficial para instalação.

### Outros links interessantes usados na aula:

- Download do Helm  
- Vertical Pod Autoscaler  
- Values do Helm Chart do Goldilocks  

---

## Troubleshooting: Como analisar OOM (Out Of Memory) no cluster Kubernetes?

O segredo aqui é acessar o **Node** que está hosteando o pod e procurar pelos arquivos:

- `/var/log/messages`
- `/var/log/kern.log`

Dentro do log, você terá uma mensagem parecida com essa:

```bash
Nov 9 16:40:30 k8s-worker-2 kernel: [5189358.480218] Memory cgroup out of memory: Killed process 321757 (java) total-vm:3473912kB, anon-rss:972768kB, file-rss:0kB, shmem-rss:0kB, UID:0 pgtables:2072kB oom_score_adj:918
```

É importante se atentar ao **anon-rss** ou **file-rss**, que representa o quanto foi efetivamente alocado na memória física pelo processo.

A partir disso, você pode tirar insights sobre o consumo e talvez ter uma ideia do que modificar.

Além disso, é sempre recomendável analisar o sistema de monitoramento por métricas de consumo de RAM para entender melhor o que ocorreu.

---

## Variáveis de Ambiente

Conforme os **12 Factors**, a configuração da aplicação deve ser feita por meio de variáveis de ambiente.

Por isso, é muito comum injetar dentro de cada container as variáveis referentes à aplicação.

> **Store config in the environment**