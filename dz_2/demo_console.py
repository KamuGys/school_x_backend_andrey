from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def run_demo():
    # --- Регистрация пользователя ---
    print("\n--- Регистрация пользователя ---")
    r = client.post("/auth/register", json={"email":"studentееее@test.com","password":"1234"})
    print("Статус:", r.status_code, "Ответ:", r.json())

    # --- Логин пользователя ---
    print("\n--- Логин пользователя ---")
    r = client.post("/auth/login", json={"email":"studenteeeeee@test.com","password":"1234"})
    print("Статус:", r.status_code, "Ответ:", r.json())
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # --- Создание задачи ---
    print("\n--- Создание задачи ---")
    r = client.post("/tasks/", headers=headers, json={
        "title": "Сделать ДЗ",
        "description": "FastAPI тест",
        "status": "pending"
    })
    print("Статус:", r.status_code, "Ответ:", r.json())
    task_id = r.json().get("id")

    # --- Получение всех задач ---
    print("\n--- Получение всех задач ---")
    r = client.get("/tasks/", headers=headers)
    print("Статус:", r.status_code, "Ответ:", r.json())

    # --- Получение задачи по ID ---
    print("\n--- Получение задачи по ID ---")
    r = client.get(f"/tasks/{task_id}", headers=headers)
    print("Статус:", r.status_code, "Ответ:", r.json())

    # --- Обновление задачи ---
    print("\n--- Обновление задачи ---")
    r = client.put(f"/tasks/{task_id}", headers=headers, json={
        "title": "Сделать ДЗ исправлено",
        "status": "done"
    })
    print("Статус:", r.status_code, "Ответ:", r.json())

    # --- Удаление задачи ---
    print("\n--- Удаление задачи ---")
    r = client.delete(f"/tasks/{task_id}", headers=headers)
    print("Статус:", r.status_code, "Ответ:", r.json())

    # --- Проверка, что задач больше нет ---
    print("\n--- Проверка, что задач больше нет ---")
    r = client.get("/tasks/", headers=headers)
    print("Статус:", r.status_code, "Ответ:", r.json())

if __name__ == "__main__":
    run_demo()