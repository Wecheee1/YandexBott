  # путь к папке с проектом
iam_token = input("Введите iam: ")
folder_id = input("Введите folder: ")
bot_token = input("Введите botapi: ")

MAX_USERS = 3  # максимальное кол-во пользователей
MAX_GPT_TOKENS = 120  # максимальное кол-во токенов в ответе GPT
COUNT_LAST_MSG = 4  # кол-во последних сообщений из диалога

# лимиты для пользователя
MAX_USER_STT_BLOCKS = 10  # 10 аудиоблоков
MAX_USER_TTS_SYMBOLS = 5000  # 5 000 символов
MAX_USER_GPT_TOKENS = 2000  # 2 000 токенов

user_cols = ['id', 'user_id', 'message', 'role', 'total_gpt_tokens', 'tts_symbols', 'stt_blocks']
LOGS = 'logs.txt'  # файл для логов
DB_FILE = 'messages.db'  # файл для базы данных
SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты веселый собеседник. Общайся с пользователем на "ты" и используй юмор. '
                                            'Поддерживай диалог. Не объясняй пользователю, что ты умеешь и можешь. '
                                            'Изображай человека'}]  # список с системным промтом