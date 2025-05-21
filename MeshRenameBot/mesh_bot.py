from pyrogram import Client, types
from pyrogram.file_id import FileId

import logging
from MeshRenameBot.config import Config

renamelog = logging.getLogger(__name__)


class MeshRenameBot(Client):
    def __init__(self):
        super().__init__(
            name="MeshRenameBot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN
        )

    async def get_file_id(self, message):
        available_media = (
            "audio", "document", "photo", "sticker", "animation",
            "video", "voice", "video_note", "new_chat_photo",
        )

        if isinstance(message, types.Message):
            for kind in available_media:
                media = getattr(message, kind, None)
                if media is not None:
                    break
            else:
                return None
        else:
            media = message

        file_id_str = media if isinstance(media, str) else media.file_id

        return FileId.decode(file_id_str)

    async def send_track(self, text_mess):
        track_channel = Config.TRACE_CHANNEL
        if track_channel:
            try:
                await self.send_message(track_channel, text_mess)
            except Exception:
                renamelog.exception(
                    "Make sure to enter the Track Channel ID correctly."
                )