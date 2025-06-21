# finance_bot/web/app.py
from flask import Flask, render_template
from finance_bot.db import async_session
from finance_bot.models import AccountEntry
import asyncio

app = Flask(__name__)

@app.route('/')
def index():
    # Flask本身不支持async视图，这里演示用同步阻塞
    async def get_entries():
        async with async_session() as session:
            result = await session.execute(
                AccountEntry.__table__.select().order_by(AccountEntry.created_at.desc())
            )
            return result.scalars().all()

    entries = asyncio.run(get_entries())
    return render_template('bill.html', entries=entries)
