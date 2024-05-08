from peremen import *
from database import *
from Yangpt import *
from creds import get_creds
import math
from peremen import *

logging.basicConfig(filename=LOGS, level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")


# получаем количество уникальных пользователей, кроме самого пользователя
def check_number_of_users(user_id):
    count = count_users(user_id)
    if count is None:
        return False, "Ошибка при работе с БД"
    if count > MAX_USERS:
        return False, "Превышено максимальное количество пользователей"
    return True, ""

# проверяем, не превысил ли пользователь лимиты на общение с GPT
def is_gpt_token_limit(messages, total_spent_tokens):
    all_tokens = count_gpt_tokens(messages) + total_spent_tokens
    if all_tokens > MAX_USER_GPT_TOKENS:
        return None, f"Превышен общий лимит GPT-токенов {MAX_USER_GPT_TOKENS}"
    return all_tokens, ""

# проверяем, не превысил ли пользователь лимиты на преобразование аудио в текст
def is_stt_block_limit(user_id, duration):
    global all_blocks
    # Переводим секунды в аудиоблоки
    audio_blocks = math.ceil(duration/15) # округляем в большую сторону
    # Функция из БД для подсчёта всех потраченных пользователем аудиоблоков
    all_blocks = count_all_blocks(user_id) + audio_blocks

    # Проверяем, что аудио длится больше 30 секунд
    if duration >= 30:
        return "Слишком большое аудио", False

    # Сравниваем all_blocks с количеством доступных пользователю аудиоблоков
    if all_blocks > MAX_USER_STT_BLOCKS:
        return "Превышенно максимальное возможное количество аудио блоков", False
    return audio_blocks, True


# проверяем, не превысил ли пользователь лимиты на преобразование текста в аудио
def is_tts_symbol_limit(user_id, text):
    text_symbols = len(text)

    # Функция из БД для подсчёта всех потраченных пользователем символов
    all_symbols = count_all_blocks_tts(user_id) + text_symbols

    # Сравниваем all_symbols с количеством доступных пользователю символов
    if all_symbols >= MAX_USER_TTS_SYMBOLS:
        msg = f"Превышен общий лимит SpeechKit TTS {MAX_USER_TTS_SYMBOLS}. Использовано: {all_symbols} символов. Доступно: {MAX_USER_TTS_SYMBOLS - all_symbols}"
        return 0, False

    # Сравниваем количество символов в тексте с максимальным количеством символов в тексте
    if text_symbols >= MAX_USER_TTS_SYMBOLS:
        msg = f"Превышен лимит SpeechKit TTS на запрос {MAX_USER_TTS_SYMBOLS}, в сообщении {text_symbols} символов"
        return 0, False
    return True, len(text)

def speech_to_text(data):
    # Указываем параметры запроса
    params = "&".join([
        "topic=general",  # используем основную версию модели
        f"folderId={folder_id}",
        "lang=ru-RU"  # распзнаём голосовое сообщение на русском языке
    ])

    # Аутентификация через IAM-токен
    headers = {
        'Authorization': f'Bearer {iam_token}',
    }

    # Выполняем запрос
    response = requests.post(
        f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}",
        headers=headers,
        data=data
    )

    # Читаем json в словарь
    decoded_data = response.json()
    # Проверяем, не произошла ли ошибка при запросе
    if decoded_data.get("error_code") is None:
        return True, decoded_data.get("result")  # Возвращаем статус и текст из аудио
    else:
        return False, "При запросе в SpeechKit возникла ошибка"

def text_to_speech(text):
    # iam_token, folder_id для доступа к Yandex SpeechKit
    # Аутентификация через IAM-токен
    headers = {
        'Authorization': f'Bearer {iam_token}',
    }
    data = {
        'text': text,  # текст, который нужно преобразовать в голосовое сообщение
        'lang': 'ru-RU',  # язык текста - русский
        'voice': 'filipp',  # мужской голос Филиппа
        'folderId': folder_id,
    }
    # Выполняем запрос
    response = requests.post(
        'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize',
        headers=headers,
        data=data
    )
    if response.status_code == 200:
        return True, response.content  # возвращаем статус и аудио
    else:
        return False, "При запросе в SpeechKit возникла ошибка"
