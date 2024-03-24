import logging
import sqlite3

from transformers import AutoTokenizer
import requests
from database import is_value_in_table


class GPT:
    def __init__(self, processed_response):
        self.URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.HEADERS = {"Content-Type": "application/json"}
        self.MAX_TOKENS = 200
        self.history = []  # Список для хранения истории общения

    def send_request(self, json):
        resp = requests.post(url=self.URL, headers=self.HEADERS, json=json)
        return resp

    def clear_history(self):
        self.assistant_content = " "
        self.history = []  # Очищаем историю

    def save_history(self, content_response):
        self.assistant_content = content_response  # Сохраняем только последний ответ

    def count_tokens(self):
        tokenizer = AutoTokenizer.from_pretrained("openchat/openchat_3.5")  # название модели
        return len(tokenizer.encode(self))

    @staticmethod
    # Функция получает идентификатор пользователя, чата и самого бота, чтобы иметь возможность отправлять сообщения
    def is_tokens_limit(user_id, chat_id, bot, self):
        if not is_value_in_table('sqlite3.db', 'user_id', user_id):
            return

        session_id = get_user_session_id(user_id)
        tokens_of_session = get_size_of_session(user_id, session_id)

        if tokens_of_session >= self.MAX_TOKENS:
            bot.send_message(chat_id,
                             f'Вы израсходовали все токены в этой сессии. Вы можете начать новую, введя help_with')
        elif tokens_of_session + 50 >= self.MAX_TOKENS:
            bot.send_message(chat_id,
                             f'Вы приближаетесь к лимиту в {self.MAX_TOKENS} токенов в этой сессии. Ваш запрос содержит суммарно {tokens_of_session} токенов.')
        elif tokens_of_session / 2 >= self.MAX_TOKENS:
            bot.send_message(chat_id,
                             f'Вы использовали больше половины токенов в этой сессии. Ваш запрос содержит суммарно {tokens_of_session} токенов.')

    @staticmethod
    # Подсчитывает количество токенов в сессии
    # messages - все промты из указанной сессии
    def count_tokens_in_dialog(messages: sqlite3.Row):
        token = "your_token_here"
        folder_id = "your_folder_id_here"
        MAX_MODEL_TOKENS = 2048

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        data = {
            "modelUri": f"gpt://{folder_id}/yandexgpt/latest",
            "maxTokens": MAX_MODEL_TOKENS,
            "messages": []
        }

        for row in messages:
            data["messages"].append(
                {
                    "role": row["role"],
                    "text": row["content"]
                }
            )

        return len(requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion", json=data,
                                 headers=headers).json()["tokens"])

    # def make_prompt(self, user_request, history):
    #     json = {
    #         "messages": [
    #             {"role": "system", "content": self.system_content},
    #             {"role": "user", "content": user_request},
    #             {"role": "assistant", "content": self.assistant_content}
    #         ]
    #     }
    #     return json
    #
     # Проверка ответа на возможные ошибки и его обработка
    def process_resp(self, request, response) -> str:
        if response.status_code < 200 or response.status_code >= 300:
            self.clear_history()
            logging.error(f"Ошибка получения ответа, статус код: {response.status_code}")
            return f"Ошибка: {response.status_code}"
        try:
            full_response = response.json()
        except:
            self.clear_history()
            return "Ошибка получения JSON"
        if "error" in full_response or 'choices' not in full_response:
            self.clear_history()
            logging.error(f"Обнаружена ошибка в поле 'error' или отсутствует поле 'choices' в ответе")
        response = full_response['choices'][0]['message']['content']
        if response == "":
            logging.error("Обнаружен пустой ответ")
            self.clear_history()
            return "Конец объяснения"
        self.save_history(response)
        return self.assistant_content

    # Выполняем запрос к YandexGPT
    @staticmethod
    def make_prompt(user_request, system_content, assistant_content):
        iam_token = 't1.9euelZqKyZmUnc-am4-OnY_GkMaJmu3rnpWalseZi8qZjJKZyZSJlJKTx8nl8_dVEwNQ-e9OXio5_t3z9xVCAFD5705eKjn-zef1656Vms-OkJSYxpmSzc6RyMfOlIuL7_zF656Vms-OkJSYxpmSzc6RyMfOlIuLveuelZrJkJ2RlMnKlJWPj8_KjIzLkLXehpzRnJCSj4qLmtGLmdKckJKPioua0pKai56bnoue0oye.ZRaLRVkJILN1NMNMWLPu5J3F3L1EkCmJTVEqt9fOQtbpvQEorkjYYePoKjZ7oroi5H7vvgVJRCj9CAq_nDqbCg'  # Токен для доступа к YandexGPT
        folder_id = '<b1gau52co3kb6aqu6u6q>'  # Folder_id для доступа к YandexGPT
        headers = {
            'Authorization': f'Bearer {iam_token}',
            'Content-Type': 'application/json'
        }
        data = {
            "modelUri": f"gpt://{folder_id}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": 2
            },
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_request},
                {"role": "assistant", "content": assistant_content}
            ]
        }
        response = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                                 headers=headers,
                                 json=data)
        if response.status_code == 200:
            text = response.json()["result"]["alternatives"][0]["message"]["text"]
            conn = sqlite3.connect('sqlite3.db')
            cur = conn.cursor()
            cur.execute("INSERT INTO users (user_request, processed_response) VALUES (?, ?)",
                        (user_request, text))
            conn.commit()
            conn.close()
            return text
        else:
            return f"Ошибка при отправке запроса: {response.status_code}"

def get_user_session_id(user_id):
    conn = sqlite3.connect('sqlite3.db')
    c = conn.cursor()
    c.execute("SELECT session_id FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def get_size_of_session(user_id, session_id):
    conn = sqlite3.connect('sqlite3.db')
    c = conn.cursor()
    c.execute("SELECT tokens_used FROM users WHERE user_id = ? AND session_id = ?", (user_id, session_id))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w", )
