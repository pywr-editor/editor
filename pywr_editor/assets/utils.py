import inspect
import json
import re
import warnings
from pathlib import Path

import pywr.domains.groundwater
import pywr.nodes
import pywr.parameters
import pywr.parameters.control_curves
import pywr.recorders
import requests as requests

session = requests.Session()


def get_doc_url(module_path: str, name: str) -> str | None:
    """
    Checks that the URL to the pywr documentation exists.
    :param module_path: The module path (for example pywr.parameters).
    :param name: The model component name.
    :return: The URL if it exists, None otherwise.
    """
    doc_url = f"https://pywr.github.io/pywr/api/generated/{module_path}.{name}.html"
    response = session.get(doc_url)
    if response.status_code == 404:
        warnings.warn(f"Cannot find documentation URL for {module_path}.{name}")
        return None
    return doc_url


def get_parameters() -> str:
    """
    Generates a dictionary with the parameter key as index and the parameter
    information and save it as JSON file. The parameter index is the
    lowercase class name. The information contains the class name and its
    formatted name.
    :return: The path to the JSON file.
    """
    parameters_data = {}
    parameters_key_lookup = {}
    param_members = (
        inspect.getmembers(pywr.parameters)
        + inspect.getmembers(pywr.parameters.control_curves)
        # this is not imported in the parameters module
        # + inspect.getmembers(pywr.parameters.groundwater)
        + inspect.getmembers(pywr.parameters.licenses)
    )
    for name, obj in param_members:
        if inspect.isclass(obj):
            # remove abstract classes
            if (
                name
                in [
                    "Parameter",
                    "BaseParameter",
                    "Base",
                    "BaseControlCurveParameter",
                    "IndexParameter",
                    "FunctionParameter",
                    "License",
                    # abstract class
                    "StorageLicense",
                    # not implemented
                    "DailyLicense",
                    # cannot be loaded
                    "TimestepLicense",
                ]
                or "Abstract" in name
            ):
                continue

            # all parameters have the Parameter suffix, except the License parameters
            if "Parameter" in name or "License" in name:
                key = name.lower()
                # remove Parameter at the end of the name
                if name[-9:] == "Parameter":
                    new_key = name[0:-9].lower()
                elif "License" in name:
                    new_key = name.lower()
                else:
                    raise NameError(
                        f"Parameter {name} does not end with 'Parameter' suffix"
                    )

                # parameters can be added with our without the Parameter suffix
                parameters_key_lookup[new_key] = new_key
                parameters_key_lookup[key] = new_key

                module_path = "pywr.parameters"
                if "control_curves" in obj.__module__:
                    module_path = "pywr.parameters.control_curves"

                parameters_data[new_key] = {
                    "class": name,
                    "sub_classes": get_component_subclasses(obj),
                    "name": humanise(name),
                    "doc_url": get_doc_url(module_path, name),
                }

    file = Path(__file__).parent / "pywr_data" / "parameter_data.json"
    with open(file, "w") as f:
        json.dump(
            {
                "parameters_key_lookup": parameters_key_lookup,
                "parameters_data": parameters_data,
            },
            f,
        )

    return str(file)


def get_nodes() -> str:
    """
    Generates a dictionary with the node key as index and the node names as values
    and save it as JSON file. The node index is the lowercase class name. The
    information contains the class name and its formatted name.
    :return: The path to the JSON file.
    """
    to_exclude = [
        "Node",
        "Connectable",
        "DEFAULT_RIVER_DOMAIN",
        "Drawable",
        "Domain",
        "Loadable",
        "StorageInput",
        "StorageOutput",
        "_core",
        "NodeMeta",
        "BaseInput",
        "load_parameter",
        "BaseLink",
        "BaseNode",
        "BaseOutput",
        "Discharge",
        "RiverDomainMixin",
        "ShadowNode",
        "ShadowStorage",
        "interp1d",
    ]
    nodes_data = {}
    for name, obj in inspect.getmembers(pywr.nodes) + inspect.getmembers(
        pywr.domains.groundwater
    ):
        if inspect.isclass(obj):
            if name in to_exclude or "Parameter" in name:
                continue

            nodes_data[name.lower()] = {
                "class": name,
                "sub_classes": get_node_subclasses(obj),
                "name": humanise(name),
            }

    file = Path(__file__).parent / "pywr_data" / "node_data.json"
    with open(file, "w") as f:
        json.dump(nodes_data, f)

    return str(file)


def get_recorders() -> str:
    """
    Generates a dictionary with the recorder key as index and the recorder information
    and save it as JSON file. The recorder index is the lowercase class name. The
    information contains the class name and its formatted name.
    :return: The path to the JSON file.
    """
    to_exclude = [
        # base classes
        "BaseConstantNodeRecorder",
        "BaseConstantParameterRecorder",
        "BaseConstantStorageRecorder",
        "AbstractComparisonNodeRecorder",
        "NumpyArrayAbstractStorageRecorder",
        "Recorder",
        "ParameterRecorder",
        "IndexParameterRecorder",
        # class does not support JSON loading
        "AssertionRecorder",
        "NashSutcliffeEfficiencyNodeRecorder",
        "RMSEStandardDeviationRatioNodeRecorder",
        "PercentBiasNodeRecorder",
        "RootMeanSquaredErrorNodeRecorder",
        "MeanAbsoluteErrorNodeRecorder",
        "MeanSquareErrorNodeRecorder",
        "H5PyRecorder",
    ]
    recorders_key_lookup = {}
    recorders_data = {}
    for name, obj in inspect.getmembers(pywr.recorders):
        if inspect.isclass(obj):
            if name in to_exclude:
                continue

            if "Recorder" in name:
                humanised_name = humanise(name)
                if name == "CSVRecorder":
                    humanised_name = "CSV recorder"
                elif name == "RMSEStandardDeviationRatioNodeRecorder":
                    humanised_name = "RMSE Standard Deviation Ratio Node recorder"
                elif name == "GaussianKDEStorageRecorder":
                    humanised_name = "Gaussian KDE Storage recorder"
                elif name == "NormalisedGaussianKDEStorageRecorder":
                    humanised_name = "Normalised Gaussian KDE Storage recorder"
                elif name == "H5PyRecorder":
                    humanised_name = "H5 recorder"

                key = name.lower()
                new_key = name.lower().replace("recorder", "")

                # recorder can be added with our without the Recorder suffix
                recorders_key_lookup[new_key] = new_key
                recorders_key_lookup[key] = new_key

                recorders_data[new_key] = {
                    "class": name,
                    "name": humanised_name,
                    "sub_classes": get_component_subclasses(obj),
                    "doc_url": get_doc_url("pywr.recorders", name),
                }

    file = Path(__file__).parent / "pywr_data" / "recorder_data.json"
    with open(file, "w") as f:
        json.dump(
            {
                "recorders_key_lookup": recorders_key_lookup,
                "recorders_data": recorders_data,
            },
            f,
        )

    return str(file)


def humanise(label: str) -> str:
    """
    Converts a pascal case string. For example "AbstractInterpolatedParameter"
    returns "Abstract interpolated".
    :param label: The label to convert.
    :return: The formatted label.
    """
    if label == "Polynomial1DParameter":
        return "Polynomial 1D parameter"
    elif label == "Polynomial2DStorageParameter":
        return "Polynomial 2D storage parameter"

    label_list = re.findall("[A-Z][^A-Z]*", label)
    label_list = [name.lower() for name in label_list]
    if len(label_list) <= 1:
        new_label = label.title()
    else:
        label_list[0] = label_list[0].title()
        new_label = " ".join(label_list)

    return new_label


def get_component_subclasses(param_obj: object) -> list[str]:
    """
    Returns the subclasses of a pywr component class.
    :param param_obj: The component class to get the subclasses of.
    :return: A list of subclass names.
    """
    bases = []
    obj = param_obj

    try:
        while obj.__base__.__name__ != "Component":
            bases.append(obj.__base__.__name__)
            obj = obj.__base__
        return bases
    except AttributeError:
        return []


def get_node_subclasses(node_obj: object) -> list[str]:
    """
    Returns the subclasses of a pywr node class.
    :param node_obj: The class to get the subclasses of.
    :return: A list of subclass names.
    """
    bases = []
    obj = node_obj

    try:
        while obj.__base__.__name__ != "AbstractNode":
            name = obj.__base__.__name__
            if name != obj.__name__:
                bases.append(name)
            obj = obj.__base__

        # remove duplicates
        return list(set(bases))
    except AttributeError:
        return []
