from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Save(db.Model):
    """Represents a single save file upload."""
    __tablename__ = "saves"

    id = db.Column(db.Integer, primary_key=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    fish_snapshots = db.relationship("FishSnapshot", backref="save", lazy=True)
    recipe_snapshots = db.relationship("RecipeSnapshot", backref="save", lazy=True)

    def __repr__(self):
        return f"<Save id={self.id} uploaded_at={self.uploaded_at}>"


class FishSnapshot(db.Model):
    """Records which fish were caught at the time of a given upload."""
    __tablename__ = "fish_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    save_id = db.Column(db.Integer, db.ForeignKey("saves.id"), nullable=False)
    fish_id = db.Column(db.String(64), nullable=False)
    fish_name = db.Column(db.String(128), nullable=False)
    caught = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"<FishSnapshot fish_name={self.fish_name} caught={self.caught}>"


class RecipeSnapshot(db.Model):
    """Records which recipes were learned/cooked at the time of a given upload."""
    __tablename__ = "recipe_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    save_id = db.Column(db.Integer, db.ForeignKey("saves.id"), nullable=False)
    recipe_name = db.Column(db.String(128), nullable=False)
    learned = db.Column(db.Boolean, nullable=False)
    cooked = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"<RecipeSnapshot recipe_name={self.recipe_name} cooked={self.cooked}>"
