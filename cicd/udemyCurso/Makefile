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