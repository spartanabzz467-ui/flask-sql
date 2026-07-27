import pytest

from app import create_app, db


@pytest.fixture
def client():
    app = create_app({
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "TESTING": True,
    })
    with app.app_context():
        db.create_all()
        with app.test_client() as client:
            yield client
        db.drop_all()


def test_create_exercise(client):
    resp = client.post("/exercises", json={"name": "Deadlift", "category": "strength"})
    assert resp.status_code == 201
    assert resp.get_json()["name"] == "Deadlift"


def test_create_exercise_bad_category(client):
    resp = client.post("/exercises", json={"name": "Deadlift", "category": "not-a-category"})
    assert resp.status_code == 400


def test_create_exercise_duplicate_name(client):
    client.post("/exercises", json={"name": "Deadlift", "category": "strength"})
    resp = client.post("/exercises", json={"name": "Deadlift", "category": "strength"})
    assert resp.status_code == 400


def test_create_and_list_workouts(client):
    resp = client.post("/workouts", json={"notes": "Leg day"})
    assert resp.status_code == 201
    resp = client.get("/workouts")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_add_exercise_to_workout(client):
    ex = client.post("/exercises", json={"name": "Squat", "category": "strength"}).get_json()
    wk = client.post("/workouts", json={"notes": "Leg day"}).get_json()

    resp = client.post(
        f"/workouts/{wk['id']}/exercises",
        json={"exercise_id": ex["id"], "sets": 3, "reps": 10},
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert len(body["exercise_links"]) == 1
    assert body["exercise_links"][0]["sets"] == 3


def test_add_exercise_to_workout_invalid_reps(client):
    ex = client.post("/exercises", json={"name": "Squat", "category": "strength"}).get_json()
    wk = client.post("/workouts", json={"notes": "Leg day"}).get_json()

    resp = client.post(
        f"/workouts/{wk['id']}/exercises",
        json={"exercise_id": ex["id"], "reps": -5},
    )
    assert resp.status_code == 400


def test_delete_workout(client):
    wk = client.post("/workouts", json={"notes": "Leg day"}).get_json()
    resp = client.delete(f"/workouts/{wk['id']}")
    assert resp.status_code == 204
    assert client.get(f"/workouts/{wk['id']}").status_code == 404
