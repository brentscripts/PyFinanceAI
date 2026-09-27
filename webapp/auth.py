import sqlite3

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash

login_manager = LoginManager()
login_manager.login_view = "auth.login"

auth_bp = Blueprint("auth", __name__)


class User(UserMixin):
    """Thin wrapper around a row in the `users` table.

    Household membership (not per-user data ownership) is what auth gates
    here: every logged-in user of a household sees the same shared
    transactions table, so this class only needs to carry identity, not
    scoping — there's no per-user filtering anywhere else in the app.
    """

    def __init__(self, id, username, household_id):
        self.id = str(id)
        self.username = username
        self.household_id = household_id


def _get_db_connection():
    conn = sqlite3.connect(current_app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


@login_manager.user_loader
def load_user(user_id):
    conn = _get_db_connection()
    row = conn.execute(
        "SELECT id, username, household_id FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return User(row["id"], row["username"], row["household_id"])


@login_manager.unauthorized_handler
def unauthorized():
    # /update/<id> and /api/* are called via fetch() from dashboard.js and
    # editTable.js, not followed as normal navigation, so they need a JSON
    # 401 rather than a redirect the JS never sees.
    if request.path.startswith("/api/") or request.path.startswith("/update/"):
        return jsonify({"success": False, "error": "Authentication required"}), 401
    return redirect(url_for("auth.login", next=request.path))


def _is_safe_next_path(path):
    # Only allow same-site relative paths for the post-login redirect, so a
    # crafted ?next= can't send a logged-in user off to another host.
    return bool(path) and path.startswith("/") and not path.startswith("//")


@auth_bp.route("/login", methods=("GET", "POST"))
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = _get_db_connection()
        row = conn.execute(
            "SELECT id, username, password_hash, household_id FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        conn.close()

        if row is None or not row["password_hash"] or not check_password_hash(row["password_hash"], password):
            error = "Invalid username or password."
        else:
            login_user(User(row["id"], row["username"], row["household_id"]))
            next_path = request.args.get("next") or request.form.get("next")
            if _is_safe_next_path(next_path):
                return redirect(next_path)
            return redirect(url_for("index"))

    return render_template("login.html", error=error, next=request.args.get("next", ""))


@auth_bp.route("/logout", methods=("POST",))
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
