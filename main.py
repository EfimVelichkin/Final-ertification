import disnake
from disnake.ext import commands
import subprocess
import os
from config import host, user, password, db_name, port
from database import get_theory, create_db_connection, update_user_points, user_exists_in_db, get_random_pet_project, get_random_task

connection_string = f"dbname='{db_name}' user='{user}' host='{host}' password='{password}' port='{port}'"

def add_user_to_db(connection, user: disnake.User):
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (id, username, discriminator) VALUES (%s, %s, %s)",
            (user.id, user.name, user.discriminator)
        )
        print(f"{user.name} был добавлен в базу данных!")
    except Exception as e:
        print(f"Ошибка при добавлении пользователя в базу данных: {e}")
    finally:
        cursor.close()

intents = disnake.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, test_guilds=[1155554329026121768])

@bot.event
async def on_ready():
    print("Bot is ready!")
    bot.db_connection = create_db_connection()

@bot.command(name="add_user")
async def add_user(ctx):
    if bot.db_connection:
        add_user_to_db(bot.db_connection, ctx.author)
    else:
        await ctx.send("Ошибка подключения к базе данных.")

@bot.command()
async def menu(ctx):
    # Создаем кнопки для первого уровня
    if bot.db_connection:
        user_id = ctx.author.id
        if user_exists_in_db(bot.db_connection, user_id):
            await ctx.send("Выберите раздел:", components=[
                disnake.ui.ActionRow(
                    disnake.ui.Button(style=disnake.ButtonStyle.primary, label="Учебник", custom_id="text_book"),
                    disnake.ui.Button(style=disnake.ButtonStyle.primary, label="Легендарные табутаски", custom_id="pet_projects"),
                    disnake.ui.Button(style=disnake.ButtonStyle.primary, label="Мой рейтинг", custom_id=f"my_lvl_{ctx.author.id}_")
                )
            ])
        else:
            # Если пользователь не найден, предлагаем зарегистрироваться
            await ctx.send("Вы не зарегистрированы. Зарегистрируйтесь, чтобы продолжить.")
            add_user_to_db(bot.db_connection, ctx.author)
            await ctx.send("Вы успешно занесены в БД.")
    else:
        await ctx.send("Ошибка подключения к базе данных.")
user_themes = {}

def get_user_stats(connection, user_id):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT username, points FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            username, points = user_data
            # Определение звания на основе количества баллов
            if points < 5:
                rank = "Вангер"
            elif points >= 20 and points < 30:
                rank = "Элипод"
            elif points >= 30:
                rank = "Бибурат"
            else:
                rank = "~неизвестно~"
            return username, points, rank
        else:
            return None, None, None
    except Exception as e:
        print(f"Ошибка при получении статистики пользователя: {e}")
        return None, None, None
    finally:
        cursor.close()

@bot.listen("on_button_click")
async def on_button_click(inter: disnake.MessageInteraction):
    user_id = inter.user.id
    if inter.component.custom_id == "text_book":
        # Создаем кнопки для второго уровня
        await inter.response.send_message("Выберите что хотите изучать:", components=[
            disnake.ui.ActionRow(
                disnake.ui.Button(style=disnake.ButtonStyle.primary, label="python", custom_id="python"),
                disnake.ui.Button(style=disnake.ButtonStyle.primary, label="HTML\CSS", custom_id="verstka")
            )
        ])
    elif inter.component.custom_id == "python":
        # Создаем кнопки для третьего уровня
        await inter.response.send_message("Чем сегодня хотите заниматься?", components=[
            disnake.ui.ActionRow(
                disnake.ui.Button(style=disnake.ButtonStyle.primary, label="изучать теорию", custom_id="theory"),
                disnake.ui.Button(style=disnake.ButtonStyle.primary, label="решать задачи", custom_id="practice_task"),
            )
        ])
    elif inter.component.custom_id == "theory":
        # выдаем теорию
        theory = get_theory()
        if theory:
            await inter.response.send_message(theory)
    elif inter.component.custom_id == "practice_task":
        # создаем кнопки для четвертого уровня
        await inter.response.send_message("Выберите раздел:", components=[
            disnake.ui.ActionRow(
                disnake.ui.Button(style=disnake.ButtonStyle.primary, label="ввод и вывод", custom_id="theme_1"),
                disnake.ui.Button(style=disnake.ButtonStyle.primary, label="условные операторы", custom_id="theme_2"),
                disnake.ui.Button(style=disnake.ButtonStyle.primary, label="циклы", custom_id="theme_3"),
            ),
            disnake.ui.ActionRow(
                disnake.ui.Button(style=disnake.ButtonStyle.primary, label="списки", custom_id="theme_4"),
                disnake.ui.Button(style=disnake.ButtonStyle.primary, label="функции", custom_id="theme_5"),
                disnake.ui.Button(style=disnake.ButtonStyle.primary, label="словари", custom_id="theme_6")
            )
        ])
    elif inter.component.custom_id == "theme_1":
        # создаем кнопки для пятого уровня
        user_themes[user_id] = "1"
        await inter.response.send_message("Выберите уровень сложности", components=[
            disnake.ui.Button(style=disnake.ButtonStyle.green, label="Элипод", custom_id="easy_py"),
            disnake.ui.Button(style=disnake.ButtonStyle.danger, label="Бибурат", custom_id="hard_py")
        ])
    elif inter.component.custom_id == "theme_2":
        # создаем кнопки для пятого уровня
        user_themes[user_id] = "2"
        await inter.response.send_message("Выберите уровень сложности", components=[
            disnake.ui.Button(style=disnake.ButtonStyle.green, label="Элипод", custom_id="easy_py"),
            disnake.ui.Button(style=disnake.ButtonStyle.danger, label="Бибурат", custom_id="hard_py")
        ])
    elif inter.component.custom_id == "theme_3":
        # создаем кнопки для пятого уровня
        user_themes[user_id] = "3"
        await inter.response.send_message("Выберите уровень сложности", components=[
            disnake.ui.Button(style=disnake.ButtonStyle.green, label="Элипод", custom_id="easy_py"),
            disnake.ui.Button(style=disnake.ButtonStyle.danger, label="Бибурат", custom_id="hard_py")
        ])
    elif inter.component.custom_id == "theme_4":
        # создаем кнопки для пятого уровня
        user_themes[user_id] = "4"
        await inter.response.send_message("Выберите уровень сложности", components=[
            disnake.ui.Button(style=disnake.ButtonStyle.green, label="Элипод", custom_id="easy_py"),
            disnake.ui.Button(style=disnake.ButtonStyle.danger, label="Бибурат", custom_id="hard_py")
        ])
    elif inter.component.custom_id == "theme_5":
        # создаем кнопки для пятого уровня
        user_themes[user_id] = "5"
        await inter.response.send_message("Выберите уровень сложности", components=[
            disnake.ui.Button(style=disnake.ButtonStyle.green, label="Элипод", custom_id="easy_py"),
            disnake.ui.Button(style=disnake.ButtonStyle.danger, label="Бибурат", custom_id="hard_py")
        ])
    elif inter.component.custom_id == "theme_6":
        # создаем кнопки для пятого уровня
        user_themes[user_id] = "6"
        await inter.response.send_message("Выберите уровень сложности", components=[
            disnake.ui.Button(style=disnake.ButtonStyle.green, label="Элипод", custom_id="easy_py"),
            disnake.ui.Button(style=disnake.ButtonStyle.danger, label="Бибурат", custom_id="hard_py")
        ])
    elif inter.component.custom_id == "easy_py":
        # выдыем задания легкого уровня для пайтона
        theme = user_themes.get(user_id)
        if theme:
            task = get_random_task(theme)
            if task:
                await inter.response.send_message(task)
            else:
                await inter.response.send_message("В таблице tasks нет заданий")
        else:
            await inter.response.send_message("Выберите тему перед уровнем сложности")
    elif inter.component.custom_id == "hard_py":
        await inter.response.send_message("Вы выбрали сложное задание (оно сейчас не добавлено)")
    elif inter.component.custom_id == "pet_projects":
        # выдаем 1 рандомный пет-проект
        proj = get_random_pet_project()
        if proj:
            await inter.response.send_message(proj)
        else:
            await inter.response.send_message("В таблице pet_projects нет заданий")
    elif inter.component.custom_id.startswith("my_lvl_"):
        print("Button clicked") # Добавьте это для проверки
        if inter.component.custom_id.startswith("my_lvl_"):
            print(f"Received custom_id: {inter.component.custom_id}")
            user_id_part = inter.component.custom_id.split("_")[2]
            print(f"Extracted user_id_part: {user_id_part}")
            if user_id_part.isdigit():
                user_id = int(user_id_part)
                # Здесь ваш код для обработки нажатия на кнопку
                username, points, rank = get_user_stats(bot.db_connection, user_id)
                if username and points and rank:
                # Отправка статистики пользователю
                    await inter.response.send_message(f"Ваше имя: {username}\nВаши кол-во баллов: {points}\nВаше звание: {rank}", ephemeral=True)
                print("Handling button click") # Добавьте это для проверки
        else:
            await inter.response.send_message("Ошибка: неверный формат custom_id.", ephemeral=True)

async def check_and_assign_role(ctx, user_id):
    # Получение текущих баллов пользователя
    cursor = bot.db_connection.cursor()
    cursor.execute("SELECT points FROM users WHERE id = %s", (user_id,))
    points = cursor.fetchone()[0]
    cursor.close()
    
    # Присвоение роли в зависимости от количества баллов
    if points <= 5:
        role_id = "1155888327623442532" # Замените на реальный ID роли
    elif points == 20:
        role_id = "1155888622239744030" # Замените на реальный ID роли
    elif points == 30:
        role_id = "1155888691445768192"
    else:
        return # Если баллов недостаточно, не присваиваем роль
    
    role = ctx.guild.get_role(int(role_id))
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"Вы получили роль {role.name}!")
    else:
        await ctx.send("Ошибка при присвоении роли.")

@bot.command()
async def submit(ctx: commands.Context, *, code: str):
    # Создание файла с кодом
    filename = "user_code.py"
    with open(filename, "w") as file:
        file.write(code)
    
    try:
        # Выполнение теста кода
        result = subprocess.run(["python", "-m", "py_compile", filename], capture_output=True, text=True)
        
        # Удаление временного файла
        os.remove(filename)
        
        # Отправка результата пользователю
        if result.returncode == 0:
            await ctx.send("Код успешно скомпилирован!")
            # Обновление баллов пользователя
            update_user_points(bot.db_connection, ctx.author.id)
            # Проверка и присвоение роли
            await check_and_assign_role(ctx, ctx.author.id)
        else:
            await ctx.send(f"Ошибка компиляции кода:\n{result.stderr}")
    except Exception as e:
        await ctx.send(f"Произошла ошибка при тестировании кода: {e}")
