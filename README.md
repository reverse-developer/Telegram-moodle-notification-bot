#Telegram-moodle-notification-bot Moodle Bot
@reverse-developer 

Telegram bot for students at any University that uses moodle LMS Platform.  

This bot will update assignment updates, exam reminders (with timer) and grades on excel.
This bot allows you to get your new tasks daily and also get them all right now!

## Setup

1. Get your token api from [BotFather](https://telegram.me/BotFather).
2. Put it on `app.py` instead of `"<HERE_IS_YOUR_API_TOKEN>"`.
3. Get your telegram user id from [userinfobot](https://telegram.me/userinfobot).
4. Put it on `app.py` instead of `"<PUT_YOUR_ADMINS_USER_ID_HERE>"`.
5. On `entry-point.sh` replace `<USER_ID>` with your telegram user id. Also put your ID and your moodle password on `<ID>` and `<MOODLE_PASSWD>` respectively.
6. Build the `Dockerfile` and name it as your wish, for example: `docker build -t uname-moodle-bot .`.
7. Run the image `docker run --rm -ti uname-moodle-bot` :)
