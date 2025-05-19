# handlers/bulk_rename.py

from pyrogram import Client, filters
from pyrogram.types import Message
from core.temp_store import user_file_sequences

@Client.on_message(filters.command("startsequence"))
async def start_sequence(client, message: Message):
    user_id = message.from_user.id
    user_file_sequences[user_id] = {
        "files": []
    }
    await message.reply_text("Sequence mode started. Send your files now.")

@Client.on_message(filters.command("endsequence"))
async def end_sequence(client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_file_sequences or not user_file_sequences[user_id]["files"]:
        await message.reply_text("No files found in sequence.")
        return

    files = user_file_sequences[user_id]["files"]

    for index, msg in enumerate(files, start=1):
        file_name = f"File_{index}"  # Customize this logic
        await message.reply_text(f"Will rename {msg.document.file_name} to {file_name}")

    del user_file_sequences[user_id]
    await message.reply_text("Sequence completed and cleared.")
