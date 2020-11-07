import getpass
import os
import re
from urllib.parse import unquote

import pdfkit
import requests
from bs4 import BeautifulSoup


def get(session, url, attempts=5, timeout=30, raise_exception=0):
    for attempt in range(attempts):
        try:
            return session.get(url, timeout=timeout, headers={'User-Agent': user_agent, 'Referer': url})
        except requests.exceptions.RequestException as e:
            print(f'Failed to connect (URL: {url})')
            if attempt == attempts - 1:
                print()
                if raise_exception:
                    raise e
                return 0


def valid_name(name):
    return re.sub(r'[\\/:"*?<>|]', '-', name)


def parse_videos(lessons, filename='webinars.txt'):
    with open(filename, 'w') as f:
        for lesson in lessons:
            r = get(s, lesson)
            if r == 0:
                print(f'Failed to get the page (URL: {lesson})\n')
                continue
            page = r.text.replace('<hr>', '\n')
            page = page.replace('<br>', '\n')
            lesson_soup = BeautifulSoup(page, 'html.parser')
            lesson_name = lesson_soup.find('h1').get_text()
            lesson_date = lesson_soup.find('span', class_='val').get_text()
            yt = 'https://youtu.be/' + re.search(r'https://www\.youtube\.com/embed/.{11}', page).group(1)
            print(f'{lesson_name} ({lesson_date}): {yt}', file=f)
            description = lesson_soup.find('div', class_='fr-view')
            if description:
                lines = description.find_all('p')
                if lines:
                    print('\n', file=f)
                    for line in lines:
                        print(line.get_text(), file=f)
                    print('\n', file=f)
            save_materials(page, valid_name(lesson_name))


def save_materials(lesson_page, lesson_name):
    files = re.findall(r'/media/[^"]+\.(?:pdf|docx|doc|jpg|jpeg|png|rar|zip)', lesson_page, re.I)
    if files:
        if not os.path.isdir('extra_materials'):
            os.mkdir('extra_materials')
        os.chdir('extra_materials')
        if not os.path.isdir(lesson_name):
            os.mkdir(lesson_name)
        os.chdir(lesson_name)
        for file in files:
            link = 'https://umschool.net' + unquote(file)
            filename = re.search(r'/[^/"]+\.(?:pdf|docx|doc|jpg|jpeg|png|rar|zip)', unquote(file), re.I).group(0)
            data = get(s, link)
            if data == 0:
                print(f'Failed to download the file (URL: {link})\n')
                continue
            with open(valid_name(filename[1:]), 'wb') as doc:
                doc.write(data.content)
        os.chdir('..')
        os.chdir('..')


def save_homework(homework):
    for assignment in homework:
        r = get(s, assignment)
        if r == 0:
            print(f'Failed to get the page (URL: {assignment})\n')
            continue
        assignment_soup = BeautifulSoup(r.text, 'html.parser')
        try:
            title = assignment_soup.find('span', class_='val').get_text()
        except:
            title = assignment_soup.find('h1').get_text()
        assignment_name = f'{title}.pdf'
        k = 1
        while os.path.isfile(assignment_name):
            assignment_name = f'{title} ({k}).pdf'
            k += 1
        cookies = s.cookies.items()
        options = {'custom-header': [('User-Agent', user_agent)], 'cookie': cookies}
        pdfkit.from_url(assignment, valid_name(assignment_name), options=options)


login_page = 'https://umschool.net/accounts/login/'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 ' \
             'Safari/537.36'
s = requests.Session()

get(s, login_page, raise_exception=1)
csrftoken = s.cookies['csrftoken']
login = input('Login: ')
password = getpass.getpass()
login_data = dict(login=login, password=password, csrfmiddlewaretoken=csrftoken)
r = s.post(login_page, data=login_data, headers={'User-Agent': user_agent, 'Referer': login_page})
if 'Имя пользователя и/или пароль не верны.' in r.text:
    raise Exception('Имя пользователя и/или пароль не верны.')

course_page = input('Enter course page URL: ')
course = get(s, course_page, raise_exception=1)
if course.status_code == 404:
    raise Exception('Invalid URL or no access to the course.')

lessons = ['https://umschool.net' + lesson for lesson in re.findall(r'/\w+/lessons/\d+/', course.text)]
lessons = sorted(set(lessons))

pattern = r'/\w+/lessons/\d+/homework/|/homework/go/\d+/'
homework = ['https://umschool.net' + assignment for assignment in re.findall(pattern, course.text)]
homework = sorted(set(homework))

soup = BeautifulSoup(course.text, 'html.parser')
name = valid_name(soup.find('h1').get_text())
if not os.path.isdir(name):
    os.mkdir(name)
os.chdir(name)

if lessons:
    parse_videos(lessons)

if homework:
    if not os.path.isdir('homework'):
        os.mkdir('homework')
    os.chdir('homework')
    save_homework(homework)
    os.chdir('..')

os.chdir('..')
