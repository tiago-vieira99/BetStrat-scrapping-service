class Match():

    def __init__(self, date, homeTeam, awayTeam, ftResult, htResult, competition, url):
        self.date = date
        self.homeTeam = homeTeam
        self.awayTeam = awayTeam
        self.ftResult = ftResult
        self.htResult = htResult
        self.competition = competition
        self.url = url

    def to_dict(self):
        return {
            'date': self.date,
            'homeTeam': self.homeTeam,
            'awayTeam': self.awayTeam,
            'ftResult': self.ftResult,
            'htResult': self.htResult,
            'competition': self.competition,
            'url': self.url
        }