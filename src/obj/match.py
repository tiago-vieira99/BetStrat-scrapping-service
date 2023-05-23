class Match():

    def __init__(self, date, homeTeam, awayTeam, ftResult):
        self.date = date
        self.homeTeam = homeTeam
        self.awayTeam = awayTeam
        self.ftResult = ftResult

    def to_dict(self):
        return {
            'date': self.date,
            'homeTeam': self.homeTeam,
            'awayTeam': self.awayTeam,
            'ftResult': self.ftResult
        }