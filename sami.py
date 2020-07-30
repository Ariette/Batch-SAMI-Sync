import re


class Sami():
    def __init__(self, header_str: str, body: list):
        self.header = header_str
        self.list = body

    def shiftStamp(self, offset: float, line_index=0, strip=True):
        header_str = self.header
        body = self.list
        former = body[:line_index]
        later = body[line_index:]
        shift = int(offset * 1000)
        threshold = max([later[0]['startTime'] - shift, 0])
        if strip:
            for (i, value) in enumerate(former):
                former[i] = None if not value['startTime'] < threshold else value
            for (i, value) in enumerate(later):
                later[i] = None if value['startTime'] < shift else value
            former = [i for i in former if i]
            later = [i for i in later if i]
        for (idx, value) in enumerate(later):
            later[idx]['startTime'] = max([later[idx]['startTime'] - shift, 0])
        new_body = former + later
        return Sami(header_str, new_body)

    def changeSpeed(self, rate: int):
        header_str = self.header
        body = self.list
        length = len(body)
        for i in range(0, length):
            body[i]['startTime'] = round(body[i]['startTime'] * rate / 100)
        return Sami(header_str, body)

    def sponsorSwitcher(self, sponsor_time: float, sponsor_text: str, offset: int, ignore_line: int, ignore_time: int, strip: bool):
        length = len(self.list)
        time = ignore_time * 1000
        index = None
        if length < ignore_line:
            raise Exception('자막 길이가 ' + str(ignore_line) + '줄보다 짧습니다.')
        for i in range(ignore_line, length):
            if time < self.list[i]['startTime'] and self.list[i]['content'].find(sponsor_text) != -1:
                index = i + offset
                break
        if index:
            return self.shiftStamp(sponsor_time, index, strip)
        raise Exception('검색 텍스트를 찾을 수 없습니다.')

    def stringify(self):
        body_text = ''.join(map(Sami.formatContent, self.list))
        return self.header + body_text

    @staticmethod
    def parse(raw: str):
        lines = re.split('<SYNC ', raw, 0, re.IGNORECASE)
        regexp = re.compile('^Start=(\d+)><P Class=(\w+)>([\s\S]*)', re.IGNORECASE | re.MULTILINE)
        header_str = lines[0]
        body = []
        for (index, line) in enumerate(lines):
            if index > 0:
                find = regexp.match(line)
                if find is not None:
                    data = {
                        'startTime': int(find.group(1)),
                        'lang': find.group(2),
                        'content': find.group(3) if find.group(3) else ''
                    }
                    body.append(data)
        if not len(body):
            raise Exception('SAMI 파일 읽기 실패')
        body.sort(key=lambda item: (item['startTime'], item['lang']))
        return Sami(header_str, body)

    @staticmethod
    def formatContent(data: dict):
        return '<SYNC Start=' + str(data['startTime']) + '><P Class=' + data['lang'] + '>' + data['content']
