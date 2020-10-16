from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

chatbot = ChatBot('TheBot',
    logic_adapters=[
        'chatterbot.logic.MathematicalEvaluation',
        #'chatterbot.logic.TimeLogicAdapter',
        'chatterbot.logic.BestMatch'
    ])


# Create a new trainer for the chatbot
trainer = ChatterBotCorpusTrainer(chatbot)

# Train the chatbot based on the english corpus
trainer.train("./english")



def talk_to_bot(text):
    return chatbot.get_response(text)

if __name__ == "__main__":
    while True:
        bot_out = talk_to_bot(input('Me: '))
        print(f"TheBot: {bot_out}")