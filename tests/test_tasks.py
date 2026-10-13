def create_task(client, headers, project_id, title="Test task", priority=1):
    return client.post(
        f"/projects/{project_id}/tasks/",
        headers=headers,
        json={
            "title": title,
            "description": "Test description",
            "priority": priority
        }
    )


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "TaskFlow API"
    }


def test_register_and_login(client):
    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 201
    assert "password_hash" not in response.json()

    login = client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "password123"
        }
    )

    assert login.status_code == 200
    assert "access_token" in login.json()


def test_me(client, user_a):
    response = client.get(
        "/auth/me",
        headers=user_a["headers"]
    )

    assert response.status_code == 200
    assert response.json()["username"] == "usera"


def test_no_authentication(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_invalid_token(client):
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401


def test_create_task(client, user_a, project_a):
    response = create_task(
        client,
        user_a["headers"],
        project_a["id"],
        "Learn pytest",
        1
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Learn pytest"
    assert data["priority"] == 1
    assert data["completed"] is False
    assert data["project_id"] == project_a["id"]


def test_get_task(client, user_a, project_a):
    create_response = create_task(
        client,
        user_a["headers"],
        project_a["id"]
    )

    task_id = create_response.json()["id"]

    response = client.get(
        f"/tasks/{task_id}",
        headers=user_a["headers"]
    )

    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_update_task(client, user_a, project_a):
    create_response = create_task(
        client,
        user_a["headers"],
        project_a["id"]
    )

    task_id = create_response.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        headers=user_a["headers"],
        json={
            "title": "Updated",
            "description": "Updated description",
            "priority": 3,
            "completed": True
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Updated"
    assert data["priority"] == 3
    assert data["completed"] is True


def test_patch_task(client, user_a, project_a):
    create_response = create_task(
        client,
        user_a["headers"],
        project_a["id"]
    )

    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        headers=user_a["headers"],
        json={
            "completed": True
        }
    )

    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_delete_task(client, user_a, project_a):
    create_response = create_task(
        client,
        user_a["headers"],
        project_a["id"]
    )

    task_id = create_response.json()["id"]

    response = client.delete(
        f"/tasks/{task_id}",
        headers=user_a["headers"]
    )

    assert response.status_code == 200

    response = client.get(
        f"/tasks/{task_id}",
        headers=user_a["headers"]
    )

    assert response.status_code == 404


def test_invalid_priority(client, user_a, project_a):
    response = create_task(
        client,
        user_a["headers"],
        project_a["id"],
        priority=5
    )

    assert response.status_code == 422


def test_filter_tasks(client, user_a, project_a):
    create_task(client, user_a["headers"], project_a["id"], priority=1)
    create_task(client, user_a["headers"], project_a["id"], priority=3)
    create_task(client, user_a["headers"], project_a["id"], priority=3)

    response = client.get(
        "/tasks/?priority=3",
        headers=user_a["headers"]
    )

    assert response.status_code == 200

    tasks = response.json()["tasks"]

    assert len(tasks) == 2

    for task in tasks:
        assert task["priority"] == 3


def test_sort_tasks(client, user_a, project_a):
    create_task(client, user_a["headers"], project_a["id"], priority=1)
    create_task(client, user_a["headers"], project_a["id"], priority=3)
    create_task(client, user_a["headers"], project_a["id"], priority=2)

    response = client.get(
        "/tasks/?sort=-priority",
        headers=user_a["headers"]
    )

    assert response.status_code == 200

    priorities = [
        task["priority"]
        for task in response.json()["tasks"]
    ]

    assert priorities == [3, 2, 1]


def test_pagination(client, user_a, project_a):
    for i in range(5):
        create_task(
            client,
            user_a["headers"],
            project_a["id"],
            title=f"Task {i}"
        )

    response = client.get(
        "/tasks/?skip=1&limit=2",
        headers=user_a["headers"]
    )

    assert response.status_code == 200
    assert len(response.json()["tasks"]) == 2


def test_task_stats(client, user_a, project_a):
    task1 = create_task(
        client,
        user_a["headers"],
        project_a["id"],
        priority=3
    ).json()

    create_task(
        client,
        user_a["headers"],
        project_a["id"],
        priority=1
    )

    create_task(
        client,
        user_a["headers"],
        project_a["id"],
        priority=3
    )

    task4 = create_task(
        client,
        user_a["headers"],
        project_a["id"],
        priority=2
    ).json()

    client.patch(
        f"/tasks/{task1['id']}",
        headers=user_a["headers"],
        json={"completed": True}
    )

    client.patch(
        f"/tasks/{task4['id']}",
        headers=user_a["headers"],
        json={"completed": True}
    )

    response = client.get(
        "/tasks/stats",
        headers=user_a["headers"]
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 4
    assert data["completed"] == 2
    assert data["pending"] == 2
    assert data["high_priority"] == 2


def test_user_cannot_access_other_users_task(
    client,
    user_a,
    user_b,
    project_a
):
    create_response = create_task(
        client,
        user_a["headers"],
        project_a["id"]
    )

    task_id = create_response.json()["id"]

    response = client.get(
        f"/tasks/{task_id}",
        headers=user_b["headers"]
    )

    assert response.status_code == 404