import datetime, pytz


class WikiError(object):

    error_type = None
    title = None
    error = None

    def __init__(self):
        self.timestamp = datetime.datetime.now(tz=pytz.timezone('America/Los_Angeles'))
        self.date = self.timestamp.strftime('%Y-%m-%d')

    def format_for_print(self):
        return '{} - {}: {} - {}'.format(
            self.date,
            self.error_type,
            '[[{}]]'.format(self.title) if self.title else '(No title recorded)',
            self.error
        )
