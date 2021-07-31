import telegram
import time

class telegramBot():

    user_id = -1234567890 # Enter user_id

    def read_token(self, read_txt):
        f = open(f"{read_txt}.txt", "r")
        BOT_TOKEN = f.readline()
        Bot = telegram.Bot(BOT_TOKEN)
        return Bot

    def sendSignal(self,text):
        Bot = self.read_token("Bot_token")
        return Bot.sendMessage(self.user_id, text)

    def sendPic(self):
        return

    def getupdate(self):
        return



if __name__ == "__main__":
    bot = telegramBot()
    text = "Hello World"
    while(True):
        bot.sendSignal(text)