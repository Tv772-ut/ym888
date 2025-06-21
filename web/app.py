from flask import Flask, render_template, request, jsonify
from models import AccountRecord
from db import get_db

app = Flask(__name__)

# 分页账单展示+筛选
@app.route("/")
def index():
    db = next(get_db())
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    user_id = request.args.get('user_id')
    group_id = request.args.get('group_id')
    category = request.args.get('category')
    q = db.query(AccountRecord)
    # 可选筛选条件
    if user_id:
        q = q.filter(AccountRecord.user_id == user_id)
    if group_id:
        q = q.filter(AccountRecord.group_id == group_id)
    if category:
        q = q.filter(AccountRecord.category == category)
    total = q.count()
    records = q.order_by(AccountRecord.created_at.desc()).offset((page-1)*per_page).limit(per_page).all()

    return render_template(
        "bill.html",
        records=records,
        page=page,
        per_page=per_page,
        total=total,
        user_id=user_id or "",
        group_id=group_id or "",
        category=category or ""
    )

# 支持API方式获取账单（RESTful风格，方便前端/小程序等调用）
@app.route("/api/bills")
def api_bills():
    db = next(get_db())
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    q = db.query(AccountRecord)
    total = q.count()
    records = q.order_by(AccountRecord.created_at.desc()).offset((page-1)*per_page).limit(per_page).all()
    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "data": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "group_id": r.group_id,
                "amount": r.amount,
                "category": r.category,
                "note": r.note,
                "created_at": r.created_at.isoformat()
            } for r in records
        ]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
