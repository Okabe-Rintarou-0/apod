import datetime
import os

import regex
import requests
from bs4 import BeautifulSoup
from markdown import markdownFromFile

if __name__ == '__main__':
    url = 'https://apod.nasa.gov/apod/'
    try:
        r = requests.get(url)
        doc = BeautifulSoup(r.content, parser='html.parser', features="lxml")
        img_ele = doc.find('img')
        org_img_src = f"https://apod.nasa.gov/apod/{img_ele.parent.get('href')}"
        overview_img_src = f"https://apod.nasa.gov/apod/{img_ele.get('src')}"
        explanation_fst_ele = doc.find('b', text=regex.compile('.*Explanation.*'))
        explanation_para_ele = explanation_fst_ele.parent
        explanation = str(explanation_para_ele).replace('\n', ' ')

        markdownFromFile(input='./README.md', output='./tmp.html', output_format='html')
        today_time = datetime.datetime.now().strftime('%Y/%m/%d')

        with open('./tmp.html', 'r') as f:
            doc = BeautifulSoup(f.read(), parser='html.parser', features="lxml")
            details_parent = doc.find('div')
            details = doc.findAll('details')
            summary = None
            if len(details) > 0:
                yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
                yesterday_url = yesterday.strftime("https://apod.nasa.gov/apod/ap%y%m%d.html")
                original = details[0].findAll('td')[1]
                summary = details[0].find('summary').text.strip()
                if summary is not today_time:
                    new_original = BeautifulSoup(f'<td>Original url: <a href="{yesterday_url}">{yesterday_url}</a></td>',
                                                 features="lxml").find(
                        'td')
                    original.replace_with(new_original)

            if summary != today_time:
                today_apod = f'<details>\n' \
                             f'<summary>{today_time}</summary>\n' \
                             f'<table>\n' \
                             f'<tr>\n' \
                             f'<td><a href="{org_img_src}"><img src="{overview_img_src}" alt=""/></a></td>\n' \
                             f'</tr>\n' \
                             f'<tr>\n' \
                             f'<td>Original url: <a href="{url}">{url}</a></td>\n' \
                             f'</tr>\n' \
                             f'<tr>\n' \
                             f'<td>\n' \
                             f'{explanation}\n' \
                             f'</td>\n' \
                             f'</tr>\n' \
                             f'</table>\n' \
                             f'</details>\n'

                details_parent.insert(0, BeautifulSoup(today_apod, features='lxml').find('details'))
                with open('./README.md', 'w') as f:
                    content = f'# apod\n\n' \
                              f'This repo will crawl apod(Astronomy Picture of the Day) from ' \
                              f'https://apod.nasa.gov/apod/ ' \
                              f'every day, using **Github Actions**.\n\n' \
                              f'{details_parent.prettify()}'
                    f.write(content)

        os.remove('./tmp.html')
    except Exception as e:
        print(e)
