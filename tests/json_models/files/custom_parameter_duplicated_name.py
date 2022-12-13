from pywr.parameters import Parameter


class MonthlyProfileParameter(Parameter):
    def __init__(self, model, value, **kwargs):
        super().__init__(model, **kwargs)
        self._value = value

    def value(self, ts, scenario_index):
        return self._value[ts]

    @classmethod
    def load(cls, model, data):
        value = data.pop("value")
        return cls(model, value, **data)
