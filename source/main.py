import data as data
from data import usersDict
import random
import telebot
from telebot import types

bot = telebot.TeleBot('Token')


@bot.message_handler(commands=['start'])
def start(message):
    kb = types.InlineKeyboardMarkup()
    if message.from_user.id in usersDict.keys():
        btn_profile = types.InlineKeyboardButton(text='Check my profile', callback_data='check_profile')
        kb.add(btn_profile)
        bot.send_message(message.chat.id, 'You already have a profile here', parse_mode='html', reply_markup=kb)
        return
    hello_message = f'Hello, <b>{message.from_user.first_name}</b>! \n' \
                    f'I will help you to find new friends! Register to start ;)'
    btn_register = types.InlineKeyboardButton(text='Register', callback_data='reg')
    kb.add(btn_register)

    bot.send_message(message.chat.id, hello_message, parse_mode='html', reply_markup=kb)


@bot.message_handler(commands=['help'])
def help_bot(message):
    help_txt = f'<b>Hi there!</b>\n' \
               f'I am a bot which is going to help you to make new friends!\n' \
               f'Before we begin make sure that you have a profile. In other case create it by command /start\n\n' \
               f'You can here:\n' \
               f'1) Check your profile: /check_profile \n' \
               f'2) Edit your profile: /check_profile -> press button "Edit"\n' \
               f'3) Find a new friend: /check_profile -> press button "Find a new friend"\n' \
               f'3.1) Send friend-request: press button "🤝 friend request"\n' \
               f'3.2) Check next profile: press button "👎 next"\n' \
               f'4) You can find contacts of all your friends: /friend-list\n' \
               f'5) You check current status of your friend-requests: /requested_list\n\n' \
               f'If you send a friend-request recipient will be notified and able to send a reply\n' \
               f'If you received a friend-request senders profile will be shown to you next in "Find a new friend" section\n' \
               f'If you accept a friend-request then I will send you both contacts of each other'
    bot.send_message(message.chat.id, help_txt, parse_mode='html')


####################################################################################################################
#                                           PROFILE
####################################################################################################################

@bot.callback_query_handler(func=lambda callback: callback.data == 'reg')
def registration(callback):
    user = data.User()
    user.id = callback.from_user.id
    user.username = callback.from_user.username
    user.chat_id = callback.message.chat.id
    user.status = 'registering'
    usersDict[user.id] = user
    profile_edit(callback)


@bot.callback_query_handler(func=lambda callback: callback.data == 'profile_edit')
def profile_edit(callback):
    sent = bot.send_message(callback.message.chat.id, "What's your name?")
    bot.register_next_step_handler(sent, SetName)


def SetName(message):
    data.usersDict[message.from_user.id].name = message.text
    sent = bot.send_message(message.chat.id, "How old are you?")
    bot.register_next_step_handler(sent, SetAge)


def SetAge(message):
    data.usersDict[message.from_user.id].age = message.text
    sent = bot.send_message(message.chat.id, "Tell about yourself:")
    bot.register_next_step_handler(sent, SetDescription)


def SetDescription(message):
    data.usersDict[message.from_user.id].description = message.text
    sent = bot.send_message(message.chat.id, "Last step, waiting for your photo:")
    bot.register_next_step_handler(sent, SetPhoto)


def SetPhoto(message):
    if message.content_type != 'photo':
        sent = bot.send_message(message.chat.id, "Ooops, it doesn't seem as a photo...\nTry again")
        bot.register_next_step_handler(sent, SetPhoto)
        return

    data.usersDict[message.from_user.id].photo = message.photo[0].file_id

    kb = types.InlineKeyboardMarkup()
    btn_profile = types.InlineKeyboardButton(text='Check my profile', callback_data='check_profile')
    kb.add(btn_profile)

    bot.send_message(message.chat.id, "<b>Well done!</b>\nYour profile has been completed!", reply_markup=kb,
                     parse_mode='html')


####################################################################################################################
#                                           PROFILE
####################################################################################################################


def checkIfRegistered(user_id, chat_id=None):
    if user_id in usersDict.keys():
        return True

    kb = types.InlineKeyboardMarkup()
    btn_register = types.InlineKeyboardButton(text='Register', callback_data='reg')
    kb.add(btn_register)
    bot.send_message(chat_id, 'Before checking friend-list create a profile', reply_markup=kb)
    return False


@bot.message_handler(commands=['check_profile'])
def profile_message(message):
    kb = types.InlineKeyboardMarkup(row_width=1)
    if message.from_user.id not in usersDict.keys():
        btn_register = types.InlineKeyboardButton(text='Register', callback_data='reg')
        kb.add(btn_register)
        bot.send_message(message.chat.id, 'Before checking your profile create it', reply_markup=kb)
        return

    btn_pr_edit = types.InlineKeyboardButton(text='Edit', callback_data='profile_edit')
    btn_meet = types.InlineKeyboardButton(text='Find a new friend', callback_data='meet')
    kb.add(btn_pr_edit, btn_meet)

    user = usersDict[message.from_user.id]
    bot.send_photo(message.chat.id, user.photo, user.About(), reply_markup=kb)


@bot.callback_query_handler(func=lambda callback: callback.data == 'check_profile')
def profile(callback):
    kb = types.InlineKeyboardMarkup(row_width=1)

    btn_pr_edit = types.InlineKeyboardButton(text='Edit', callback_data='profile_edit')
    btn_meet = types.InlineKeyboardButton(text='Find a new friend', callback_data='meet')
    kb.add(btn_pr_edit, btn_meet)

    user = usersDict[callback.from_user.id]
    bot.send_photo(callback.message.chat.id, user.photo, user.About(), reply_markup=kb)


####################################################################################################################
#                                           FRIEND LIST
####################################################################################################################


@bot.message_handler(commands=['friend_list'])
def friend_list(message):
    if not checkIfRegistered(message.from_user.id, message.chat.id):
        return
    user = usersDict[message.from_user.id]
    if len(user.friends) == 0:
        kb = types.InlineKeyboardMarkup(row_width=1)
        btn_profile = types.InlineKeyboardButton(text='Check my profile', callback_data='check_profile')
        kb.add(btn_profile)
        bot.send_message(message.chat.id, 'For now your friend list is empty', reply_markup=kb)
        return

    sent = bot.send_message(message.chat.id, f'You have {len(user.friends)} friends\n'
                                             f'Write a number of them to print')
    bot.register_next_step_handler(sent, friend_list_print)


def friend_list_print(message):
    if not message.text.isdigit() or message.text == 0:
        sent = bot.send_message(message.chat.id, "Ooops, it doesn't seem as a correct number...\nTry again")
        bot.register_next_step_handler(sent, friend_list_print)
        return
    user = usersDict[message.from_user.id]
    kb = types.InlineKeyboardMarkup(row_width=1)
    btn_profile = types.InlineKeyboardButton(text='Check my profile', callback_data='check_profile')
    kb.add(btn_profile)

    text = ''
    for i in range(min(len(user.friends), int(message.text))):
        friend = usersDict[user.friends[-i - 1]]
        text = text + f'{i + 1}) {friend.name}: @{friend.username}\n'
    bot.send_message(message.chat.id, text, reply_markup=kb)


####################################################################################################################
#                                           REQUESTED-LIST
####################################################################################################################


@bot.message_handler(commands=['requested_list'])
def requested_list(message):
    if not checkIfRegistered(message.from_user.id, message.chat.id):
        return
    user = usersDict[message.from_user.id]
    if len(user.requested) == 0:
        kb = types.InlineKeyboardMarkup(row_width=1)
        btn_profile = types.InlineKeyboardButton(text='Check my profile', callback_data='check_profile')
        kb.add(btn_profile)
        bot.send_message(message.chat.id, 'For now your requested list is empty', reply_markup=kb)
        return

    sent = bot.send_message(message.chat.id, f'You have {len(user.requested)} requests\n'
                                             f'Write a number of them to print')
    bot.register_next_step_handler(sent, requested_list_print)


def requested_list_print(message):
    if not message.text.isdigit() or message.text == 0:
        sent = bot.send_message(message.chat.id, "Ooops, it doesn't seem as a correct number...\nTry again")
        bot.register_next_step_handler(sent, requested_list_print)
        return
    user = usersDict[message.from_user.id]

    for i in range(min(len(user.requested), int(message.text))):
        other_user = usersDict[user.requested[-i - 1]]
        if user.id in other_user.friends:
            bot.send_message(message.chat.id, 'You are friends with:')
        elif user.id not in other_user.viewed:
            bot.send_message(message.chat.id, 'Pending answer from:')
        else:
            bot.send_message(message.chat.id, 'Friend request was rejected by:')
        bot.send_photo(message.chat.id, other_user.photo, other_user.About())

    kb = types.InlineKeyboardMarkup(row_width=1)
    btn_profile = types.InlineKeyboardButton(text='Check my profile', callback_data='check_profile')
    kb.add(btn_profile)
    bot.send_message(message.chat.id, "That's it", reply_markup=kb)


####################################################################################################################
#                                         MEET
####################################################################################################################

@bot.callback_query_handler(func=lambda callback: callback.data == 'meet')
def meet_next(callback):
    kb = types.InlineKeyboardMarkup(row_width=1)
    user = usersDict[callback.from_user.id]

    pick_from = set(usersDict.keys()).difference(user.viewed)
    pick_from.discard(user.id)
    pick_from = list(pick_from)
    btn_profile = types.InlineKeyboardButton(text='Check my profile', callback_data='check_profile')

    if len(pick_from) == 0:
        btn_meet = types.InlineKeyboardButton(text='Find a new friend', callback_data='meet')
        kb.add(btn_profile, btn_meet)
        bot.send_message(callback.message.chat.id, "Ooops, you have seen all profiles!\nTry a bit later!",
                         reply_markup=kb)
        return

    btn_like = types.InlineKeyboardButton(text='🤝 friend request', callback_data='like')
    btn_dislike = types.InlineKeyboardButton(text='👎 next', callback_data='ignore')
    kb.add(btn_like, btn_dislike, btn_profile)

    if len(user.was_liked) > 0:
        next_id = user.was_liked[-1]
        next_user = usersDict[next_id]
        user.was_liked.pop()
        user.last_viewed = next_id
        bot.send_message(user.id, "<b>Friend request was sent by:</b>", parse_mode='html')
        bot.send_photo(callback.message.chat.id, next_user.photo, next_user.About(), reply_markup=kb)
        return

    next_id = pick_from[random.randint(0, len(pick_from) - 1)]
    user.last_viewed = next_id
    next_user = usersDict[next_id]
    bot.send_photo(callback.message.chat.id, next_user.photo, next_user.About(), reply_markup=kb)


@bot.callback_query_handler(func=lambda callback: callback.data == 'like')
def like(callback):
    user = usersDict[callback.from_user.id]
    user.viewed.add(user.last_viewed)
    user.liked.add(user.last_viewed)
    user.requested.append(user.last_viewed)

    if user.id in usersDict[user.last_viewed].liked:
        next_user = usersDict[user.last_viewed]
        user.friends.append(next_user.id)
        next_user.friends.append(user.id)
        bot.send_message(user.id, f"<b>YEES mutual friend-request with:</b> @{next_user.username}", parse_mode='html')
        bot.send_photo(user.id, next_user.photo, next_user.About())
        bot.send_message(next_user.id, f"<b>YEES mutual friend-request with:</b> @{user.username}", parse_mode='html')
        bot.send_photo(next_user.id, user.photo, user.About())
        return

    usersDict[user.last_viewed].was_liked.append(callback.from_user.id)
    bot.send_message(user.last_viewed, "You received one friend request 🤝")
    meet_next(callback)


@bot.callback_query_handler(func=lambda callback: callback.data == 'ignore')
def ignore(callback):
    user = usersDict[callback.from_user.id]
    user.viewed.add(user.last_viewed)
    meet_next(callback)


@bot.message_handler()
def unknown_text(message):
    bot.send_message(message.chat.id, 'Unknown data\nPlease choose button from upper message or check the spelling',
                     parse_mode='html')


bot.polling(none_stop=True)
