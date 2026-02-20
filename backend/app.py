import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from save_parser import analyze_save_file
from models import db, Save, FishSnapshot, RecipeSnapshot

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xml', 'txt', ''}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


def allowed_file(filename: str) -> bool:
    """Check if file has no extension or is xml/txt (save files often have no extension)."""
    if '.' not in filename:
        return True
    return filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_snapshot(result: dict) -> Save:
    """Persist analysis results to the database and return the new Save record."""
    save = Save()
    db.session.add(save)
    db.session.flush()  # get save.id before committing

    # Fish snapshots — one row per fish species
    for fish in result["fish"].get("caughtList", []):
        db.session.add(FishSnapshot(
            save_id=save.id,
            fish_id=fish["id"],
            fish_name=fish["name"],
            caught=True
        ))

    for fish in result["fish"]["missingList"]:
        db.session.add(FishSnapshot(
            save_id=save.id,
            fish_id=fish["id"],
            fish_name=fish["name"],
            caught=False
        ))

    # Recipe snapshots — one row per recipe
    for recipe in result["recipes"].get("cookedList", []):
        db.session.add(RecipeSnapshot(
            save_id=save.id,
            recipe_name=recipe["name"],
            learned=True,
            cooked=True
        ))

    for recipe in result["recipes"]["missingList"]:
        db.session.add(RecipeSnapshot(
            save_id=save.id,
            recipe_name=recipe["name"],
            learned=not recipe["needToLearn"],
            cooked=False
        ))

    db.session.commit()
    return save


def compute_diff(current_save: Save) -> dict | None:
    """
    Compare the current save snapshot against the previous one.
    Returns newly caught fish and newly cooked recipes, or None if this is
    the first upload.
    """
    previous_save = (
        Save.query
        .filter(Save.id < current_save.id)
        .order_by(Save.id.desc())
        .first()
    )

    if previous_save is None:
        return None

    # Fish diff
    prev_caught = {s.fish_id for s in previous_save.fish_snapshots if s.caught}
    curr_caught = {s.fish_id for s in current_save.fish_snapshots if s.caught}
    newly_caught_ids = curr_caught - prev_caught
    newly_caught = [
        {"id": s.fish_id, "name": s.fish_name}
        for s in current_save.fish_snapshots
        if s.fish_id in newly_caught_ids
    ]

    # Recipe diff
    prev_cooked = {s.recipe_name for s in previous_save.recipe_snapshots if s.cooked}
    curr_cooked = {s.recipe_name for s in current_save.recipe_snapshots if s.cooked}
    newly_cooked = [{"name": n} for n in sorted(curr_cooked - prev_cooked)]

    return {
        "previousUploadAt": previous_save.uploaded_at.isoformat(),
        "newlyCaughtFish": newly_caught,
        "newlyCookedRecipes": newly_cooked,
    }


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze an uploaded save file, persist a snapshot, and return results with progress diff."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Please upload a Stardew Valley save file."}), 400

    filepath = None  # initialize before try so except block can always reference it safely
    try:
        filename = secure_filename(file.filename) or 'save_file'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        result = analyze_save_file(filepath)
        os.remove(filepath)

        current_save = save_snapshot(result)
        diff = compute_diff(current_save)

        return jsonify({**result, "progressSince": diff})

    except Exception as e:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": f"Failed to analyze save file: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
