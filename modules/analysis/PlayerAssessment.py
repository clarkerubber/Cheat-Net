class PlayerAssessment:
    def __init__(self, jsonin):
        self.id = jsonin['_id']
        self.gameId = jsonin['gameId']
        self.userId = jsonin['userId']
        self.white = jsonin['white']
        self.assessment = jsonin['assessment']
        self.date = jsonin['date']
        self.sfAvg = jsonin['sfAvg']
        self.sfSd = jsonin['sfSd']
        self.mtAvg = jsonin['mtAvg']
        self.mtSd = jsonin['mtSd']
        self.blurs = jsonin['blurs'] # percentage 0-100 blur rate
        self.hold = jsonin['hold'] # boolean hold alert
        self.flags = PlayerFlags(jsonin['flags'])

class PlayerFlags:
    def __init__(self, jsonin):
        self.jsonin = jsonin
        self.ser = self.get_key('ser') # Suspicious Error Rate
        self.aha = self.get_key('aha') # Always Has Advantage
        self.hbr = self.get_key('hbr') # High Blur Rate
        self.mbr = self.get_key('mbr') # Medium Blur Rate
        self.cmt = self.get_key('cmt') # Consistent Move Times
        self.nfm = self.get_key('nfm') # No Fast Moves
        self.sha = self.get_key('sha') # Suspicious Hold Alert

    def get_key(self, key):
        return self.jsonin.get(key, False)