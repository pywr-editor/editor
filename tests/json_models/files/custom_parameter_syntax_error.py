from pywr.parameters import IndexParameter


class MyParameter(IndexParameter):
    def __init__(self, model, value, **kwargs):
        super().__init__(model, **kwargs)
        self._value =

    def index(self, timestep, scenario_index):
        return self._value[timestep]

    @classmethod
    def load(cls, model, data):
        value = data.pop("value")
        return cls(model, value, **data)
