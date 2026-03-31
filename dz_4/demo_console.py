from fastapi.testclient import TestClient
from main import app, TaskService, TaskIn
from unittest.mock import Mock

client = TestClient(app)

def run_demo():
    r = client.post("/auth/register", json={"email": "test@example.com", "password": "password"})
    print(f"Регистрация: {r.status_code} {r.json()}")
    
    r = client.post("/auth/login", json={"email": "test@example.com", "password": "password"})
    print(f"Логин: {r.status_code} {r.json()}")
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    r = client.post("/tasks/", headers=headers, json={"title": "Test", "description": "Desc"})
    print(f"Создание задачи: {r.status_code} {r.json()}")
    task_id = r.json().get("id")
    
    r = client.post(f"/v1/tasks/{task_id}/comments", headers=headers, json={"content": "Comment 1"})
    print(f"POST комментарий: {r.status_code} {r.json()}")
    
    r = client.get(f"/v1/tasks/{task_id}/comments", headers=headers)
    print(f"GET комментарии: {r.status_code} {r.json()}")
    
    r = client.get("/tasks/99999", headers=headers)
    print(f"TaskNotFound задача: {r.status_code} {r.json()}")
    
    r = client.post("/v1/tasks/99999/comments", headers=headers, json={"content": "Bad"})
    print(f"TaskNotFound POST комментарий: {r.status_code} {r.json()}")
    
    r = client.get("/v1/tasks/99999/comments", headers=headers)
    print(f"TaskNotFound GET комментарии: {r.status_code} {r.json()}")
    
    mock_repo = Mock()
    service = TaskService(mock_repo)
    task_data = TaskIn(title="Unit", description="Test")
    mock_repo.create.return_value = type('Task', (), {"id": 1, "title": "Unit"})()
    result = service.create_task(task_data)
    mock_repo.create.assert_called_once_with(task_data)
    print(f"Unit-тест: {'PASSED ✓' if result.title == 'Unit' else 'FAILED ✗'}")
    
    r = client.post("/tasks/", headers=headers, json={"title": "Integration", "description": "Test"})
    print(f"Интеграционный тест: {'PASSED ✓' if r.status_code == 200 else 'FAILED ✗'}")
    
    client.delete(f"/tasks/{task_id}", headers=headers)
    print("\n Tесты завершены")

if __name__ == "__main__":
    run_demo()