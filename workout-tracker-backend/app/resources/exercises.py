from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Exercise
from app.schemas import exercise_schema, exercises_schema

exercises_bp = Blueprint("exercises", __name__, url_prefix="/exercises")


@exercises_bp.get("")
def list_exercises():
    exercises = Exercise.query.all()
    return jsonify(exercises_schema.dump(exercises)), 200


@exercises_bp.get("/<int:exercise_id>")
def get_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404
    return jsonify(exercise_schema.dump(exercise)), 200


@exercises_bp.post("")
def create_exercise():
    json_data = request.get_json(silent=True) or {}
    try:
        data = exercise_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    exercise = Exercise(**data)
    try:
        db.session.add(exercise)
        db.session.commit()
    except (IntegrityError, ValueError) as err:
        db.session.rollback()
        return jsonify({"error": str(err.orig) if hasattr(err, "orig") else str(err)}), 400

    return jsonify(exercise_schema.dump(exercise)), 201


@exercises_bp.delete("/<int:exercise_id>")
def delete_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404

    db.session.delete(exercise)
    db.session.commit()
    return "", 204
