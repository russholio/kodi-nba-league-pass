import vars

def findTeamById(id, a):
    for k in a:
        if k == id:
            return a[k]

def findTeamByName(name, a):
    for k in a:
        if a[k] == name:
            return k

class Team():
    def __init__(self, id=None, name='None'):
        self.name = name

        if id != None:
            self.id = id.lower()
            self.name = findTeamById(self.id, vars.teams)
        elif name != 'None':
            self.id = findTeamByName(name, vars.teams)

    def __nonzero__(self):
        return not not self.id

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id

    def __repr__(self):
        return '%s:%s' % (self.id, self.name)