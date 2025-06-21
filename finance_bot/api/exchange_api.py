# finance_bot/api/exchange_api.py
import httpx

async def get_usd_cny() -> float | None:
    async with httpx.AsyncClient() as client:
        res = await client.get("https://api.exchangerate-api.com/v4/latest/USD")
        res.raise_for_status()
        data = res.json()
        return data['rates'].get('CNY')
