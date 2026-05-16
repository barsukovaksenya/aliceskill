import json
import logging

logging.basicConfig(level=logging.INFO)
sessionStorage = {}


def handler(request):
    from http.server import BaseHTTPRequestHandler

    class Response:
        def __init__(self, status_code=200, body="", headers=None):
            self.status_code = status_code
            self.body = body
            self.headers = headers or {}

    # GET — health check
    if request.method == 'GET':
        return Response(200, 'OK')

    # POST — обработка запроса от Алисы
    body = json.loads(request.body)
    logging.info(f'Request: {body!r}')

    response = {
        'session': body['session'],
        'version': body['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(body, response)
    logging.info(f'Response: {response!r}')

    return Response(
        status_code=200,
        body=json.dumps(response, ensure_ascii=False),
        headers={'Content-Type': 'application/json'}
    )


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance'].lower() in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо'
    ]:
        res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = True
        return

    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи слона!"
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })

    return suggests