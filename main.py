import telebot
from newsapi import NewsApiClient
from telebot import types
from function import *

connect = sqlite3.connect('dbase.db', check_same_thread=False)
cursor = connect.cursor()
newsapi = NewsApiClient(api_key='76ba137bf38b4150b603fab468df7f3a')

bot = telebot.TeleBot("6477893231:AAHgIVCKUF1QZqjKkG0sYBc3FMiRzE_LCyY", parse_mode=None)


@bot.message_handler(commands=['start'])
def start(message):

    # ищем и добавляем  пользователя
    user_id =[message.chat.id]
    user = cursor.execute('SELECT * FROM users WHERE tg_id = ?;', (user_id)).fetchall()




    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_news = types.KeyboardButton('Новости')
    button_categories = types.KeyboardButton('Категории')
    button_sub = types.KeyboardButton('Подписки')
    markup.add(button_news, button_categories, button_sub)
    if not user:
        cursor.execute('''INSERT INTO users('tg_id') VALUES (?)''', user_id)
        connect.commit()
        bot.reply_to(message, "Вы успешно зарегистрировались)", reply_markup=markup)
        print('Добавил в базу')
    else:
        bot.reply_to(message, "Вы уже зарегистрированы)", reply_markup=markup)
        print('Уже в базе')


@bot.message_handler(content_types=['text'])
def News(message):
    connect = sqlite3.connect("dbase.db")
    cursor = connect.cursor()
    if message.chat.type == 'private':
        if message.text == 'Категории':
            markup = types.ReplyKeyboardMarkup( resize_keyboard=True )
            categories = cursor.execute('''SELECT * FROM categories''').fetchall()
            i = 0
            while i < len(categories):
                categor = types.KeyboardButton('+ ' + categories[i][1])
                i = i + 1
                markup.add(categor)
            back = types.KeyboardButton('Назад')
            markup.add(back)
            bot.reply_to(message, 'Категории', reply_markup=markup)
    if message.chat.type == 'private':
        pattern = '+'
        if message.text.startswith(pattern):
            user_id = [message.chat.id]
            id = cursor.execute('''SELECT id FROM users WHERE tg_id = ?''', (user_id)).fetchone()
            id = str(id[0])
            subs = cursor.execute(
                '''SELECT * FROM subscribes INNER JOIN categories ON categories.id = subscribes.category_id WHERE user_id = ? ;''',
                (id)).fetchall()
            mass = []
            i = 0
            while i < len(subs):
                mass.append(subs[i][3])
                i = i + 1
            i = 0
            count = 0
            name_sub = message.text[2:]
            while i < len(mass):
                if name_sub == mass[i]:
                    count = count + 1
                i = i + 1
            if count == 0:
                cat_id = cursor.execute('''SELECT id FROM categories WHERE name = ? ; ''', (name_sub,)).fetchall()
                cursor.execute('''INSERT INTO subscribes ('user_id', 'category_id') VALUES (?, ?) ''',(id, cat_id[0][0]))
                connect.commit()
                bot.reply_to(message, 'Вы подписались')
            else:
                bot.reply_to(message, 'У вас уже есть данная подписка')

    if message.chat.type == 'private':
        if message.text == 'Подписки':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            tg_id = message.from_user.id
            user_id = str(findUserId(tg_id)[0])
            subscribes = cursor.execute(
                '''SELECT name FROM subscribes  INNER JOIN categories  ON categories.id=subscribes.category_id WHERE user_id = ?''',
                (user_id,)).fetchall()
            i = 0
            while i < len(subscribes):
                print(subscribes[i])
                sub = types.KeyboardButton('- ' + subscribes[i][0])
                i = i + 1
                markup.add(sub)
            back = types.KeyboardButton('Назад')
            markup.add(back)
            bot.reply_to(message, 'Подписки', reply_markup=markup)
    if message.chat.type == 'private':
        pattern = '-'
        if message.text.startswith(pattern):
            user_id = [message.chat.id]
            id = cursor.execute('''SELECT id FROM users WHERE tg_id = ?''', (user_id)).fetchone()
            id = str(id[0])

            subs = cursor.execute(
                '''SELECT * FROM subscribes INNER JOIN categories ON categories.id = subscribes.category_id WHERE user_id = ? ;''',
                (id)).fetchall()
            mass = []
            i = 0
            count = 0
            name_sub = message.text[2:]
            while i < len(mass):
                if name_sub == mass[i]:
                    count = count + 1
                i = i + 1
            cat_id = cursor.execute('''SELECT id FROM categories WHERE name = ? ; ''', (name_sub,)).fetchall()
            cursor.execute('''DELETE FROM subscribes                                                                                                                    
                  WHERE user_id = ? AND category_id = ?''',
                           (id, cat_id[0][0]))
            connect.commit()
            bot.reply_to(message, 'Вы отписались')
        elif message.text == 'Новости':

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            tg_id = message.from_user.id
            user_id = str(findUserId(tg_id)[0])
            userSub = findUserSubscribes(user_id)
            i = 0
            while i < len(userSub):
                name = types.KeyboardButton("Посмотреть новости про:" + ' '.join(userSub[i]))
                markup.add(name)
                i = i + 1
            back = types.KeyboardButton('Назад')
            markup.add(back)
            bot.reply_to(message, "Новости про:", reply_markup=markup)

        elif message.text.startswith("Посмотреть"):
            tg_id = message.from_user.id
            user_id = str(findUserId(tg_id)[0])
            subscribes = searchUserCategory(user_id)
            arr = []
            i = 0
            while i < len(subscribes):
                arr.append(subscribes[i])
                i = i + 1
            i = 0
            count = 0
            text = message.text[23:]
            while i < len(arr):
                if text == arr[i][0]:
                    count = count + 1
                i = i + 1
            if count > 0:
                category_id = findCategory(text)[0]

                category_name = findCategoryName(category_id)[0]
                print(category_name)
                top_headlines = newsapi.get_top_headlines(category=category_name, language='ru')
                bot.send_message(message.from_user.id,
                                 f'{top_headlines["articles"][0]["title"]}\n {top_headlines["articles"][0]["url"]}')
                bot.send_message(message.from_user.id,
                                 f'{top_headlines["articles"][1]["title"]}\n {top_headlines["articles"][1]["url"]}')

        if message.text == 'Назад':

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_news = types.KeyboardButton('Новости')
            button_categories = types.KeyboardButton('Категории')
            button_sub = types.KeyboardButton('Подписки')

            markup.add(button_news, button_categories, button_sub)
            bot.reply_to(message, "Главное меню", reply_markup=markup)


bot.infinity_polling(none_stop=True)
