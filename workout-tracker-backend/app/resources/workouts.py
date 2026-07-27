from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Exercise, Workout, WorkoutExercise
from app.schemas import (
    workout_exercise_schema,
    workout_schema,
    workouts_schema,
)

workouts_bp = Blueprint("workouts", __name__, url_prefix="/workouts")


@workouts_bp.get("")
def list_workouts():
    workouts = Workout.query.all()
    return jsonify(workouts_schema.dump(workouts)), 200


@workouts_bp.get("/<int:workout_id>")
def get_workout(workout_id):
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return jsonify({"error": "Workout not found"}), 404
    return jsonify(workout_schema.dump(workout)), 200


@workouts_bp.post("")
def create_workout():
    json_data = request.get_json(silent=True) or {}
    try:
        data = workout_schema.load(json_data, partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    workout = Workout(**data)
    try:
        db.session.add(workout)
        db.session.commit()
    except (IntegrityError, ValueError) as err:
        db.session.rollback()
        return jsonify({"error": str(err.orig) if hasattr(err, "orig") else str(err)}), 400

    return jsonify(workout_schema.dump(workout)), 201


@workouts_bp.delete("/<int:workout_id>")
def delete_workout(workout_id):
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return jsonify({"error": "Workout not found"}), 404

    db.session.delete(workout)
    db.session.commit()
    return "", 204


@workouts_bp.post("/<int:workout_id>/exercises")
def add_exercise_to_workout(workout_id):
    """Attach an existing Exercise to a Workout, with sets/reps/duration."""
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return jsonify({"error": "Workout not found"}), 404

    json_data = request.get_json(silent=True) or {}
    try:
        data = workout_exercise_schema.load(json_data, partial=("exercise",))
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    exercise = db.session.get(Exercise, data.get("exercise_id"))
    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404

    link = WorkoutExercise(
        workout_id=workout.id,
        exercise_id=exercise.id,
        sets=data.get("sets"),
        reps=data.get("reps"),
        duration_seconds=data.get("duration_seconds"),
    )

    try:
        db.session.add(link)
        db.session.commit()
    except (IntegrityError, ValueError) as err:
        db.session.rollback()
        return jsonify({"error": str(err.orig) if hasattr(err, "orig") else str(err)}), 400

    return jsonify(workout_schema.dump(workout)), 201
