from mwclient.errors import AssertUserFailedError


class EsportsCacheKeyError(KeyError):
    def __init__(self, file, value, length, value_table):
        self.file = file
        self.value = value
        self.length = length
        self.value_table = value_table
        self.allowed_keys = value_table.keys()
    
    def __str__(self):
        return "Invalid length of {} requested for {} in {}. Allowed: {}".format(
            self.length,
            self.value,
            self.file,
            ', '.join(self.allowed_keys)
        )


class PageModifierNotImplemented(NotImplementedError):
    pass


class TemplateModifierNotImplemented(NotImplementedError):
    pass


class InvalidUserFile(KeyError):
    pass


class CantFindMatchHistory(KeyError):
    def __str__(self):
        return "Cannot find any valid tournament for provided match history. It may be missing from the MatchSchedule data, or there may be an issue with the parser."


class PatrolRevisionNotSpecified(KeyError):
    pass


class PatrolRevisionInvalid(KeyError):
    pass


class RetriedLoginAndStillFailed(AssertUserFailedError):
    def __init__(self, action, codes):
        self.action = action
        self.codes = codes
        
    def __str__(self):
        return "Tried to re-login but still failed. Attempted action: {}, codes: {}".format(
            self.action, ', '.join(self.codes))
