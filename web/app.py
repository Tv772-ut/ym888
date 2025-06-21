# ym888/web/app.py
from flask import Flask, render_template
from models import AccountRecord
from db import get_db

app = Flask(__name__)

@app.route("/")
def index():
    db = next(get_db())
    records = db.query(AccountRecord).order_by(AccountRecord.created_at.desc()).limit(100).all()
    return render_template("bill.html", records=records)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
