#!/usr/bin/env python3

import logging
import os
import sys
import datetime
from threading import Thread

from telegram import ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from functools import wraps

from db import get_id, get_passwd, get_tasks_from_db, remove_task, set_tasks
from moodle_api import login, get_upcoming_tasks_as_text, get_upcoming_tasks, \
    from_dict_to_set

LIST_OF_ADMINS = ["<PUT_YOUR_ADMINS_USER_ID_HERE>"]

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            logger.warning(
                f"Restricted - Unauthorized access denied for {user_id}.")
            return
        return func(update, context, *args, **kwargs)
    return wrapped


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(
                chat_id=update.effective_message.chat_id, action=action)
            return func(update, context,  *args, **kwargs)
        return command_func

    return decorator


@restricted
@send_action(ChatAction.TYPING)
def get_tasks(update, context):
    uuid = update.effective_chat.id
    user_id = get_id(uuid)
    user_passwd = get_passwd(uuid)
    login(user_id, user_passwd)

    message = get_upcoming_tasks_as_text()
    if message is None:
        message = "We might have some network issues, please try again later 😊"
        logger.error(f'Network issues for user {uuid}')
    update.message.reply_text(message, parse_mode='Markdown')


@send_action(ChatAction.TYPING)
def unknown(update, context):
    # For unknown commands
    update.message.reply_text("Sorry, I don't understand this command.")


@send_action(ChatAction.TYPING)
def echo(update, context):
    # For unknown messages
    update.message.reply_text("Say what? 😅")


def callback_find_diff(context: CallbackContext):
    for uuid in LIST_OF_ADMINS:
        user_id = get_id(uuid)
        user_passwd = get_passwd(uuid)
        login(user_id, user_passwd)

        new_tasks = []
        tasks_to_remove = []
        now_tasks = get_upcoming_tasks()

        tasks_from_db = get_tasks_from_db(uuid)
        now_tasks_as_set = from_dict_to_set(now_tasks)

        for task_name in (now_tasks_as_set - tasks_from_db):
            new_tasks.append(task_name)

        for task_name in (tasks_from_db - now_tasks_as_set):
            tasks_to_remove.append(task_name)

        if len(new_tasks) > 0:
            set_tasks(uuid, new_tasks)
            context.bot.send_message(chat_id=uuid,
                                     text='Sending new assignments')
            tasks = []
            for _, task in now_tasks.items():
                name = task['name']
                if [name in new_tasks]:
                    date = task['date']
                    delta = task['delta']
                    tasks.append(f'*{name}* by *{date}*.\n'
                                 f'*{delta}* have left!\n')

            message = '\n'.join(tasks)
            context.bot.send_message(chat_id=uuid,
                                     text=message, parse_mode='Markdown')
        else:
            logger.info(f'There are no new tasks for user id {uuid}')

        for task in tasks_to_remove:
            logger.info(f'Removing {task} for user id {uuid}.')
            remove_task(uuid, task)


def main():
    updater = Updater(
        token='<HERE_IS_YOUR_API_TOKEN>', use_context=True)
    dispatcher = updater.dispatcher
    job_queue = updater.job_queue

    job_queue.run_daily(callback_find_diff, datetime.time(0, 0, 0, 0))

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(update, context):
        update.message.reply_text('Bot is restarting...')
        logger.warning(
            f'User ID {update.effective_chat.id} restarted ArielMoodleBot')
        Thread(target=stop_and_restart).start()

    dispatcher.add_handler(CommandHandler('tasks', get_tasks))
    dispatcher.add_handler(MessageHandler(Filters.text, echo))

    # Admins Command
    dispatcher.add_handler(CommandHandler(
        'r', restart, filters=Filters.user(user_id=LIST_OF_ADMINS)))

    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
