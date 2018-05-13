import json
import requests
from os import path, environ
from mailer import Mailer
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from notifaction import Notification


class Bowling(object):
    def __init__(self):
        try:
            load_dotenv(find_dotenv())
        except Exception:
            print("Could not find .env, rename .env.example and set values")
            exit()

        self.url = environ.get("URL")
        self.save_dir = environ.get("SAVE_DIR")
        self.results_changed = False
        self.results = dict()
        self.get_results()

        self.send_results_email()

    def load(self):
        if not path.isfile(self.save_dir):
            self.results_changed = True
            return None

        with open(self.save_dir) as data_file:
            results = json.load(data_file)

        return results

    def save(self, results):
        previous = self.load()

        if previous:
            results = self.diff_results(previous, results)

        self.results = results

        with open(self.save_dir, 'w') as out:
            out.write(json.dumps(results))

    def diff_results(self, old_results, new_results):
        results = old_results

        for result in new_results.items():
            if not result[0] in results:
                self.results_changed = True
                results[result[0]] = result[1]

        return results

    def get_results(self):
        raw_data = self.get_raw_data()
        data = self.sort_data(raw_data)
        self.save(data)

    def sort_data(self, raw):
        raw = raw.split('<tr')
        raw = raw[1:]

        data = dict()

        for row in raw:
            row_array = row.split('<td>')

            raw_date = row_array[2][:-5]
            split_date = raw_date.split('/')
            day = split_date[0]
            month = split_date[1]
            year = split_date[2]

            if int(day) < 10:
                day = "0{}".format(day)

            date = "{day}/{month}/{year}".format(day=day, month=month, year=year)

            game1 = row_array[4][:-5].replace('*', '')
            game2 = row_array[5][:-5].replace('*', '')
            game3 = row_array[6][:-5].replace('*', '')

            if game1.isdigit() and game2.isdigit() and game3.isdigit():
                data[date] = [game1, game2, game3]

        return data

    def get_raw_data(self):
        page = requests.get(self.url)
        content = str(page.content)

        player = self.url[len(self.url) - 7:]
        player = player.replace('#', '')

        # top_section = content.find('name="{}"'.format(player))
        top_section = content.find(player)

        if top_section == -1:
            print("unable to find player")
            exit()

        content = content[top_section:]

        bottom_section = content.find('</table>')
        if bottom_section == -1: exit()

        content = content[:bottom_section]

        tbody = content.find('<tbody>')
        if tbody == -1: exit()

        content = content[tbody:]

        tbody_end = content.find('</tbody>')
        if tbody_end == -1: exit()

        return content[:tbody_end]

    def average(self):
        total = 0
        count = 0

        for scores in self.results.items():
            total += (int(scores[1][0]) + int(scores[1][1]) + int(scores[1][2]))
            count += 3

        average = int((total / count))
        return "Average score of {} with a total of {} games. \n" \
               "Total pin count is {}.".format(average, count, total)

    def high_game(self):
        highest = 0
        week = ''

        for scores in self.results.items():
            for game in scores[1]:
                if int(game) > highest:
                    highest = int(game)
                    week = scores[0]

        return "Highest game on {} with a score of {}.".format(week, highest)

    def high_series(self):
        highest = 0
        week = ''

        for scores in self.results.items():
            total = (int(scores[1][0]) + int(scores[1][1]) + int(scores[1][2]))
            if int(total) > highest:
                highest = int(total)
                week = scores[0]

        return "Highest series on {} with a total of {}.".format(week, highest)

    def low_game(self):
        lowest = 301
        week = ''

        for scores in self.results.items():
            for game in scores[1]:
                if int(game) < lowest:
                    lowest = int(game)
                    week = scores[0]

        return "Lowest game on {} with a score of {}.".format(week, lowest)

    def running_average(self):
        weeks = 3
        total = 0
        count = 0

        ordered = sorted(self.results.items(), key=lambda t: datetime.strptime(t[0], "%d/%m/%Y").date())

        pre_weeks = ordered[-weeks:]

        for scores in pre_weeks:
            total += (int(scores[1][0]) + int(scores[1][1]) + int(scores[1][2]))
            count += 3

        average = int((total / count))
        return "{} Week running Average of {}. ".format(weeks, average)

    def games_over_amount(self, above):
        total = 0

        for scores in self.results.items():
            for game in scores[1]:
                if int(game) >= above:
                    total += 1

        return "Total of {total} game over {above}.".format(total=total, above=above)

    def series_over_amount(self, above):
        total = 0

        for scores in self.results.items():
            series = (int(scores[1][0]) + int(scores[1][1]) + int(scores[1][2]))
            if series >= above:
                total += 1

        return "{total} series over {above}.".format(total=total, above=above)

    def latest_game(self):
        date = datetime.strptime('01/01/1990', "%d/%m/%Y").date()

        for week in self.results.items():
            week_date = datetime.strptime(week[0], "%d/%m/%Y").date()

            if week_date > date:
                date = week_date

        key = date.strftime('%d/%m/%Y')
        results = self.results[key]
        total = int(results[0]) + int(results[1]) + int(results[2])
        average = int((total / 3))

        return "Latest game on {}, with scores of {}, {}, {}. \n" \
               "Series total of {}. This week average of {}.".format(key, results[0], results[1], results[2], total, average)

    def send_results_email(self):
        methods = {
            'latest_game',
            'average',
            'high_game',
            'low_game',
            'high_series',
            'running_average',
            'series_over_amount:500',
            'series_over_amount:600',
            'series_over_amount:700',
            'games_over_amount:200',
            'games_over_amount:250',
        }

        body = ''

        for method in methods:
            parts = method.split(':')

            if len(parts) > 1:
                body += getattr(self, parts[0])(int(parts[1])) + "\n\n"
            else:
                body += getattr(self, parts[0])() + "\n\n"

        if environ.get("MAIL_SEND", False) != 'False' and self.results_changed:
            Mailer(body)

            if environ.get("SEND_NOTIFICATION", False) != 'False':
                Notification(body, "Bowling Update", environ.get("NOTIFICATION_API"), environ.get("NOTIFICATION_USER"))
        else:
            print(body)


if __name__ == '__main__':
    bowling = Bowling()
