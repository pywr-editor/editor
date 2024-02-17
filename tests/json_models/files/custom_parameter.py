import numpy as np
from pywr.parameters import IndexParameter, Parameter, load_parameter


# noinspection PyAttributeOutsideInit,PyMethodOverriding
class MyParameter(IndexParameter):
    def __init__(self, model, value, **kwargs):
        super().__init__(model, **kwargs)
        self._value = value

    def index(self, timestep, scenario_index):
        return self._value[timestep]

    @classmethod
    def load(cls, model, data):
        value = data.pop("value")
        return cls(model, value, **data)


# noinspection PyArgumentList
MyParameter.register()


# noinspection PyMethodOverriding
class EnhancedMonthlyProfileParameter(Parameter):
    def __init__(self, model, profile, **kwargs):
        super().__init__(model, **kwargs)
        self.profile = profile  # a 12-element list of floats

    def value(self, timestep, scenario_index):
        index = timestep.month - 1  # convert to zero-based index
        return self.profile[index]

    @classmethod
    def load(cls, model, data):
        profile = data.pop("profile")
        return cls(model, profile, **data)


class MyClass:
    pass


# noinspection PyAttributeOutsideInit,PyUnresolvedReferences,PyMethodOverriding
class LicenseParameter(Parameter, MyClass):
    def __init__(self, model, total_volume, **kwargs):
        super().__init__(self, model, **kwargs)
        self.total_volume = total_volume

    def setup(self):
        # allocate an array to hold the parameter state
        num_scenarios = len(self.model.scenarios.combinations)
        self._volume_remaining = np.empty([num_scenarios], np.float64)

    def reset(self):
        # reset the amount remaining in all states to the initial value
        self._volume_remaining[...] = self.total_volume

    def value(self, timestep, scenario_index):
        # return the current volume remaining for the scenario
        return self._volume_remaining[scenario_index.global_id]

    def after(self):
        # update the state
        timestep = self.model.timestepper.current  # get current timestep
        flow_during_timestep = self._node.flow * timestep.days  # see explanation below
        self._remaining -= flow_during_timestep
        self._remaining[self._remaining < 0] = (
            0  # volume remaining cannot be less than zero
        )

    @classmethod
    def load(cls, model, data):
        total_volume = data.pop("total_volume")
        return cls(model, total_volume, **data)


# noinspection PyArgumentList
LicenseParameter.register()


# noinspection PyArgumentList
class SumParameter:
    def __init__(self, model, parameters, **kwargs):
        super().__init__(model, **kwargs)
        self.parameters = parameters
        for parameter in self.parameters:
            self.children.add(parameter)

    def value(self, timestep, scenario_index):
        total_value = sum(
            [parameter.get_value(scenario_index) for parameter in self.parameters]
        )
        return total_value

    @classmethod
    def load(cls, model, data):
        parameters = [
            load_parameter(parameter_data) for parameter_data in data.pop("parameters")
        ]
        return cls(model, parameters, **data)
