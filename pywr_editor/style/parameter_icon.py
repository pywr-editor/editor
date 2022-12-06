from pywr_editor.style.icon_with_initials import IconWithInitials


class ParameterIcon(IconWithInitials):
    def __init__(self, parameter_key: str | None):
        """
        Initialises the class.
        :param parameter_key: The parameter key.
        """
        self.parameter_key = parameter_key
        super().__init__(parameter_key, "rectangle")

    def get_color(self) -> str:
        """
        Gets the icon color based on the parameter key. For global or default
        parameters, a default color is used.
        :return: The color name.
        """
        colors = {
            "abstractinterpolated": "slate",
            "abstractthreshold": "red",
            "aggregatedindex": "orange",
            "aggregated": "amber",
            "annualharmonicseries": "indigo",
            "annuallicense": "red",
            "annualexponentiallicense": "blue",
            "annualhyperbolalicense": "zinc",
            "arrayindexed": "purple",
            "arrayindexedscenariomonthlyfactors": "green",
            "arrayindexedscenario": "blue",
            "binarystep": "teal",
            "controlcurveindex": "red",
            "controlcurveinterpolated": "green",
            "controlcurve": "zinc",
            "controlcurvepiecewiseinterpolated": "purple",
            "constant": "cyan",
            "constantscenarioindex": "sky",
            "constantscenario": "amber",
            "currentordinaldaythreshold": "green",
            "currentyearthreshold": "pink",
            "dailyprofile": "purple",
            "dataframe": "blue",
            "deficit": "orange",
            "discountfactor": "sky",
            "division": "rose",
            "flowdelay": "zinc",
            "flow": "fuchsia",
            "hydropowertarget": "lime",
            "index": "sky",
            "indexedarray": "purple",
            "interpolatedflow": "pink",
            "interpolated": "amber",
            "interpolatedquadrature": "lime",
            "interpolatedvolume": "teal",
            "logistic": "pink",
            "max": "yellow",
            "min": "red",
            "monthlyprofile": "stone",
            "multiplethresholdindex": "orange",
            "negativemax": "violet",
            "negativemin": "emerald",
            "negative": "teal",
            "nodethreshold": "indigo",
            "offset": "zinc",
            "threshold": "lime",
            "piecewiseintegral": "green",
            "polynomial1d": "purple",
            "polynomial2dstorage": "amber",
            "rbfprofile": "yellow",
            "recorderthreshold": "teal",
            "rectifier": "rose",
            "scaledprofile": "red",
            "scenariodailyprofile": "stone",
            "scenariomonthlyprofile": "orange",
            "scenarioweeklyprofile": "emerald",
            "storage": "amber",
            "storagethreshold": "rose",
            "tablesarray": "lime",
            "uniformdrawdownprofile": "blue",
            "weeklyprofile": "sky",
        }

        if self.parameter_key in colors:
            return colors[self.parameter_key]
        else:
            return "orange"
