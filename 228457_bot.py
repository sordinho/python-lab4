# Created by Davide Sordi in 14/04/2018 at 13.33
import time
import pymysql

from telegram import ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def read_from_db():
    """
    Reading task list from a DB
    :return: a list of tasks
    """
    lista = list()
    # prepare the query for reading from DB
    query = "SELECT * FROM tasks"

    # connectione to database
    connection = pymysql.connect(user="root", password="sysadmin", host="localhost", database="todolist")

    # get a cursor
    cursor = connection.cursor()

    # execute query
    cursor.execute(query)

    # fetch result from query
    results = cursor.fetchall()
    for result in results:
        print(result[0], result[1])
        lista.append(result[1])

    # close cursor and connection
    cursor.close()
    connection.close()
    return lista


def modify_db(task, cmd):
    """
    function for saving task list on a file
    :param cmd: 1->insert 2->remove tasks
    :param task: new task to insert/delete in DB
    """
    if cmd == 1:
        # insert query
        query = "INSERT INTO tasks (todo) VALUES (%s)"
    elif cmd == 2:
        # delete query
        query = "DELETE FROM tasks WHERE todo=(%s)"

    # connectione to database
    connection = pymysql.connect(user="root", password="sysadmin", host="localhost", database="todolist")
    # get a cursor
    cursor = connection.cursor()
    # parameters for a query must be in a tuple so we execute the quey many times as many parameters there are
    for target in task:
        # execute query
        cursor.execute(query, (target,))
        # commit on DB
        connection.commit()
    # close cursor and connection
    cursor.close()
    connection.close()


def start(bot, received):
    """
    Start function for the telegram bot
    :param bot:
    :param received: received message (probably /start)
    """
    bot.sendChatAction(received.message.chat_id, ChatAction.TYPING)
    received.message.reply_text("Welcome to your Task List bot try /help")


def error_non_command_message(bot, received):
    """
    function for replying to non command messages
    :param bot:
    :param received: received message from user
    """
    bot.sendChatAction(received.message.chat_id, ChatAction.TYPING)
    answer = "Sorry, only command messages are eccepted. Try /help to know more..."
    received.message.reply_text(answer)


def unknown_command(bot, received):
    """
    Function for handling unknown commands
    :param bot:
    :param received:
    """
    bot.sendChatAction(received.message.chat_id, ChatAction.TYPING)
    answer = "Sorry this command is not accepted. Try /help to know more..."
    received.message.reply_text(answer)


def help_the_noob(bot, received):
    """
    Function to show possibles commands to the user
    :param bot:
    :param received:
    :return:
    """
    bot.sendChatAction(received.message.chat_id, ChatAction.TYPING)
    time.sleep(2)
    answer = "Here's a list of accepted commands:\n" \
             "/help I think you know what is\n" \
             "/showTasks will show you the tasks you have to do\n" \
             "/newTask <task to add> insert a new task \n" \
             "/removeTask <task to remove> (you need the exact name of the task)\n" \
             "/removeAllTasks <substring to search in a task to remove> "
    received.message.reply_text(answer)


def show_tasks(bot, received):
    """
    This function will reply to the user with the to-do list or another message if this list is empty
    :param bot:
    :param received:
    """
    bot.sendChatAction(received.message.chat_id, ChatAction.TYPING)
    if len(tasks) > 0:
        # answer formatted with \n
        answer = ""
        for task in tasks:
            tmp1 = answer + task + "\n"
            answer = tmp1
    else:
        answer = "Nothing to do."
    received.message.reply_text(answer)


def insert_new_task(bot, received, args):
    """
    Function for insert a new task to the list and rewrite the list to a new file
    :param bot:
    :param received:
    :param args:
    :return:
    """
    bot.sendChatAction(received.message.chat_id, ChatAction.TYPING)
    if len(args) == 0:
        answer = "You need to specify a task!!!"
    else:
        task = list()
        task.append(" ".join(args))
        tasks.append(task[0])
        answer = "Task inserted successfully"
        modify_db(task, 1)
    received.message.reply_text(answer)


def remove_task(bot, received, args):
    """
    function who remove the specified task
    :param bot:
    :param received:
    :param args:
    :return:
    """
    bot.sendChatAction(received.message.chat_id, ChatAction.TYPING)
    print(len(args))
    if len(args) == 0:
        answer = "You need to specify a task!!!"
    else:
        task_to_rem = list()
        if len(args) == 1:
            task_to_rem.append("".join(args))
        else:
            task_to_rem.append(" ".join(args))
        if task_to_rem[0] in tasks:
            tasks.remove(task_to_rem[0])
            answer = "Task deleted successfully"
            modify_db(task_to_rem, 2)
        else:
            answer = "This task doesn't exists"
    received.message.reply_text(answer)


def remove_all_tasks(bot, received, args):
    """
    this function will remove all tasks containing a string (args see below)
    :param bot:
    :param received:
    :param args: this is a list containing the words of the user's message
    :return:
    """
    bot.sendChatAction(received.message.chat_id, ChatAction.TYPING)
    if len(args) == 0:
        answer = "You need to specify a task!!!"
    else:
        deleted = list()
        if len(args) == 1:
            task_to_rem = "".join(args)
        else:
            task_to_rem = " ".join(args)
        for task in tasks:
            if task_to_rem in task:
                tasks.remove(task)
                deleted.append(task)
        if len(deleted) == 0:
            answer = "No tasks to delete"
        else:
            answer = "The elements " + " and ".join(deleted) + " were successfully removed"
            modify_db(deleted, 2)
    received.message.reply_text(answer)


def main():
    """
    Main function of the bot
    """
    # updater check if there are any updates in telegram chat
    updater = Updater(token='597817386:AAFsTFvxWdAV-824-CQfRBB0TiaLOcqAmqk')

    # read initial task list from a file

    # create a command handler for /start command
    disp = updater.dispatcher
    disp.add_handler(CommandHandler("start", start))

    # message handler for non command messages
    disp.add_handler(MessageHandler(Filters.text, error_non_command_message))

    # help handler for giving hint to noob user :)
    disp.add_handler(CommandHandler("help", help_the_noob))

    # show task command handler
    disp.add_handler(CommandHandler("showTasks", show_tasks))

    # insert new task command handler
    disp.add_handler(CommandHandler("newTask", insert_new_task, pass_args=True))

    # remove task command handler
    disp.add_handler(CommandHandler("removeTask", remove_task, pass_args=True))

    # remove all tasks handler
    disp.add_handler(CommandHandler("removeAllTasks", remove_all_tasks, pass_args=True))

    # handler for unknown commands command is not iterable we use filterd messages
    disp.add_handler(MessageHandler(Filters.command, unknown_command))

    # start requesting information
    updater.start_polling()

    # will handle the stop of the bot
    updater.idle()


# trying for first declaring task list as global variable
# tasks = read_from_file('task_list.txt')
# tasks = ""
# prova commento


if __name__ == '__main__':
    # trying now declaring task list as not too much global var
    tasks = read_from_db()
    main()
