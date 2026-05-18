from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}

ANIMALS = ['слон', 'кролик']

ANIMAL_FORMS = {
    'слон': {
        'accusative': 'слона',
        'market_url': 'https://market.yandex.ru/search?text=слон',
    },
    'кролик': {
        'accusative': 'кролика',
        'market_url': 'https://market.yandex.ru/search?text=кролик',
    },
}

AGREEMENT_WORDS = ('ладно', 'куплю', 'покупаю', 'хорошо')


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return jsonify(response)


def reset_suggests(user_id, animal):
    sessionStorage[user_id] = {
        'animal': animal,
        'suggests': [
            "Не хочу.",
            "Не буду.",
            "Отстань!",
        ],
    }


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        reset_suggests(user_id, ANIMALS[0])
        res['response']['text'] = f'Привет! Купи {ANIMAL_FORMS[ANIMALS[0]]["accusative"]}!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    animal = sessionStorage.get(user_id, {}).get('animal', ANIMALS[0])

    utterance_words = req['request']['original_utterance'].lower().split()
    if any(word in utterance_words for word in AGREEMENT_WORDS):
        animal_acc = ANIMAL_FORMS[animal]['accusative']
        market_url = ANIMAL_FORMS[animal]['market_url']

        current_index = ANIMALS.index(animal)
        if current_index + 1 < len(ANIMALS):
            next_animal = ANIMALS[current_index + 1]
            next_animal_acc = ANIMAL_FORMS[next_animal]['accusative']
            reset_suggests(user_id, next_animal)
            res['response']['text'] = (
                f'{animal_acc.capitalize()} можно найти на Яндекс.Маркете! '
                f'А теперь купи {next_animal_acc}!'
            )
            res['response']['buttons'] = [
                {
                    'title': f'Купить {animal_acc}',
                    'url': market_url,
                    'hide': True,
                },
                *get_suggests(user_id),
            ]
            return

        res['response']['text'] = f'{animal_acc.capitalize()} можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = True
        return

    animal_acc = ANIMAL_FORMS[animal]['accusative']
    res['response']['text'] = (
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {animal_acc}!"
    )
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]
    animal = session.get('animal', ANIMALS[0])

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": ANIMAL_FORMS[animal]['market_url'],
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run()