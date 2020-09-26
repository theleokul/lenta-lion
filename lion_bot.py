import sys
from pathlib import Path

import telebot
from telebot import types

DIRPATH = Path(__file__).resolve().parent
sys.path.append(str(DIRPATH))
import lion


user_data = {}
bot = telebot.TeleBot('1225129237:AAE2kx6dq1vuM22PfcD0Md0lyZv3cl1Dbbk')
goods_array = ['chocolate', 'coffee', 'croissant', 'omelet', 'bacon']
user = {
    'card_id' : ''
    ,'plant_id' : ''
    ,'fav_prod_1': ''
    ,'fav_prod_2': ''
    ,'fav_prod_3': ''
    ,'order_date': ''
}


def dummy(message):
    try:
        msg = bot.send_message(
            message.chat.id, 
            'Thank you!'
        )
    except Exception as e:
        bot.reply_to(message, 'Meow...')


def predict(message):
    try:
        msg = bot.send_message(message.chat.id, 'Hello world start')
        goods_array, discounts = lion.roar_basket(
            user['card_id'] 
            ,[user['fav_prod_1'], user['fav_prod_2'], user['fav_prod_3']]
            ,user['plant_id'] 
            ,user['order_date'] 
        )
        print('Hello world end')
        # import ipdb; ipdb.set_trace()
        # msg = bot.send_message(
        #     message.chat.id
        #     ,f"""
        #     This is your basket:
        #     {r' '.join(goods_array)}
        #     This is your discounts:
        #     {r' '.join(list(discounts.items()))}

        #     Thank you!
        #     """
        # )
        bot.register_next_step_handler(msg, dummy)
    except Exception as e:
        bot.reply_to(message, 'Meow...')


def get_order_date(message):
    try:
        user['order_date'] = message.text
        msg = bot.send_message(
            message.chat.id, 
            "Wait a minute... I need to scratch the chair."
        )
        bot.register_next_step_handler(msg, predict)
    except Exception as e:
        bot.reply_to(message, 'Meow...')


def get_fav_prod_3(message):
    try:
        user['fav_prod_3'] = message.text
        msg = bot.send_message(message.chat.id, "When do you like to get your basket?")
        bot.register_next_step_handler(msg, get_order_date)
    except Exception as e:
        bot.reply_to(message, 'Meow...')


def get_fav_prod_2(message):
    try:
        user['fav_prod_2'] = message.text
        msg = bot.send_message(message.chat.id, "What is you favourite product #3?")
        bot.register_next_step_handler(msg, get_fav_prod_3)
    except Exception:
        bot.reply_to(message, 'Meow...')


def get_fav_prod_1(message):
    try:
        user['fav_prod_1'] = message.text
        msg = bot.send_message(message.chat.id, "What is you favourite product #2?")
        bot.register_next_step_handler(msg, get_fav_prod_2)
    except Exception:
        bot.reply_to(message, 'Meow...')


def get_plant_id(message):
    try:
        user['plant_id'] = message.text
        msg = bot.send_message(message.chat.id, "What is you favourite product #1?")
        bot.register_next_step_handler(msg, get_fav_prod_1)
    except Exception:
        bot.reply_to(message, 'Meow...')


def get_card_id(message):
    try:
        user['card_id'] = message.text
        msg = bot.send_message(message.chat.id, "What is you favourite plant?")
        bot.register_next_step_handler(msg, get_plant_id)
    except Exception:
        bot.reply_to(message, 'Meow...')


@bot.message_handler(content_types=['text'])
def start_message(message):
    msg = bot.send_message(
        message.chat.id, 
        'Hey, I am Lenta Lion, enter your card id, please...'
    )
    bot.register_next_step_handler(msg, get_card_id)


bot.polling(none_stop=True, interval=0)
