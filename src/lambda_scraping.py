import json
import sys
import urllib.request
import logging

import boto3
from requests_html import HTMLSession

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout)
logger = logging.getLogger(__name__)

BUCKET_NAME = 'poketetsu'
OBJKEY = 'theories.json'
FILEPATH = 'theories.json'
BASE_URL = 'https://yakkun.com' 
PAGE1_URL = '/swsh/theory/list/?start=0&sort=spotlight'
WEBHOOCK_URL = 'https://hooks.slack.com/services/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'

def post_slack(argStr: str) -> None:
    """Post a message to skack webhoock url.
    Args:
        argStr (str):A message to be posted.
    """
    message = argStr
    send_data = {
        "text": message,
    }
    send_text = json.dumps(send_data)
    request = urllib.request.Request(
        WEBHOOCK_URL, 
        data=send_text.encode('utf-8'), 
        method="POST"
    )
    with urllib.request.urlopen(request) as response:
        response_body = response.read().decode('utf-8')
    logger.info('new message is posted as {}'.format(argStr))

def theory_check(theories: dict, page_links: list) -> dict:
    """Add new theories to latest theories.json 
    Args:
        theories (dict): Existing theory names and links
        page_links (list): A list of pager links
    Returns:
        theories (dict): whole theory names and links
        new_theories (dict): new theory names and links
    """
    # theory 一覧の中にスクレイピングしてきた theory 名が無ければ追加
    for page_link in page_links:
        logger.info('pick up theories in {}'.format(page_link))
        page_url ='https://yakkun.com'  + page_link 
        
        response = session.get(page_url)
        contents = response.html.find('#contents', first=True)
        theory_names = contents.find('.next')

        new_theories = {}
        for theory_name in theory_names:
            if theory_name.text not in theories:
                logger.info('New theory {} added'.format(theory_name.text))

                theory_link = base_url + list(theory_name.links)[0]
                theories.setdefault(theory_name.text, theory_link)
                new_theories.setdefault(theory_name.text, theory_link)

            else:
                logging.info('The theory {} already exists'.format(theory_name.text))

    return theories, new_theories


# スクレイピング対象となるページの url を取得
session = HTMLSession()
r = session.get(BASE_URL+PAGE1_URL)
page_elements = r.html.find('#contents > div:nth-child(3) > ul.pager')
for elements in page_elements:
    page_links = elements.links
    page_links.add('/swsh/theory/list/?start=0&sort=spotlight')

# 最新の theory 一覧を S3 から取得
s3 = boto3.resource('s3')
bucket = s3.Bucket(BUCKET_NAME)
bucket.download_file(OBJKEY, FILEPATH)
with open(FILEPATH) as f:
    theories = json.load(f)

theories, new_theories = theory_check(theories, page_links)

# with open('theories.json', 'w') as f:
#     json.dump(theories, f, indent=2, ensure_ascii=False)

obj = s3.Object(BUCKET_NAME,OBJKEY)
r = obj.put(Body=json.dumps(theories, indent=2, ensure_ascii=False))
logger.info('{} is uploaded in {}'.format(BUCKET_NAME, OBJKEY))

if not new_theories:
    logger.info('No new theory exists')
else:
    for k, v in new_theories.items():
        argStr = '{} が育成論に追加されました。リンクはこちら {}'.format(k, v)
        logger.info('new theory:{}, link:{}'.format(k, v))
        post_slack(argStr)