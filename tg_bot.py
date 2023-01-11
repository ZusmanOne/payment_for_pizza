from environs import Env
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, )
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackQueryHandler)

import redis
from api_moltin import (get_all_pizza,get_product,get_image, get_token, add_product_cart,
                        get_cart,get_cart_items, create_cart,)
from time import time


def start(context, update):
    serialize_products = get_all_pizza(context.bot_data['valid_token'])
    keyboard = [[InlineKeyboardButton("Корзина", callback_data='Корзина')]]
    for product in serialize_products['data']:
        keyboard.append(
            [InlineKeyboardButton(product['name'], callback_data=product['id'])]
        )
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return "HANDLE_MENU"


def handle_menu(context, update):
    query = update.callback_query
    if query.data == 'Корзина':
        chat_id = query.message.chat_id
        cart_items = get_cart_items(chat_id, context.bot_data['valid_token'])
        keyboard = [([InlineKeyboardButton(f"Удалить {product_item['name']}", callback_data=product_item['id'])])
                    for product_item in cart_items['data']]
        keyboard.append([InlineKeyboardButton("Назад к пиццам", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        cart = get_cart_items(chat_id, context.bot_data['valid_token'])
        description_cart = [
            f"""Наименование-{product['name']}
            Описание-{product['description']}
            В корзине: {product['quantity']} шт на сумму:
            {product['meta']['display_price']['with_tax']['value']['formatted']}\n\n"""
            for product in cart['data']]
        full_cart = get_cart(chat_id, context.bot_data['valid_token'])
        description_cart.append(f"Общая сумма:{full_cart['data']['meta']['display_price']['with_tax']['formatted']}")
        context.bot.send_message(chat_id=chat_id,
                                 text="".join(description_cart),
                                 reply_markup=reply_markup)
        return "HANDLE_CART"

    keyboard = [[InlineKeyboardButton("Положить в корзину", callback_data=query.data)],
                [InlineKeyboardButton("Назад к пиццам", callback_data='back')],
                [InlineKeyboardButton("Корзина", callback_data='Корзина'), ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    serializer_product = get_product(query.data, context.bot_data['valid_token'])
    file_product_id = serializer_product['data']['relationships']['files']['data'][0]['id']
    context.bot.send_photo(chat_id=query.message.chat_id, photo=get_image(file_product_id,context.bot_data['valid_token']),
                           caption=f"""{serializer_product['data']['name']}
                                       {serializer_product['data']['description']}
                                       {serializer_product['data']['price'][0]['amount']}р. - за шт""",
                           reply_markup=reply_markup)
    context.bot.delete_message(chat_id=query.message.chat_id,
                               message_id=update.callback_query.message.message_id)

    return 'HANDLE_DESCRIPTION'


def handle_description(context, update):
    query = update.callback_query
    query_data = query.data
    chat_id = query.message.chat_id
    if query.data == 'Корзина':
        cart_items = get_cart_items(chat_id, context.bot_data['valid_token'])
        keyboard = [([InlineKeyboardButton(f"Удалить {product_item['name']}", callback_data=product_item['id']), ])
                    for product_item in cart_items['data']]
        keyboard.append([InlineKeyboardButton("Назад к пиццам", callback_data='back')])
        keyboard.append([InlineKeyboardButton("Оплатить", callback_data='pay')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        cart = get_cart_items(query.message.chat_id, context.bot_data['valid_token'])
        description_cart = [
            f"""Наименование-{product['name']}
            Описание-{product['description']}
            Цена за 1кг: {product['meta']['display_price']['with_tax']['unit']['formatted']}
            В корзине: {product['quantity']} кг на сумму:
            {product['meta']['display_price']['with_tax']['value']['formatted']}\n\n"""
                            for product in cart['data']]
        full_cart = get_cart(query.message.chat_id, context.bot_data['valid_token'])
        description_cart.append(f"Общая сумма:{full_cart['data']['meta']['display_price']['with_tax']['formatted']}")
        context.bot.send_message(text="".join(description_cart),
                                 chat_id=query.message.chat_id,
                                 reply_markup=reply_markup)
        return "HANDLE_CART"
    elif query.data == 'back':
        serialize_products = get_all_pizza(context.bot_data['valid_token'])
        keyboard = []
        for product in serialize_products['data']:
            keyboard.append(
                [InlineKeyboardButton(product['name'], callback_data=product['id'])]
            )
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text="Selected option:",
                                 chat_id=chat_id,
                                 reply_markup=reply_markup)
        return "HANDLE_MENU"
    else:
        # product, quantity = query_data.split('*')
        get_cart(chat_id, context.bot_data['valid_token'])
        print(query_data)
        product_id = query_data
        #print(product_id)
        add_product_cart(chat_id, product_id, context.bot_data['valid_token'])
        return "HANDLE_CART"


def handle_cart(context, update):
    query = update.callback_query
    chat_id = query.message.chat_id
    item_id = query.data
    if query.data == 'pay':
        context.bot.send_message(text="Напишите свою почту, мы вышлем счет",
                                 chat_id=chat_id)
        return 'WAITING_EMAIL'
    if query.data == 'back':
        serialize_products = get_all_product(context.bot_data['valid_token'])
        keyboard = []
        for product in serialize_products['data']:
            keyboard.append(
                [InlineKeyboardButton(product['name'], callback_data=product['id'])]
            )
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text="Selected option:",
                                 chat_id=chat_id,
                                 reply_markup=reply_markup)
        return "HANDLE_MENU"
    else:
        delete_cart_item(chat_id, item_id, context.bot_data['valid_token'])
        return 'HANDLE_CART'


def waiting_email(context, update):
    chat_id = update.message.chat_id
    user_email = update.message.text
    update.message.reply_text(f'Ваша почта {user_email}')
    create_customers(user_email, context.bot_data['valid_token'])
    return "START"


def handle_users_reply(update, context):
    db = context.bot_data['db']
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode("utf-8")
    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart,
        'WAITING_EMAIL': waiting_email,
    }

    state_handler = states_functions[user_state]
    try:
        if context.bot_data['lifetime_token'] < time():
            client_id = db.get('client_id')
            client_secret = db.get('client_secret')
            authorization_data = get_token(client_id, client_secret)
            context.bot_data['valid_token'] = authorization_data['authorization']
            context.bot_data['lifetime_token'] = authorization_data['expires']
        next_state = state_handler(context, update)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err, 'error')


if __name__ == '__main__':
    env = Env()
    env.read_env()
    token = env("TG_TOKEN")
    client_id = env('CLIENT_ID')
    client_secret = env('CLIENT_SECRET')
    database_password = env('REDIS_PASSWORD')
    database_host = env('REDIS_HOST')
    database_port = env('REDIS_PORT')
    db = redis.StrictRedis(host=database_host,
                           port=database_port,
                           password=database_password,
                           charset="utf-8")
    authorization_data = get_token(client_id, client_secret)
    db.set('client_id',client_id)
    db.set('client_secret', client_secret)
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.bot_data['db'] = db
    dispatcher.bot_data['valid_token'] = authorization_data['authorization']
    dispatcher.bot_data['lifetime_token'] = authorization_data['expires']
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
