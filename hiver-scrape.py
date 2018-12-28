import re
from html.parser import HTMLParser
from typing import List
from urllib.request import Request, urlopen

URL = "https://hiverhq.com/"
LIMIT_COUNT = 5


class KeyValue:

    def __init__(self, key: str, value: int):
        self.key = key
        self.value = value

    def __str__(self):
        return f'keyword: {self.key}, count: {self.value}'


def sort_key_value(data: List[KeyValue], first, last):

    if first < last:
        mid = (first + (last - 1)) // 2

        sort_key_value(data, first, mid)
        sort_key_value(data, mid + 1, last)

        merge(data, first, mid, last)

    return data


def merge(data: List[KeyValue], first, mid, last):
    l1 = mid - first + 1
    l2 = last - mid
    t1 = [0] * l1
    t2 = [0] * l2

    for i in range(0, l1):
        t1[i] = data[i + first]

    for j in range(0, l2):
        t2[j] = data[j + mid + 1]

    i = 0
    j = 0
    k = first
    while i < l1 and j < l2:
        if t1[i].value >= t2[j].value:
            data[k] = t1[i]
            i += 1
        else:
            data[k] = t2[j]
            j += 1
        k += 1

    while i < l1:
        data[k] = t1[i]
        i += 1
        k += 1

    while j < l2:
        data[k] = t2[j]
        j += 1
        k += 1


class _HTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.key_values: List[KeyValue] = []
        self._text = []
        self.distinct_words = {}
        self.hide_output = False
        self.i = 0

    @staticmethod
    def is_alpha_numeric(word: str) -> bool:
        for char in list(word):
            ascii_value = ord(char)
            if (48 <= ascii_value <= 57) or (65 <= ascii_value <= 90) or (97 <= ascii_value <= 112):
                return True

        return False

    def handle_data(self, data):
        text = data.strip()
        if text and not self.hide_output:
            self._text.append(re.sub(r'\s+', ' ', text))

            words = text.lower().split()
            for word in words:
                if not self.is_alpha_numeric(word):
                    continue

                if word not in self.distinct_words:
                    self.distinct_words[word] = self.i
                    self.key_values.append(KeyValue(key=word, value=1))

                    self.i += 1
                else:
                    self.key_values[self.distinct_words[word]].value += 1

    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'br') and not self.hide_output:
            self._text.append('\n')
        elif tag in ('script', 'style'):
            self.hide_output = True

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self._text.append('\n')

    def handle_endtag(self, tag):
        if tag == 'p':
            self._text.append('\n')
        elif tag in ('script', 'style'):
            self.hide_output = False

    def text(self):
        return ''.join(self._text).strip()


def hiver_scrape():
    req = Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    web_page = urlopen(req).read().decode()

    try:
        parser = _HTMLParser()
        parser.feed(web_page)
        parser.close()

        sort_key_value(parser.key_values, 0, len(parser.key_values) - 1)

        for key_value in parser.key_values[:LIMIT_COUNT]:
            print(str(key_value))
    except Exception as e:
        print('Error: ', str(e))
        raise


hiver_scrape()
