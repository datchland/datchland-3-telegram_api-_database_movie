import telebot
import base
import app_api
import database  

bot = telebot.TeleBot(base.TOKEN)
database.init_db()
print('bot created ... ')

@bot.message_handler(commands=['start'])
def say_hello(message):
    markup = telebot.types.InlineKeyboardMarkup()

    btn1 = telebot.types.InlineKeyboardButton(text=" Search",  callback_data="search")
    btn2 = telebot.types.InlineKeyboardButton(text=" Popular", callback_data="popular")
    btn3 = telebot.types.InlineKeyboardButton(text=" About Us", callback_data="about")
    btn4 = telebot.types.InlineKeyboardButton(text=" Saved",   callback_data="saved")

    markup.row(btn1, btn2)
    markup.row(btn3, btn4)  

    bot.send_message(
        message.chat.id,
        "Welcome! Please choose an option.",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "search")
def handle_search(call):
    msg = bot.send_message(call.message.chat.id, "Please enter the movie title you want to search:")
    bot.register_next_step_handler(msg, search_query)


def search_query(message):
    query = message.text.strip()

    if not query or len(query) < 2:
        msg = bot.send_message(message.chat.id, "Please enter at least 2 characters.")
        bot.register_next_step_handler(msg, search_query)
        return

    bot.send_message(message.chat.id, f"Searching for {query}...")  

    try:
        results = app_api.get_movie_info_by_name(query)

        if results == 'ERROR':
            bot.send_message(message.chat.id, "Could not reach the movie database.")
            return
        if results == 'EMPTY' or not results:
            bot.send_message(message.chat.id, "No movies found. Try a different title.")
            return

        markup = telebot.types.InlineKeyboardMarkup()
        for movie in results[:5]:
            title = movie.get('title', 'Unknown')
            year  = movie.get('year', '')
            label = f"{title} ({year})" if year else title
            btn   = telebot.types.InlineKeyboardButton(text=label, callback_data=f"movie_{movie['id']}")
            markup.add(btn)

        bot.send_message(message.chat.id, "Select a movie to see details:", reply_markup=markup)

    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("movie_"))
def show_movie_details(call):
    movie_id = call.data.split("_")[1]
    result = app_api.get_movie_info_by_id(movie_id)

    if result == 'ERROR':
        bot.send_message(call.message.chat.id, "Could not fetch movie details.")
        return

    text = (
        f"🎬 {result['title']}\n\n"
        f"📅 Year: {result['year']}\n"
        f"🌍 Country: {result['country']}\n"
        f"🎥 Director: {result['director']}\n"
        f"⭐ IMDB Rating: {result['imdb_rating']}"
    )

    markup = telebot.types.InlineKeyboardMarkup()
    btn_save = telebot.types.InlineKeyboardButton(
        text="Save this movie",
        callback_data=f"save_{movie_id}"
    )
    markup.add(btn_save)

    bot.send_message(call.message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "popular")
def handle_popular(call):
    bot.send_message(call.message.chat.id, "Fetching popular movies...")
    results = app_api.get_popular_movies()

    if results == 'ERROR':
        bot.send_message(call.message.chat.id, "Could not reach the movie database.")
        return
    if results == 'EMPTY':
        bot.send_message(call.message.chat.id, "No movies found.")
        return

    markup = telebot.types.InlineKeyboardMarkup()
    for movie in results[:10]:
        title = movie.get('title', 'Unknown')
        year  = movie.get('year', '')
        label = f"{title} ({year})" if year else title
        btn   = telebot.types.InlineKeyboardButton(text=label, callback_data=f"movie_{movie['id']}")
        markup.add(btn)

    bot.send_message(                        
        call.message.chat.id,
        "Popular Movies:\nTap one to see details.",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "help")
def handle_help(call):
    bot.send_message(call.message.chat.id, "Use Search to find a movie, Popular to see trending.")




@bot.callback_query_handler(func=lambda call: call.data == "about")
def handle_about(call):
    text = (
        "🏢 Name: fira.inc\n"
        "📧 Contact: fira.inc@gmail.com\n"
        "👨‍💻 Bot created by Sina Zamani"
    )
    bot.send_message(call.message.chat.id, text)




@bot.callback_query_handler(func=lambda call: call.data.startswith("save_"))
def handle_save(call):
    movie_id = call.data.split("_")[1]
    result = app_api.get_movie_info_by_id(movie_id)

    if result == 'ERROR':
        bot.answer_callback_query(call.id, "Could not save.")
        return

    result['id'] = movie_id
    saved = database.save_movie(call.from_user.id, result)

    if saved:
        bot.answer_callback_query(call.id, " Movie saved!")
    else:
        bot.answer_callback_query(call.id, "Already in your saved list.")


@bot.callback_query_handler(func=lambda call: call.data == "saved")
def handle_saved(call):
    movies = database.get_saved_movies(call.from_user.id)

    if not movies:
        bot.send_message(call.message.chat.id, "You have no saved movies yet.")
        return

    markup = telebot.types.InlineKeyboardMarkup()
    for movie in movies:
        label = f"{movie['title']} ({movie['year']})"
        btn_view = telebot.types.InlineKeyboardButton(
            text=label,
            callback_data=f"movie_{movie['id']}"
        )
        btn_del = telebot.types.InlineKeyboardButton(
            text=" Remove",
            callback_data=f"delete_{movie['id']}"
        )
        markup.row(btn_view, btn_del)   

    bot.send_message(call.message.chat.id, " Your saved movies:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def handle_delete(call):
    movie_id = call.data.split("_")[1]
    database.delete_saved_movie(call.from_user.id, movie_id)
    bot.answer_callback_query(call.id, " Removed!")
    handle_saved(call)





if __name__ == '__main__':
    bot.infinity_polling()