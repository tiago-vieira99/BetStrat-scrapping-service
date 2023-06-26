class Match():

    def __init__(self, date, homeTeam, awayTeam, ftResult, competition):
        self.date = date
        self.homeTeam = homeTeam
        self.awayTeam = awayTeam
        self.ftResult = ftResult
        self.competition = competition

    def to_dict(self):
        return {
            'date': self.date,
            'homeTeam': self.homeTeam,
            'awayTeam': self.awayTeam,
            'ftResult': self.ftResult,
            'competition': self.competition
        }