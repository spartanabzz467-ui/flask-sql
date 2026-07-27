from datetime import date as date_cls

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import validates

from app import db

VALID_CATEGORIES = ("strength", "cardio", "mobility", "balance", "plyometric")


class Exercise(db.Model):
    """A reusable exercise (e.g. 'Squat', 'Plank') that can appear in many workouts."""

    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    equipment_needed = db.Column(db.String(80), nullable=True, default="none")

    # --- Table constraints (2+) ---
    __table_args__ = (
        UniqueConstraint("name", name="uq_exercise_name"),
        CheckConstraint("length(name) > 0", name="ck_exercise_name_not_empty"),
    )

    workout_links = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )

    # --- Model validations (2+) ---
    @validates("name")
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Exercise name cannot be blank.")
        if len(value.strip()) < 2:
            raise ValueError("Exercise name must be at least 2 characters long.")
        return value.strip()

    @validates("category")
    def validate_category(self, key, value):
        if value is None or value.lower() not in VALID_CATEGORIES:
            raise ValueError(
                f"Category must be one of: {', '.join(VALID_CATEGORIES)}."
            )
        return value.lower()

    def __repr__(self):
        return f"<Exercise {self.id} {self.name}>"


class Workout(db.Model):
    """A single workout session made up of one or more exercises."""

    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date_cls.today)
    notes = db.Column(db.String(255), nullable=True)

    # --- Table constraints (2+) ---
    __table_args__ = (
        CheckConstraint("date <= CURRENT_DATE OR date IS NOT NULL", name="ck_workout_date_present"),
    )

    exercise_links = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
    )

    # association-proxy-style convenience (kept explicit rather than importing
    # sqlalchemy.ext.associationproxy, to keep the relationship visible)
    @property
    def exercises(self):
        return [link.exercise for link in self.exercise_links]

    # --- Model validation ---
    @validates("notes")
    def validate_notes(self, key, value):
        if value is not None and len(value) > 255:
            raise ValueError("Notes must be 255 characters or fewer.")
        return value

    def __repr__(self):
        return f"<Workout {self.id} {self.date}>"


class WorkoutExercise(db.Model):
    """
    Join table between Workout and Exercise. Carries the per-workout detail
    (sets/reps/duration) for that exercise, which is what makes the same
    Exercise reusable across many Workouts with different parameters.
    """

    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)

    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)

    # --- Table constraints (2+) ---
    __table_args__ = (
        CheckConstraint("sets IS NULL OR sets > 0", name="ck_we_sets_positive"),
        CheckConstraint("reps IS NULL OR reps > 0", name="ck_we_reps_positive"),
        CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds > 0",
            name="ck_we_duration_positive",
        ),
    )

    workout = db.relationship("Workout", back_populates="exercise_links")
    exercise = db.relationship("Exercise", back_populates="workout_links")

    # --- Model validations (2+) ---
    @validates("sets", "reps")
    def validate_positive(self, key, value):
        if value is not None and value <= 0:
            raise ValueError(f"{key} must be a positive number.")
        return value

    @validates("duration_seconds")
    def validate_duration(self, key, value):
        if value is not None and value <= 0:
            raise ValueError("duration_seconds must be a positive number.")
        # Requires at least one of sets/reps or duration to be meaningful.
        if value is None and not self.sets and not self.reps:
            raise ValueError(
                "A workout exercise needs sets/reps or a duration_seconds."
            )
        return value

    def __repr__(self):
        return f"<WorkoutExercise workout={self.workout_id} exercise={self.exercise_id}>"
