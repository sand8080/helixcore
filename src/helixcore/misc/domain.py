
class DomainName(object):
    def __init__(self, name, zone):
        self.name = name
        self.zone = zone

    @classmethod
    def parse(cls, fullname):
        '''@return DomainName'''
        n, z = fullname.split('.', 1)
        return DomainName(n, z)

    def __str__(self):
        return self.name + '.' + self.zone
