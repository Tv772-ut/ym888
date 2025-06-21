# app.py

from flask import Flask, request, jsonify, render_template, redirect, url_for
from models import db, Bill, User
import datetime

app = Flask(__name__)

# 配置数据库（如已在models.py配置可省略）
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bills.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

# 首页：账单列表
@app.route('/')
def index():
    bills = Bill.query.order_by(Bill.created_at.desc()).limit(50).all()
    return render_template('index.html', bills=bills)

# 新增账单页面
@app.route('/add', methods=['GET', 'POST'])
def add_bill():
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        remark = request.form.get('remark', '')
        currency = request.form.get('currency', 'CNY')
        user_id = int(request.form.get('user_id', 1))
        bill = Bill(
            amount=amount,
            remark=remark,
            currency=currency,
            user_id=user_id,
            created_at=datetime.datetime.utcnow()
        )
        db.session.add(bill)
        db.session.commit()
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('add.html', users=users)

# 编辑账单
@app.route('/edit/<int:bill_id>', methods=['GET', 'POST'])
def edit_bill(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    if request.method == 'POST':
        bill.amount = float(request.form.get('amount'))
        bill.remark = request.form.get('remark', '')
        bill.currency = request.form.get('currency', 'CNY')
        db.session.commit()
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('edit.html', bill=bill, users=users)

# 删除账单
@app.route('/delete/<int:bill_id>', methods=['POST'])
def delete_bill(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    db.session.delete(bill)
    db.session.commit()
    return redirect(url_for('index'))

# 账单API列表
@app.route('/api/bills')
def api_bills():
    bills = Bill.query.order_by(Bill.created_at.desc()).limit(100).all()
    return jsonify([
        {
            "id": b.id,
            "amount": b.amount,
            "remark": b.remark,
            "currency": b.currency,
            "created_at": b.created_at.isoformat(),
            "user_id": b.user_id
        } for b in bills
    ])

# 账单API详情
@app.route('/api/bill/<int:bill_id>')
def api_bill_detail(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    return jsonify({
        "id": bill.id,
        "amount": bill.amount,
        "remark": bill.remark,
        "currency": bill.currency,
        "created_at": bill.created_at.isoformat(),
        "user_id": bill.user_id
    })

# 用户账单API
@app.route('/api/user/<int:user_id>/bills')
def api_user_bills(user_id):
    bills = Bill.query.filter_by(user_id=user_id).order_by(Bill.created_at.desc()).all()
    return jsonify([
        {
            "id": b.id,
            "amount": b.amount,
            "remark": b.remark,
            "currency": b.currency,
            "created_at": b.created_at.isoformat(),
            "user_id": b.user_id
        } for b in bills
    ])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
