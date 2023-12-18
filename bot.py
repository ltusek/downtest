import slack
import os
import cfscrape
import execjs
import json
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response

envPath = Path('.') / '.env'
load_dotenv(dotenv_path=envPath)

app = Flask(__name__)

client = slack.WebClient(token=os.environ['slack_token'])

simple_map = {
    'de': 'https://xn--allestrungen-9ib.de',
    'uk': 'https://downdetector.co.uk',
    'us': 'https://downdetector.com',
    'pl': 'https://downdetector.pl',
    'se': 'https://downdetector.se',
    'br': 'https://downdetector.com.br/fora-do-ar/',
}

@ app.route('/downdetector', methods=['POST'])
def downdetector_answer():
    data = request.form
    channel_id = data.get('channel_id')

    passed_strings = data.get('text').split(' ', 1)
    country_code = passed_strings[0]
    search_application = passed_strings[1]
    url = simple_map[country_code] + search_application

    scraper = cfscrape.create_scraper()
    response = scraper.get(url)

    bs = BeautifulSoup(response.text, 'html.parser')
    script = bs.select('script:-soup-contains(chartTranslations)')[0].string

    result = evaluate_javascript(script)

    if response.status_code != 200:
        client.chat_postMessage(channel=channel_id, text=f"Jebiga ne radi scraper2, status code: {response.status_code}")
    
    client.chat_postMessage(channel=channel_id, text=f"Message: gdje si bio 91!")
    return Response(), 200

def evaluate_javascript(js_code):
    # Create a new JavaScript context
    context = execjs.compile('window = {};window.DD={};' + js_code)

    # Evaluate JavaScript code
    json_string = context.eval('JSON.stringify(window.DD.currentServiceProperties)')

    # Parse the JSON string into a Python object
    python_object = json.loads(json_string)

    return python_object
    
if __name__ == "__main__":
    app.run(debug=True)