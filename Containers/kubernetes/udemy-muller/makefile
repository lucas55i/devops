CONTAINERS = \
	study-devops-control-plane \
	study-devops-worker \
	study-devops-worker2

.PHONY: stop start restart status

stop:
	@echo "⛔ Parando cluster Kind..."
	@docker stop $(CONTAINERS)

start:
	@echo "▶️ Iniciando cluster Kind..."
	@docker start $(CONTAINERS)

restart: stop start
	@echo "🔄 Cluster Kind reiniciado."

status:
	@echo "📦 Status dos containers:"
	@docker ps -a --filter "name=study-devops"

