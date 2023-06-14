import os

from dotenv import load_dotenv

from modules.Classifier.Classifier import Classifier
from modules.Server.Server import Server
from modules.Utils.utils import text_to_bytes
from modules.VoiceRecog.VoiceRecog import VoiceRecog


# question1 = 'Покажи какое расписание у Бровко Александра Валерьевича'

# command_object = recognize_command(question1)
# entity_object = recognize_entity(question1)

# answer = execute_action(command_object, entity_object)

# print(command_object)
# print(entity_object)
# print(answer)

load_dotenv(".env")

server = Server(int(os.environ.get("SOCKET_SERVER_PORT")))  # type: ignore
voice_recog = VoiceRecog()
classifire = Classifier()

server.add_handler(
    command="recognize",
    handler=lambda handler_object: voice_recog.recognize(
        lambda text: server.send_data(
            connection=handler_object.connection, send_object={"command": "recognizing_end", "body": text}
        )
    ),
)

server.add_handler(
    command="classifier",
    handler=lambda handler_object: classifire.classify(
        handler_object.command,
        handler_object.body,
        callback=lambda answer: server.send_data(
            connection=handler_object.connection, send_object={"command": "classifying_end", "body": answer}
        ),
    ),
)

server.listen()
