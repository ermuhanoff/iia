import datetime
import urllib3
from bs4 import BeautifulSoup, NavigableString, Tag

class HtmlParser:
    @staticmethod
    def __parse_childer(childer, callback) -> None:
        for c in childer:
            if isinstance(c, NavigableString):
                continue
            if isinstance(c, Tag):
                callback(c)

    @staticmethod
    def get_rasp(entity_group: str, entity_id: int, is_now: str) -> str:
        def parse_week_tag(tag: Tag, output):
            HtmlParser.__parse_childer(tag.children, lambda tag : parse_day_tag(tag, output))
            
        def parse_day_tag(tag: Tag, output):
            if 'day-header-color-blue' not in tag.get('class'):  # type: ignore
                    HtmlParser.__parse_childer(tag.children, lambda tag : parse_lessons_tags(tag, output))

        def parse_lessons_tags(tag: Tag, output):
            if 'day-header' in tag.get('class') and is_now == None: # type: ignore
                output['str'] += f'\n{tag.contents[0].contents[1]} ({tag.contents[0].contents[0].getText()})' # type: ignore
            if 'day-lesson' in tag.get('class') and 'day-lesson-empty' not in tag.get('class'): # type: ignore
                HtmlParser.__parse_childer(tag.children, lambda tag : parse_lesson_tag(tag, output))

        def parse_lesson_tag(tag: Tag, output):
            output['str'] += f'\n\t{tag.contents[0].contents[0]} | {tag.contents[1].getText()} | {tag.contents[2].getText()} {tag.contents[4].getText()}' # type: ignore
            if entity_group == 'group':
                output['str'] += f'\n\t\tПреподаватель: {tag.contents[5].getText()}'

        def parse_day_tag_by_time(tag: Tag, output, time_minute: int):
            HtmlParser.__parse_childer(tag.children, lambda tag : pars_lessons_tags_by_time(tag, output, time_minute))

        def pars_lesson_tag_by_time(tag: Tag, output, time_minute: int):
            left, right = tag.contents[0].contents[0].split(' - ') # type: ignore

            left_hour, left_minute = left.split(':')
            right_hour, right_minute = right.split(':')

            left_bound = int(left_hour) * 60 + int(left_minute)
            righ_bound = int(right_hour) * 60 + int(right_minute)

            if time_minute >= left_bound and time_minute <= righ_bound:
                parse_lesson_tag(tag, output)
        
        def pars_lessons_tags_by_time(tag: Tag, output, time_minute: int):
            if 'day-lesson' in tag.get('class') and 'day-lesson-empty' not in tag.get('class'):  # type: ignore
                HtmlParser.__parse_childer(tag.children, lambda tag : pars_lesson_tag_by_time(tag, output, time_minute))

        response = urllib3.request('GET', f'https://rasp.sstu.ru/rasp/{entity_group}/{entity_id}')
        soup = BeautifulSoup(response.data, 'html.parser')
        output = { 'str': '' }

        if is_now == 'day':
            tag = soup.find('div', attrs={'class': 'day-current'})
            parse_day_tag(tag, output)  # type: ignore
        elif is_now == 'time':
            now = datetime.datetime.now()
            now_hour = now.hour
            now_minute = now.minute

            tag = soup.find('div', attrs={'class': 'day-current'})
            parse_day_tag_by_time(tag, output, now_hour * 60 + now_minute)  # type: ignore
        else:
            tag = soup.find('div', attrs={'class': 'calendar'})
            HtmlParser.__parse_childer(tag.children, lambda tag : parse_week_tag(tag, output))  # type: ignore

        return output['str']
        