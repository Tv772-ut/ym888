from telegram import Update
from telegram.ext import ContextTypes
from PIL import Image, ImageDraw, ImageFont
import io

async def watermark_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 简单水印功能演示
    if not update.message.photo:
        await update.message.reply_text("请发送一张图片。")
        return
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    image = Image.open(io.BytesIO(photo_bytes))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((10, 10), "ym888", fill=(255, 0, 0), font=font)
    output = io.BytesIO()
    image.save(output, format='PNG')
    output.seek(0)
    await update.message.reply_photo(photo=output, caption="已加水印")
