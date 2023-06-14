import io
import re
from bs4 import BeautifulSoup
import urllib3


response = urllib3.request('GET', 'https://rasp.sstu.ru/rasp/teachers')
soup = BeautifulSoup(response.data, 'html.parser')

with io.open("teachers.txt", 'w', encoding='utf8') as f:
    f.write('teacher:\n')
    for tag in soup.find_all('a',  attrs={'href': re.compile("^/rasp/teacher/")}):
        id = tag.get('href').split('/')[3]
        f.write(f'- {tag.getText()}:\n')
        f.write(f'    id: {id}\n')