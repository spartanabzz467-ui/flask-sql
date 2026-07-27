"""Seed the database with example Workouts, Exercises, and WorkoutExercises.

Usage:
    python seed.py
"""
from datetime import date, timedelta

from app import create_app, db
from app.models import Exercise, Workout, WorkoutExercise


def seed():
    app = create_app()
    with app.app_context():
        print("Clearing existing data...")
        WorkoutExercise.query.delete()
        Exercise.query.delete()
        Workout.query.delete()
        db.session.commit()

        print("Seeding exercises...")
        squat = Exercise(name="Barbell Squat", category="strength", equipment_needed="barbell")
        plank = Exercise(name="Plank", category="mobility", equipment_needed="none")
        run = Exercise(name="Interval Run", category="cardio", equipment_needed="treadmill")
        lunge = Exercise(name="Walking Lunge", category="strength", equipment_needed="dumbbells")

        db.session.add_all([squat, plank, run, lunge])
        db.session.commit()

        print("Seeding workouts...")
        leg_day = Workout(date=date.today(), notes="Lower body strength session")
        recovery_day = Workout(
            date=date.today() - timedelta(days=2), notes="Light mobility and core work"
        )
        cardio_day = Workout(date=date.today() - timedelta(days=4), notes="Interval training")

        db.session.add_all([leg_day, recovery_day, cardio_day])
        db.session.commit()

        print("Linking exercises to workouts...")
        links = [
            WorkoutExercise(workout_id=leg_day.id, exercise_id=squat.id, sets=4, reps=8),
            WorkoutExercise(workout_id=leg_day.id, exercise_id=lunge.id, sets=3, reps=12),
            WorkoutExercise(
                workout_id=recovery_day.id, exercise_id=plank.id, duration_seconds=60
            ),
            WorkoutExercise(
                workout_id=cardio_day.id, exercise_id=run.id, duration_seconds=1200
            ),
        ]
        db.session.add_all(links)
        db.session.commit()

        print(
            f"Done. Seeded {Exercise.query.count()} exercises, "
            f"{Workout.query.count()} workouts, "
            f"{WorkoutExercise.query.count()} workout-exercise links."
        )


if __name__ == "__main__":
    seed()
