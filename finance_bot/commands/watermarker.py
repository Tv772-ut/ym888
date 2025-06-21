# finance_bot/commands/watermarker.py

from telegram import Update, InputFile
from telegram.ext import ContextTypes
from PIL import Image, ImageDraw, ImageFont
import io
import asyncio

WATERMARK_TEXT = "高级水印"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # 可替换为你服务器上的字体路径
FONT_SIZE = 48
ALPHA = 128  # 水印透明度

async def add_text_watermark(image_bytes: bytes, text: str = WATERMARK_TEXT) -> bytes:
    # 异步包装
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _add_text_watermark_sync, image_bytes, text)

def _add_text_watermark_sync(image_bytes: bytes, text: str) -> bytes:
    with Image.open(io.BytesIO(image_bytes)).convert("RGBA") as base:
        txt_layer = Image.new("RGBA", base.size, (255,255,255,0))
        draw = ImageDraw.Draw(txt_layer)
        try:
            font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        except Exception:
            font = ImageFont.load_default()
        textwidth, textheight = draw.textsize(text, font=font)
        x = base.width - textwidth - 30
        y = base.height - textheight - 30
        draw.text((x, y), text, font=font, fill=(255,255,255,ALPHA))
        watermarked = Image.alpha_composite(base, txt_layer)
        output = io.BytesIO()
        watermarked.convert("RGB").save(output, format="JPEG")
        output.seek(0)
        return output.read()

async def watermark_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text("请对一张图片回复本命令以添加水印。")
        return

    photo = update.message.reply_to_message.photo[-1]
    photo_file = await photo.get_file()
    photo_bytes = await photo_file.download_as_bytearray()

    watermarked_bytes = await add_text_watermark(photo_bytes)
    await update.message.reply_photo(photo=InputFile(io.BytesIO(watermarked_bytes), filename="watermarked.jpg"))
    await update.message.reply_text("✅ 水印已添加！")

# 可选：注册命令
# 在 bot.py 里加
# application.add_handler(CommandHandler("watermark", watermarker.watermark_command))
