# Workout Tracker API

A Flask + SQLAlchemy + Marshmallow backend API for a workout tracking application
used by personal trainers. Trainers can manage a reusable library of exercises
and build workouts by attaching exercises with per-workout sets, reps, or
duration.

## Description

The API is built around three models:

- **Exercise** — a reusable exercise (e.g. "Barbell Squat"). Exercises can be
  attached to many different workouts.
- **Workout** — a single training session on a given date.
- **WorkoutExercise** — the join table between `Workout` and `Exercise`. It
  carries the sets/reps/duration for that specific pairing, which is what
  lets the same `Exercise` be reused across many `Workout`s with different
  parameters each time.

The app follows an application-factory + blueprint structure for
maintainability:

```
workout-tracker-backend/
├── app/
│   ├── __init__.py          # app factory, db/migrate setup
│   ├── models.py            # SQLAlchemy models, constraints, validations
│   ├── schemas.py           # Marshmallow schemas + schema validations
│   └── resources/
│       ├── workouts.py      # /workouts endpoints
│       └── exercises.py     # /exercises endpoints
├── migrations/               # Flask-Migrate / Alembic migrations
├── tests/
│   └── test_api.py
├── app.py                    # entrypoint (flask run)
├── seed.py                   # populates example data for all models
├── Pipfile
└── README.md
```

## Installation

```bash
pipenv install
pipenv shell
```

(If you prefer plain `pip`, a `pip install -r requirements.txt`-equivalent
set of packages is listed in the `Pipfile`.)

Set up the database:

```bash
export FLASK_APP=app.py      # Windows (cmd): set FLASK_APP=app.py
flask db init                 # only needed once, if migrations/ isn't present
flask db migrate -m "initial migration"
flask db upgrade
python seed.py
```

## Run instructions

```bash
export FLASK_APP=app.py
flask run --port 5555
```

The API will be available at `http://127.0.0.1:5555`.

Run the test suite with:

```bash
python -m pytest tests/
```

## Endpoints

| Method | Endpoint                          | Description                                              |
|--------|------------------------------------|------------------------------------------------------------|
| GET    | `/workouts`                        | List all workouts, with their linked exercises            |
| GET    | `/workouts/<id>`                   | Get a single workout by id                                 |
| POST   | `/workouts`                        | Create a workout (`date`, `notes`)                          |
| DELETE | `/workouts/<id>`                   | Delete a workout                                            |
| POST   | `/workouts/<id>/exercises`         | Attach an existing exercise to a workout (`exercise_id`, `sets`, `reps`, `duration_seconds`) |
| GET    | `/exercises`                       | List all exercises                                          |
| GET    | `/exercises/<id>`                  | Get a single exercise by id                                 |
| POST   | `/exercises`                       | Create an exercise (`name`, `category`, `equipment_needed`) |
| DELETE | `/exercises/<id>`                  | Delete an exercise                                           |

### Validation summary

- **Table constraints**: unique exercise name, non-empty name check, positive
  `sets`/`reps`/`duration_seconds` checks on `workout_exercises`.
- **Model validations**: exercise name length/blank check, category must be
  in an allowed list, workout notes length limit, `WorkoutExercise` requires
  positive values and at least one of sets/reps/duration.
- **Schema validations**: Marshmallow `Length`, `OneOf`, and `Range`
  validators on incoming request payloads for exercises and workout-exercise
  links.

## Notes

This app does not implement update (`PATCH`/`PUT`) actions or the ability to
remove an exercise from a workout, per the assignment spec — only create,
delete, and view for workouts/exercises, plus adding an exercise to a
workout.
