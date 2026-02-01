CONTAINERS = \
	comunidade-devops-control-plane \
	comunidade-devops-worker \
	comunidade-devops-worker2

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
	@docker ps -a --filter "name=comunidade-devops"

