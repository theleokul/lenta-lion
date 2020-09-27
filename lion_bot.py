import sys
from pathlib import Path

import telebot
from telebot import types

DIRPATH = Path(__file__).resolve().parent
sys.path.append(str(DIRPATH))
import lion


bot = telebot.TeleBot('YOUR_TELEGRAM_BOT_TOKEN')


@bot.message_handler(commands=['simulate'])
def simulate(message):
    components = message.text.split()[1:]
    goods_array, discounts = lion.roar_basket(
        'c23395'  
        ,['m61505', 'm55357', 'm22242'] 
        ,'pl293'   
        ,'2017-06-20' 
    )
    bot.send_message(
        message.chat.id, 
        'Basket:\n' + '\n'.join(goods_array) + '\n\nDiscounts:' + '\n' + f"{discounts}"
    )


@bot.message_handler(commands=['fill'])
def fill(message):
    components = message.text.split()[1:]
    goods_array, discounts = lion.roar_basket(
        components[0]  
        ,components[1:4]  
        ,components[4]   
        ,components[5]
    )
    bot.send_message(
        message.chat.id, 
        'Basket:\n' + '\n'.join(goods_array) + '\n\nDiscounts:' + '\n' + f"{discounts}"
    )


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(
        message.chat.id, 
        """
        To fill your basket automatically simply run the command:

        /fill client_id favourite_products plant_id date, where:

        client_id - your personal card id
        favourite_products - ids of your favourite products
        plant_id - store from which you want to buy
        date - when you want us to fill your basket in format %Y-%m-%d

        ---------------

        To simulate basket filling run the command:

        /simulate

        This command runs /fill with arguments:

        client_id: 'c23395'  
        favourite_products: ['m61505', 'm55357', 'm22242'] 
        plant_id: 'pl293'   
        date: '2017-06-20' 
        """
    )


@bot.message_handler(content_types=['text'])
def start_message(message):
    bot.send_message(
        message.chat.id, 
        'Hey, I am Lenta Lion, see /help'
    )


bot.polling(none_stop=True, interval=0)
