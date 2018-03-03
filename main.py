import telebot
from random import choice
from SQL_class import Postrges

token = '475007860:AAHf9Vp80WUiQhnc0u2ZSAfrJxGKj4QCZcs'
url = 'https://cdn.ennergiia.com/images/ennergiia-catalog/492x738/%d/ac-%d-%d.jpg'

conn_string = "host=%s port=%s dbname=%s user=%s password=%s" % ('localhost',
                                                                 '5432',
                                                                 'data2',
                                                                 'postgres',
                                                                 '1513178c')

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def command_help(message):
    print('messs', message)
    bot.send_message(message.chat.id, "Привет! Нужна твоя помощь в оценке картинок!")
    send_image(message.chat.id, message.from_user.id)

@bot.message_handler(commands=["marks"])
def command_help(message):
    mark = get_score(message.from_user.id)
    bot.send_message(message.chat.id, 'Вы оценили %d фотографий' % mark)

def get_image_from_db(rand, db):
    result = db.run_query('SELECT * FROM images WHERE id=%d;' % rand)[0]
    print('data', result)
    return result


def get_rand_image(id, db):
    img_url = None
    img_id = None
    imgs = list(map(lambda x: int(x[0]), db.run_query('SELECT id FROM images;')))
    print('col', imgs)
    marked_imgs = list(map(lambda x: int(x[0]), db.run_query('SELECT img FROM checked_img WHERE id=%d;' % id)))
    print('marked_imgs', marked_imgs)
    if len(marked_imgs) != len(imgs):
        rand = choice(list(set(imgs) - set(marked_imgs)))
        print('rand', rand)

        url_parts = get_image_from_db(rand, db)
        img_url = url % (url_parts[3], url_parts[1], url_parts[2])
        img_id = url_parts[0]

    return img_url, img_id


def send_image(id, uid):
    db = Postrges(conn_string)
    result = db.run_query('SELECT * FROM users WHERE id=%d;' % uid)
    if not result:
        result = db.run_query('INSERT INTO users (id) VALUES (%d);' % uid)
        print(result)
    url, img_id = get_rand_image(id, db)
    if url:
        print(url)
        keyboard = telebot.types.InlineKeyboardMarkup()
        but_like = telebot.types.InlineKeyboardButton(text='Like', callback_data='like__' + str(img_id))
        but_next = telebot.types.InlineKeyboardButton(text='Next', callback_data='next__' + str(img_id))
        keyboard.add(but_like, but_next)
        bot.send_photo(id, photo=url, reply_markup=keyboard)
    else:
        bot.send_message(id, 'Вы оценили все картинки, спасибо!')


def get_score(uid):
    db = Postrges(conn_string)
    mark = db.run_query('SELECT marks FROM users WHERE id=%d' % uid)[0][0]
    print(mark)
    return mark


def mark_img(uid, text, img_id, db):
    mark = 1 if text == 'like' else 0
    print(type(uid), type(img_id))
    result = db.run_query('SELECT * FROM marks WHERE uid=%d AND img=%d;' % (uid, img_id))
    print('checked?', result)
    if not result:
        db.run_query('UPDATE users SET marks=marks+1 WHERE id=%d;' % uid)
        db.run_query('INSERT INTO marks (uid, img, mark) VALUES (%d, %d, %d);' % (uid, img_id, mark))



def handle_button(score, img_id, imgExists = False):
    print('score!', score)
    uid = score.from_user.id
    if score.text in ('like', 'next') and imgExists:
        mark_img(uid, score.text, img_id)

        send_image(score.chat.id, uid)
    elif score.text == 'marks':
        mark = get_score(uid)
        ans = bot.send_message(score.chat.id, 'Вы оценили %d фотографий' % mark)
        bot.register_next_step_handler(ans, lambda m: handle_button(m, img_id, imgExists))
    else:
        ans = bot.send_message(score.chat.id, 'Пожалуйста, используйте только кнопки для оценки фотографии')
        bot.register_next_step_handler(ans, lambda m: handle_button(m, img_id, imgExists))

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    print('call', call)
    print(call.message.chat)
    mark, img_id = call.data.split('__')
    img_id = int(img_id)

    db = Postrges(conn_string)
    mark_img(call.from_user.id, mark, img_id, db)

    result = db.run_query('SELECT * FROM checked_img WHERE img=%d and id=%d' % (img_id, call.message.chat.id))
    print('exist in db?', result)
    if not result:
        db.run_query('INSERT INTO checked_img (img, id) VALUES (%d, %d)' % (img_id, call.message.chat.id))
        send_image(call.message.chat.id, call.from_user.id)



if __name__ == '__main__':
    bot.polling(none_stop=True)