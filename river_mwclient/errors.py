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


class TemplateModifierNotImplemented(NotImplementedError):
    pass
