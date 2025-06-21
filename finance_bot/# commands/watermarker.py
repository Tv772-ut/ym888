# commands/watermarker.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from PIL import Image, ImageDraw, ImageFont
import io
import os

# ===== 1. 加水印主函数 =====
async def add_watermark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("请先发送图片，再用 /水印 [水印文字] 命令。")
        return

    # 获取最大分辨率的图片
    photo_file = await update.message.photo[-1].get_file()
    img_bytes = await photo_file.download_as_bytearray()
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")

    # 获取水印文字
    watermark_text = " ".join(context.args) if context.args else f"@{update.effective_user.username}" or "ym888"
    # 字体与尺寸
    font_path = os.getenv("WATERMARK_FONT_PATH", "arial.ttf")  # 默认arial.ttf, 可替换为实际服务器字体
    font_size = max(20, img.width // 18)
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        font = ImageFont.load_default()

    # 新建透明层加水印
    txt_layer = Image.new('RGBA', img.size, (255,255,255,0))
    draw = ImageDraw.Draw(txt_layer)
    textwidth, textheight = draw.textsize(watermark_text, font=font)
    # 右下角位置
    x = img.width - textwidth - 30
    y = img.height - textheight - 20

    # 半透明白底+黑字
    draw.rectangle([x-8, y-4, x+textwidth+8, y+textheight+4], fill=(255,255,255,128))
    draw.text((x, y), watermark_text, font=font, fill=(0,0,0,196))

    # 合成图片
    watermarked = Image.alpha_composite(img, txt_layer).convert("RGB")
    output = io.BytesIO()
    watermarked.save(output, format='JPEG')
    output.seek(0)

    await update.message.reply_photo(photo=output, caption="✅ 水印已添加")

# ===== 2. 监听图片+命令 =====
def register(app):
    app.add_handler(CommandHandler("水印", add_watermark))
    # 可选：自动监听图片+水印命令的组合
    # app.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex(r'/水印'), add_watermark))
