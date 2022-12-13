import logging
import time

import aiohttp
import requests
from aiogram import Bot, Dispatcher, types, executor

url = "https://qzlsklfacc.medianetwork.cloud/get_collections"

time_last_collection = time.time()
t = 0
start_flag = True
users = list()

bot = Bot(token="your_token")
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

print("Все подключения и отключения в течении 1 минуты")


# получение данных о коллекциях
async def getting_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


# обработка полученных коллекций
async def data_processing():
    global t, time_last_collection
    try:
        response = await getting_data()
        # print("Отправка запросов на коллекции...")
    except Exception:
        print(
            "Ошибка в запросе на коллекции, возможно через минуты соединение востановится, но лучше перезапустить бота)...")
        time.sleep(60)
        response = await getting_data()

    for item in response:
        if item["updateAuth"] == "[]":
            continue
        else:
            if item["date"] > time_last_collection:
                create_time = item["date"]

                if create_time > t:
                    t = create_time

                website_collection = item["website"]
                name_collection = item["name"]
                img_collection = item["img"]
                img_preview_collection = item["imgpreview"]
                link_collection = img_collection.replace(".webp", "").replace("data.", "").replace("/img",
                                                                                                   "") + "?tab=items"

                saving_an_image(img_preview_collection, img_collection)
                await sending_messages(name_collection, website_collection, link_collection)
            else:
                break

    if t > time_last_collection:
        time_last_collection = t

    time.sleep(60)
    await data_processing()


# сохранение фотографий
def saving_an_image(img_preview, img):
    if img_preview:
        img_preview = requests.get(img_preview).content
        with open("img.webp", "wb") as f:
            f.write(img_preview)

    if img:
        img = requests.get(img).content
        with open("img1.webp", "wb") as f:
            f.write(img)


# отправка сообщений
async def sending_messages(name, website, link):
    if users:
        print("Отправка сообщений пользователям")
        for user in users:
            await bot.send_photo(chat_id=user, photo=open("img.webp", "rb"))
            await bot.send_photo(chat_id=user, photo=open("img1.webp", "rb"))
            await bot.send_message(chat_id=user, text=f"Название коллекции: {name}\n"
                                                      f"Сайт коллекции: {website}\n"
                                                      f"Cсылка на коллекцию: {link}")


# команда запуска Бота
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    global start_flag
    if message.chat.id not in users:
        users.append(message.chat.id)
        await bot.send_message(chat_id=message.chat.id, text=f"Привет {message.chat.first_name}, работаем!")
        print(f"Подключился пользователь {message.chat.first_name}...")

    if start_flag:
        start_flag = False
        await data_processing()


# команда остановки Бота
@dp.message_handler(commands=["stop"])
async def stop(message: types.Message):
    if message.chat.id in users:
        print(f"пользователь {message.chat.first_name} отключился...")
        users.remove(message.chat.id)
        await bot.send_message(chat_id=message.chat.id, text=f"Вы отключены")
    else:
        await bot.send_message(chat_id=message.chat.id, text=f"Вы не были подключены)")


executor.start_polling(dp, skip_updates=True, timeout=600)
