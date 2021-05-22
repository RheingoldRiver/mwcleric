from mwclient.errors import AssertUserFailedError


class PageModifierNotImplemented(NotImplementedError):
    pass


class TemplateModifierNotImplemented(NotImplementedError):
    pass


class InvalidUserFile(KeyError):
    pass


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


class InvalidNamespaceName(KeyError):
    pass
