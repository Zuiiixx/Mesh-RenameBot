import logging
import asyncio
import math
import time
from pyrogram import StopTransmission
from .human_format import human_readable_bytes, human_readable_timedelta
from ..core.get_config import get_var
from ..maneuvers.ExecutorManager import ExecutorManager

renamelog = logging.getLogger(__name__)


async def progress_for_pyrogram(
    current,
    total,
    ud_type,
    message,
    start,
    time_out,
    client,
    uid,
    markup=None
):
    now = time.time()
    diff = now - start
    
    # too early to update the progress
    if diff < 1:
        return
    eo = ExecutorManager()
    if uid in eo.canceled_uids:
        raise StopTransmission()

    if round(diff % time_out) == 0 or current == total:
    
        # if round(current / total * 100, 0) % 5 == 0:
        percentage = current * 100 / total
        elapsed_time = round(diff)
        speed = current / elapsed_time
        time_to_completion = round((total - current) / speed)
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = human_readable_timedelta(elapsed_time)
        estimated_total_time = human_readable_timedelta(estimated_total_time)

        progress = "[{0}{1}] \nP: {2}%\n".format(
            ''.join([get_var("COMPLETED_STR") for _ in range(math.floor(percentage / 10))]),
            ''.join([get_var("REMAINING_STR") for _ in range(10 - math.floor(percentage / 10))]),
            round(percentage, 2))

        tmp = progress + "{0} of {1}\nSpeed: {2}/s\nETA: {3}\n".format(
            human_readable_bytes(current),
            human_readable_bytes(total),
            human_readable_bytes(speed),
            estimated_total_time if estimated_total_time != '' else "0 seconds"
        )
        try:
            if not message.photo:
                await message.edit_text(
                    text="{}\n {}".format(
                        ud_type,
                        tmp
                    ),
                    reply_markup=markup
                )
            else:
                await message.edit_caption(
                    caption="{}\n {}".format(
                        ud_type,
                        tmp
                    ),
                    reply_markup=markup
                )
            await asyncio.sleep(1)
        except:
            pass