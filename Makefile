.PHONY: backend frontend dev docker reset test clean build

backend:
	cd backend && uvicorn app.main:app --reload

frontend:
	cd frontend && npm run dev

docker:
	docker compose up --build

reset:
	docker compose down -v
	docker compose up --build

test:
	cd backend && pytest -q

build:
	cd frontend && npm install && npm run build

clean:
	rm -rf backend/trustdoc.db backend/data/uploads backend/.pytest_cache frontend/node_modules frontend/dist
