import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant
from configs import Config

from pyrogram.types import Message


# @Client.on_message(filters.private & filters.incoming)
async def forcesub(c:Client, m:Message):
    owner = await c.get_users(int(Config.BOT_OWNER))
    if Config.FORCE_SUB:
        try:
            user = await c.get_chat_member(Config.UPDATES_CHANNEL_USERNAME, m.from_user.id)
            if user.status == "kicked":
               await m.reply_text("**Hey you are banned 😜**", quote=True)
               return
        except UserNotParticipant:
            buttons = [[InlineKeyboardButton(text='Updates Channel 🔖', url=f"https://t.me/{Config.UPDATES_CHANNEL_USERNAME}")]]
            if m.text:
                if (len(m.text.split()) > 1) & ('start' in m.text):
                    decoded_data = await decode(m.text.split()[1])
                    chat_id, msg_id = decoded_data.split('_')
                    buttons.append([InlineKeyboardButton('🔄 Refresh', callback_data=f'refresh+{chat_id}+{msg_id}')])
            await m.reply_text(
                f"Hey {m.from_user.mention(style='md')} you need join My updates channel in order to use me 😉\n\n"
                "__Press the Following Button to join Now 👇__",
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
            )
            
            return
        except Exception as e:
            print(e)
            await m.reply_text(f"Something Wrong. Please try again later or contact {owner.mention(style='md')}", quote=True)
            return

    await m.continue_propagation()


@Client.on_callback_query(filters.regex('^refresh'))
async def refresh_cb(c, m):
    UPDATE_CHANNEL = Config.UPDATES_CHANNEL_USERNAME
    OWNER_ID = Config.BOT_OWNER
    owner = await c.get_users(int(OWNER_ID))
    # Checking if the FORCE_SUB is enabled or not.
    if Config.FORCE_SUB:
        try:
            user = await c.get_chat_member(UPDATE_CHANNEL, m.from_user.id)
            if user.status == "kicked":
               try:
                   await m.message.edit("**Hey you are banned 😜**")
               except:
                   pass
               return
        except UserNotParticipant:
            await m.answer('You are not yet joined our channel. First join and then press refresh button 🤤', show_alert=True)
            return
        except Exception as e:
            print(e)
            await m.message.edit(f"Something Wrong. Please try again later or contact {owner.mention(style='md')}")
            return        
    await m.message.delete()

import base64
async def decode(base64_string):
    base64_bytes = base64_string.encode("ascii")
    string_bytes = base64.b64decode(base64_bytes) 
    string = string_bytes.decode("ascii")
    return string