.PHONY: up down register test logs clean update

up:
	docker compose up -d --build

down:
	docker compose down

register:
	curl -X POST http://localhost:9070/deployments \
	     -H "Content-Type: application/json" \
	     -d '{"uri": "http://legal-agent:9080"}'

test:
	python test_legal_agent.py

logs:
	docker compose logs -f

clean:
	docker compose down -v

update:
	docker compose build legal-agent
	docker compose up -d legal-agent
	@echo "⏳ Đang chờ service khởi động lại..."
	sleep 3
	make register
	@echo "✅ Cập nhật thành công!"