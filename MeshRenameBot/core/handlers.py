from os import rename
from MeshRenameBot.core.get_config import get_var
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, UsernameNotOccupied
import re
import logging
import signal
import asyncio
import time

from ..maneuvers.ExecutorManager import ExecutorManager
from ..maneuvers.Rename import RenameManeuver
from ..utils.c_filter import filter_controller, filter_interact
from ..utils.user_input import interactive_input
from .thumb_manage import handle_set_thumb, handle_get_thumb, handle_clr_thumb
from .mode_select import upload_mode, mode_callback
from ..config import Commands
from ..translations import Translator
from ..database.user_db import UserDB
from .caption_manage import set_caption, del_caption
from ..mesh_bot import MeshRenameBot
from .change_locale import change_locale, set_locale

# Temp file sequence memory
user_file_sequences = {}
sequence_timeout = 3600  # 1 hour


renamelog = logging.getLogger(__name__)


def add_handlers(client: MeshRenameBot) -> None:

    client.add_handler(MessageHandler(collect_sequence_files, filters.document | filters.video | filters.audio | filters.photo))
   
    client.add_handler(MessageHandler(rename_handler, filters.regex(Commands.RENAME, re.IGNORECASE)))
    client.add_handler(MessageHandler(
        rename_handler,
        filters.document | filters.video | filters.audio | filters.photo,
    ))
    
    client.add_handler(MessageHandler(interactive_input))
    client.add_handler(MessageHandler(start_handler, filters.command("start")))
    
    client.add_handler(MessageHandler(filter_controller, filters.regex(Commands.FILTERS, re.IGNORECASE)))
    client.add_handler(MessageHandler(handle_set_thumb, filters.regex(Commands.SET_THUMB, re.IGNORECASE)))
    client.add_handler(MessageHandler(handle_get_thumb, filters.regex(Commands.GET_THUMB, re.IGNORECASE)))
    client.add_handler(MessageHandler(handle_clr_thumb, filters.regex(Commands.CLR_THUMB, re.IGNORECASE)))
    client.add_handler(MessageHandler(handle_queue, filters.regex(Commands.QUEUE, re.IGNORECASE)))
    client.add_handler(MessageHandler(upload_mode, filters.regex(Commands.MODE, re.IGNORECASE)))
    client.add_handler(MessageHandler(help_handler, filters.regex(Commands.HELP, re.IGNORECASE)))
    client.add_handler(MessageHandler(start_sequence_handler, filters.command("startsequence")))

    client.add_handler(MessageHandler(end_sequence_handler, filters.command("endsequence")))
    client.add_handler(MessageHandler(set_caption, filters.regex(Commands.SET_CAPTION, re.IGNORECASE)))
    client.add_handler(MessageHandler(intercept_handler))
    client.add_handler(MessageHandler(change_locale, filters.regex(Commands.SET_LANG, re.IGNORECASE)))
    client.add_handler(CallbackQueryHandler(cancel_this, filters.regex("cancel", re.IGNORECASE)))
    client.add_handler(CallbackQueryHandler(filter_interact, filters.regex("fltr", re.IGNORECASE)))
    client.add_handler(CallbackQueryHandler(mode_callback, filters.regex(r"(mode|command_mode)", re.IGNORECASE)))
    client.add_handler(CallbackQueryHandler(close_message, filters.regex("close", re.IGNORECASE)))
    client.add_handler(CallbackQueryHandler(del_caption, filters.regex("delcaption", re.IGNORECASE)))
    client.add_handler(CallbackQueryHandler(set_locale, filters.regex("set_locale", re.IGNORECASE)))
    

    try:
        signal.signal(signal.SIGINT, term_handler)
        signal.signal(signal.SIGTERM, term_handler)
    except Exception as e:
        renamelog.warning(f"Signal handling setup failed: {e}")


START_PIC = "AgACAgUAAxkBAAPBaDAjpU3TG9GXV-i08l914m2xAAHtAAKAwjEbdX6AVeBhi8MzD_xKAQADAgADeAADNgQ"

async def start_handler(_, msg: Message) -> None:
    user_locale = UserDB().get_var("locale", msg.from_user.id) or "en"
    caption = Translator(user_locale).get("START_MSG")

    await msg.reply_photo(
        photo=START_PIC,
        caption=caption
    )


async def start_sequence_handler(_: MeshRenameBot, msg: Message) -> None:
    user_id = msg.from_user.id
    user_file_sequences[user_id] = {"files": [], "time": time.time()}
    user_locale = UserDB().get_var("locale", user_id) or "en"
    await msg.reply_text(Translator(user_locale).get("SEQUENCE_STARTED"), quote=True)


async def rename_handler(client: MeshRenameBot, msg: Message) -> None:
    command_mode = UserDB().get_var("command_mode", msg.from_user.id)
    user_locale = UserDB().get_var("locale", msg.from_user.id) or "en"
    translator = Translator(user_locale)

    if command_mode == UserDB.MODE_RENAME_WITHOUT_COMMAND:
        if msg.media is None:
            return
        rep_msg = msg
    else:
        if msg.media:
            return
        rep_msg = msg.reply_to_message

    if rep_msg is None:
        await msg.reply_text(translator.get("REPLY_TO_MEDIA"), quote=True)
        return

    if msg.from_user.id in user_file_sequences:
        await msg.reply_text("You are in bulk rename mode. Just send files, no need to use /rename.")
        return

    file_id = await client.get_file_id(rep_msg)
    if file_id is not None:
        await msg.reply_text(
            translator.get(
                "RENAME_ADDED_TO_QUEUE", dc_id=file_id.dc_id, media_id=file_id.media_id
            ),
            quote=True,
        )

    await client.send_track(
        translator.get(
            "TRACK_MESSAGE_ADDED_RENAME",
            username=msg.from_user.username,
            name=msg.from_user.first_name,
            user_id=msg.from_user.id,
        )
    )
    await asyncio.sleep(2)
    await ExecutorManager().create_maneuver(RenameManeuver(client, rep_msg, msg))


async def help_handler(_: MeshRenameBot, msg: Message) -> None:
    user_locale = UserDB().get_var("locale", msg.from_user.id) or "en"
    await msg.reply_text(
        Translator(user_locale).get(
            "HELP_STR",
            startcmd=Commands.START,
            renamecmd=Commands.RENAME,
            filterscmd=Commands.FILTERS,
            setthumbcmd=Commands.SET_THUMB,
            getthumbcmd=Commands.GET_THUMB,
            clrthumbcmd=Commands.CLR_THUMB,
            modecmd=Commands.MODE,
            queuecmd=Commands.QUEUE,
            setcaptioncmd=Commands.SET_CAPTION,
            helpcmd=Commands.HELP,
            setlanguagecmd=Commands.SET_LANG,
        ),
        quote=True,
    )


def term_handler(signum: int, frame: int) -> None:
    ExecutorManager().stop()


async def cancel_this(_: MeshRenameBot, msg: CallbackQuery) -> None:
    try:
        task_id = int(str(msg.data).split(" ")[1])
        ExecutorManager().canceled_uids.append(task_id)
        user_locale = UserDB().get_var("locale", msg.from_user.id) or "en"
        await msg.answer(Translator(user_locale).get("CANCEL_MESSAGE"), show_alert=True)
    except Exception:
        await msg.answer("Invalid cancel request.", show_alert=True)


async def handle_queue(_: MeshRenameBot, msg: Message) -> None:
    EM = ExecutorManager()
    user_id = msg.from_user.id
    user_locale = UserDB().get_var("locale", user_id) or "en"
    translator = Translator(user_locale)

    pending = sum(1 for i in EM.all_maneuvers_log if i.is_pending)
    executing = sum(1 for i in EM.all_maneuvers_log if i.is_executing)
    from_id = msg.from_user.id
    max_size = get_var("MAX_QUEUE_SIZE")

    fmsg = translator.get(
        "RENAME_QUEUE_STATUS",
        total_tasks=pending,
        queue_capacity=max_size,
        current_task=executing,
    )

    task_num = 1
    for i in EM.all_maneuvers_log:
        if i.sender_id == from_id:
            fmsg += translator.get(
                "RENAME_QUEUE_USER_STATUS",
                is_executing=i.is_executing,
                is_pending=i.is_pending,
                task_id=i._unique_id,
                task_number=task_num,
            )
        if i.is_pending:
            task_num += 1

    await msg.reply_text(fmsg)


async def intercept_handler(client: Client, msg: Message) -> None:
    if not msg.from_user:
        return

    user_id = msg.from_user.id
    user_locale = UserDB().get_var("locale", user_id) or "en"
    translator = Translator(user_locale)

    if get_var("FORCEJOIN") != "":
        try:
            user_state = await client.get_chat_member(get_var("FORCEJOIN_ID"), user_id)
            if user_state.status == "kicked":
                await msg.reply_text(translator.get("USER_KICKED"), quote=True)
                return
        except UserNotParticipant:
            forcejoin = get_var("FORCEJOIN")
            await msg.reply_text(
                translator.get("USER_NOT_PARTICIPANT"),
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(translator.get("JOIN_CHANNEL"), url=forcejoin)]]
                ),
            )
            return
        except ChatAdminRequired:
            renamelog.error("Bot must be admin in FORCEJOIN target group/channel.")
            return
        except UsernameNotOccupied:
            renamelog.error("Invalid FORCEJOIN ID.")
            return
        except Exception:
            renamelog.exception("Unhandled error in FORCEJOIN check.")
            return

    await msg.continue_propagation()


async def close_message(_: MeshRenameBot, msg: CallbackQuery) -> None:
    if msg.message.reply_to_message is not None:
        await msg.message.reply_to_message.delete()
    await msg.message.delete()


async def end_sequence_handler(client: MeshRenameBot, msg: Message):
    user_id = msg.from_user.id
    user_locale = UserDB().get_var("locale", user_id) or "en"
    translator = Translator(user_locale)

    if user_id not in user_file_sequences or not user_file_sequences[user_id]["files"]:
        await msg.reply_text("No files found in sequence.")
        return

    await msg.reply_text("Bulk renaming started...")

    for media_msg in user_file_sequences[user_id]["files"]:
        await ExecutorManager().create_maneuver(RenameManeuver(client, media_msg, media_msg))
        await asyncio.sleep(2)

    del user_file_sequences[user_id]
    await msg.reply_text("Sequence complete. All files added to rename queue.")


async def collect_sequence_files(client: MeshRenameBot, msg: Message):
    user_id = msg.from_user.id
    current_time = time.time()

    if user_id not in user_file_sequences:
        return await msg.continue_propagation()

    if current_time - user_file_sequences[user_id]["time"] > sequence_timeout:
        del user_file_sequences[user_id]
        await msg.reply_text("Sequence expired. Please start again with /startsequence.")
        return await msg.continue_propagation()
    user_file_sequences[user_id]["files"].append(msg)
    user_file_sequences[user_id]["time"] = current_time
    await msg.reply_text("File added to sequence.")