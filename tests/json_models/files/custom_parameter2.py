from pywr.parameters import DataFrameParameter


class My2Parameter(DataFrameParameter):
    def __init__(self, model, value, **kwargs):
        super().__init__(model, **kwargs)
        self._value = value

    def index(self, timestep, scenario_index):
        return self._value[timestep]

    @classmethod
    def load(cls, model, data):
        value = data.pop("value")
        return cls(model, value, **data)
