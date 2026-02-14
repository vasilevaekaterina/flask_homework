from flask import Blueprint, request, jsonify, g
from sqlalchemy import select
from app.models import Advertisement
from app.schemas import AdvertisementCreate, AdvertisementUpdate
from pydantic import ValidationError

api_bp = Blueprint("api", __name__)


def get_db():
    return g.db


@api_bp.route("/advertisements", methods=["GET"])
def list_advertisements():
    """Список всех объявлений."""
    db = get_db()
    stmt = select(Advertisement).order_by(Advertisement.created_at.desc())
    ads = db.execute(stmt).scalars().all()
    return jsonify([ad.to_dict() for ad in ads]), 200


@api_bp.route("/advertisements", methods=["POST"])
def create_advertisement():
    """Создание объявления."""
    try:
        data = AdvertisementCreate.model_validate(request.get_json())
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400
    except Exception:
        return jsonify({"error": "Invalid JSON or missing fields"}), 400

    db = get_db()
    ad = Advertisement(
        title=data.title,
        description=data.description,
        owner=data.owner,
    )
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return jsonify(ad.to_dict()), 201


@api_bp.route("/advertisements/<int:ad_id>", methods=["GET"])
def get_advertisement(ad_id):
    """Получение объявления по id."""
    db = get_db()
    ad = db.get(Advertisement, ad_id)
    if ad is None:
        return jsonify({"error": "Advertisement not found"}), 404
    return jsonify(ad.to_dict()), 200


@api_bp.route("/advertisements/<int:ad_id>", methods=["DELETE"])
def delete_advertisement(ad_id):
    """Удаление объявления."""
    db = get_db()
    ad = db.get(Advertisement, ad_id)
    if ad is None:
        return jsonify({"error": "Advertisement not found"}), 404
    db.delete(ad)
    db.commit()
    return "", 204


@api_bp.route("/advertisements/<int:ad_id>", methods=["PUT"])
def update_advertisement(ad_id):
    """Редактирование объявления."""
    db = get_db()
    ad = db.get(Advertisement, ad_id)
    if ad is None:
        return jsonify({"error": "Advertisement not found"}), 404
    try:
        data = AdvertisementUpdate.model_validate(request.get_json())
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    payload = data.model_dump(exclude_unset=True)
    for key, value in payload.items():
        setattr(ad, key, value)
    db.commit()
    db.refresh(ad)
    return jsonify(ad.to_dict()), 200
