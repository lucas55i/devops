.DEFAULT_GOAL := create

pre:
	@kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.9/config/manifests/metallb-native.yaml
	@kubectl wait --namespace metallb-system --for=condition=ready pod --selector=app=metallb --timeout=90s  
	@kubectl apply -f manifests/

create:
	@kind create cluster --config config.yaml

helm:
	@helmfile apply 

up: create pre helm

destroy:
	@kind delete clusters kind

passwd:
	@echo "Jenkins"
	@kubectl get secret -n jenkins jenkins -ojson | jq -r '.data."jenkins-admin-password"' | base64 -d


kaniko:
	@docker run -it \
		--network kind \
		--entrypoint "" \
		--add-host harbor.localhost.com:172.18.0.50 \
		--volume $(pwd)/app:/app \
		--volume $(pwd)/config.json:/kanico/.docker/config.json \  
		--workdir /app \
		gcr.io/kaniko-project/executor:debug sh 