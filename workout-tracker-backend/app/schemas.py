from marshmallow import Schema, fields, validate

from app.models import VALID_CATEGORIES


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=80))
    category = fields.Str(
        required=True,
        validate=validate.OneOf(VALID_CATEGORIES),
    )
    equipment_needed = fields.Str(
        required=False, load_default="none", validate=validate.Length(max=80)
    )


class WorkoutExerciseSchema(Schema):
    """Used to nest exercise details inside a Workout, and to validate the
    payload for POST /workouts/<id>/exercises."""

    id = fields.Int(dump_only=True)
    exercise_id = fields.Int(required=True)
    exercise = fields.Nested(ExerciseSchema, dump_only=True)
    sets = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1))
    reps = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1))
    duration_seconds = fields.Int(
        required=False, allow_none=True, validate=validate.Range(min=1)
    )


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=False)
    notes = fields.Str(required=False, allow_none=True, validate=validate.Length(max=255))
    exercise_links = fields.List(
        fields.Nested(WorkoutExerciseSchema), dump_only=True
    )


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

workout_exercise_schema = WorkoutExerciseSchema()
