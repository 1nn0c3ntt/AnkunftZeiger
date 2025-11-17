import requests
import datetime
import sys
from dateutil import parser

api_url = "https://start.vag.de/dm/api/v1/abfahrten.json/vgn/1431?timedelay=0&product=Ubahn,Bus,Tram,SBahn,RBahn"


try:
    response = requests.get(api_url)
    response.raise_for_status()

    response_data = response.json()


    if 'Abfahrten' not in response_data:
        print("Ошибка: API ответил, но в нем нет ключа 'Abfahrten'.")
        sys.exit(1)

    departures = response_data['Abfahrten']

    if not departures:
        print("На ближайшее время отправлений нет.")
        sys.exit(0)

    first_departure_time = parser.parse(departures[0]['AbfahrtszeitIst'])
    now = datetime.datetime.now(first_departure_time.tzinfo)

    for dep in departures:
        line = dep['Linienname']

        direction = dep['Richtungstext']

        when_time = parser.parse(dep['AbfahrtszeitIst'])

        delta = when_time - now
        minutes_left = int(delta.total_seconds() / 60)

        if minutes_left <= 0:
            print(f"  {line:>5} -> {direction} - СЕЙЧАС")
        else:
            print(f"  {line:>5} -> {direction} - {minutes_left} мин")

except requests.exceptions.HTTPError as e:
    print(f"Ой, ошибка HTTP: {e}")
except requests.exceptions.RequestException as e:
    print(f"Ой, ошибка сети (не могу подключиться): {e}")
except requests.exceptions.JSONDecodeError:
    print("Ошибка: Не могу расшифровать JSON. Сервер прислал 'сырой' текст:")
    print(response.text)
except (KeyError, IndexError, TypeError):
    print("Ошибка: Получены неверные данные от API (KeyError или TypeError).")
except parser._parser.ParserError:
    print("Ошибка: Не могу распознать формат времени от API.")