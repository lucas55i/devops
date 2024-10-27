# Anotações sobre o projeto de cicd

Arquitetura do Projeto

gitea
jenkis
testes
sonar
build
harbor
infra-test
deploy -- ArgoCD


Todo o processo será feito no Kubernetes

Gitflow: https://www.atlassian.com/br/git/tutorials/comparing-workflows/gitflow-workflow

---

# Criação do cluster
Antes de iniciar qualquer processo no nosso cluster Kind, vamos configurar alguns limites de arquivos abertos. Isso é importante porque tudo vai rodar localmente, então vai acabar usando os limites do sistema host mesmo. Aqui tem uma referência de problema que já ocorreu:

3 control-plane node setup not starting · Issue #2744 · kubernetes-sigs/kind

$ echo fs.inotify.max_user_watches=655360 | sudo tee -a /etc/sysctl.conf
$ echo fs.inotify.max_user_instances=1280 | sudo tee -a /etc/sysctl.conf
$ sudo sysctl -p
Com isso vamos iniciar a criação do nosso cluster com o seguinte arquivo de configuração:

kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
- role: worker
- role: worker
containerdConfigPatches:
  - |-
    [plugins."io.containerd.grpc.v1.cri".registry.mirrors."harbor.localhost.com"]
      endpoint = ["<https://harbor.localhost.com>"]
    [plugins."io.containerd.grpc.v1.cri".registry.configs]
      [plugins."io.containerd.grpc.v1.cri".registry.configs."harbor.localhost.com".tls]
        insecure_skip_verify = true
$ kind create cluster --config config.yaml
Makefile
Como vocês já sabem pelos outros treinamentos, eu sou um grande fã do uso do Makefile, ainda mais para trabalhar em projetos localmente. Vamos iniciar um Makefile e ir melhorando ao longo do treinamento. Recomendo a esse leitura complementar.

create:
	@kind create cluster --config config.yaml
 
down:
	@kind delete clusters kind
Com isso podemos subir e destruir o cluster assim:

$ make create
$ make down
Configurando hosts (manual)
Para que os nodes consigam falar corretamente com as URLs expostas no nosso Ingress, e sem um DNS, precisamos configurar no /etc/hosts.

for container in $(docker ps --filter "label=io.x-k8s.kind.role=worker" -q); do
	docker exec $container \
		bash -c "echo '172.21.0.50 argocd.localhost.com jenkins.localhost.com gitea.localhost.com sonarqube.localhost.com harbor.localhost.com' >> /etc/hosts"
done
Configurando hosts (DaemonSet)
Outra opção, e que dá menos trabalho, é deixar um DaemonSet que vai fazer essa configuração para você sempre que iniciar o cluster.

apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: setup-hosts
  namespace: default
spec:
  selector:
    matchLabels:
      name: setup-hosts
  template:
    metadata:
      labels:
        name: setup-hosts
    spec:
      initContainers:
      - name: setup-hosts
        image: busybox
        command:
          - /bin/sh
          - -c
          - |
            grep jenkins /tmp/hosts || echo '172.21.0.50 argocd.localhost.com jenkins.localhost.com gitea.localhost.com sonarqube.localhost.com harbor.localhost.com' >> /tmp/hosts
        volumeMounts:
        - name: etc
          mountPath: /tmp/hosts
          subPath: hosts
      containers:
      - image: "gcr.io/google-containers/pause:2.0"
        name: pause
      volumes:
      - name: etc
        hostPath:
          path: /etc




