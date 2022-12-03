from datetime import datetime
from TeamTeleRoid.database import db
from configs import Config
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Client.on_callback_query(filters.regex(r"^give_access"))
async def give_access_handler(c:Client,query: CallbackQuery):
    try:
        group_id = int(query.data.split("#")[1])
        from_user = int(query.data.split("#")[2])

        group = await db.get_group(group_id)

        if group["has_access"] and await db.is_group_verified(group_id):
            return query.answer("Group already have access", show_alert=True)

        update = await db.update_group(str(group_id).replace("-100", ""), {"has_access": True, "last_verified":datetime.now()})

        txt = await query.edit_message_text(f"Group [{group_id}] has access",)

        return await c.send_message(from_user, f"Your group has been authenticated by Admin. Now you can add your own db channel for {Config.VERIFIED_TIME} days.")
    except Exception as e:
        print(e)

@Client.on_callback_query(filters.regex(r"^dbgive_access"))
async def dbgive_access_handler(c:Client,query: CallbackQuery):
    try:
        from_user = int(query.data.split("#")[2])
        db_channel = int(query.data.split("#")[3])
        group_id = int(query.data.split("#")[1])

        try:

            await db.update_group(str(group_id).replace("-100", ""), {"db_channel":int(db_channel)})
        except Exception as e:
            print(e)

        await query.edit_message_text("DB Channel Verified. Make sure you join the channel")
        return await c.send_message(from_user, f"Your channel {db_channel} has been verified. Bot will search posts from your channel only in your group")
    except Exception as e:
        print(e)

@Client.on_callback_query(filters.regex(r"^dbgive_access"))
async def dbdeny_access_handler(c:Client,query: CallbackQuery):
    from_user = int(query.data.split("#")[1])
    db_channel = int(query.data.split("#")[2])
    await query.edit_message_text("Channel has been rejected successfully")
    return await c.send_message(from_user, f"Your request for channel [`{db_channel}`] has been rejected by Admin")


@Client.on_callback_query(filters.regex(r"^deny_access"))
async def deny_access_handler(c:Client,query: CallbackQuery):
    group_id = int(query.data.split("#")[1])
    from_user = int(query.data.split("#")[2])
    user = await db.get_group(str(group_id))
    await db.update_group(str(group_id), {"has_access": False})
    await query.edit_message_text("Group has been rejected successfully")
    return await c.send_message(from_user, "Your request has been rejected by Admin to add your own db channel")


@Client.on_callback_query(filters.regex(r"^request_access"))
async def request_access_handler(c:Client,query: CallbackQuery):
    group_id = int(query.data.split("#")[1])
    user = await db.get_group(group_id)
    if user["has_access"] and await db.is_group_verified(group_id):
        return await query.message.reply("You already have access to this Bot")
    else: 
        REPLY_MARKUP = InlineKeyboardMarkup([
            [
                InlineKeyboardButton('Allow', callback_data=f'give_access#{query.message.chat.id}#{query.from_user.id}'),
                InlineKeyboardButton('Deny', callback_data=f'deny_access#{query.message.chat.id}#{query.from_user.id}'),
            ],
            [
                
                InlineKeyboardButton('Close', callback_data=f'delete'),
            ],

        ])      

        await c.send_message(Config.LOG_CHANNEL, f"""
#NewRequest
Group ID: {group_id}
Give Access: `/give_access {group_id} no_of_days`
Deny Access: `/deny_access `{group_id}`""", reply_markup=REPLY_MARKUP)

        await query.edit_message_text("Request has been sent to Admin. You will be notified when Admin accepts your request")


@Client.on_callback_query()
async def button(bot, cmd: CallbackQuery):
        cb_data = cmd.data
        if "About_msg" in cb_data:
            await cmd.message.edit(
            text=Config.ABOUT_BOT_TEXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
            InlineKeyboardButton('➕ Add Me To Your Groups ➕', url=f'http://t.me/{Config.BOT_USERNAME}?startgroup=true')
            ],
                    [
                        InlineKeyboardButton("Home", callback_data="gohome"),
                        InlineKeyboardButton("Help", callback_data="Help_msg")
                    ]
                ]
            ),
            parse_mode="html"
        )
        elif "Help_msg" in cb_data:
            await cmd.message.edit(
            text=Config.ABOUT_HELP_TEXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
            InlineKeyboardButton('➕ Add Me To Your Groups ➕', url=f'http://t.me/{Config.BOT_USERNAME}?startgroup=true')
            ], 
                                        [
                        InlineKeyboardButton("About", callback_data="About_msg"),
                        InlineKeyboardButton("Home", callback_data="gohome")
                    ]
                ]
            ),
            parse_mode="html"
        )
        elif "gohome" in cb_data:
            await cmd.message.edit(
            text=Config.HOME_TEXT.format(cmd.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                                       [
            InlineKeyboardButton('➕ Add Me To Your Groups ➕', url=f'http://t.me/{Config.BOT_USERNAME}?startgroup=true')
            ],
                    [
                        InlineKeyboardButton("About", callback_data="About_msg"),
                        InlineKeyboardButton("Help", callback_data="Help_msg")
                    ]
                ]
            ),
            parse_mode="html"
        )

        elif "remove_api" in cb_data:
            _, group_id = cb_data.split("#")
            await db.remove_user_api(int(group_id))
            await cmd.message.edit("Deleted Successfully")
            return
        elif "cancel_removeapi" in cb_data:
            await cmd.message.delete()




