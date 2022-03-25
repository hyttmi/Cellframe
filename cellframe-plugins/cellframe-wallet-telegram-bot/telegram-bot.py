############################# TELEGRAM CELLFRAME WALLET INFO BOT #####################################
######################################################################################################
#   JUST DO YOUR OWN TELEGRAM BOT WITH BOTFATHER, USE YOUR API KEY AND YOU'RE GOOD TO GO             #
#   YOU MAY RUN THIS AS STANDALONE SCRIPT OR WITH CELLFRAME NODE (PLACE TO PLUGINS FOLDER)           #
######################################################################################################

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import subprocess

def walletinfo(update, context):
    try:
        wallet_address = str(context.args[0])
        command = "/opt/cellframe-node/bin/cellframe-node-cli wallet info -addr " + wallet_address + " -net subzero"
        cli = subprocess.check_output(command.split())
        output = str(cli, "utf-8")
        output = output.split("\n")
        data = "Address: " + output[0].strip().split()[-1] + "\n"
        data += "Balance: " + output[3].strip() + "\n"
        update.message.reply_text(data)
    except (IndexError, ValueError):
        update.message.reply_text("Bro, you didn't provide your wallet address or your wallet address is wrong!")

def help(update, context):
    update.message.reply_text('''
    Usage:\n
    /walletinfo <walletaddr>''')

updater = Updater('YOURAPIKEY', use_context=True)

updater.dispatcher.add_handler(CommandHandler("walletinfo", walletinfo))
updater.dispatcher.add_handler(CommandHandler("help", help))

updater.start_polling()
updater.idle()

def init():
    return 0


