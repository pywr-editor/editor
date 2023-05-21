from pywr.nodes import Link, Node, Output


class LeakyPipe(Node):
    def __init__(self, leakage, leakage_cost=-99999, *args, **kwargs):
        self.allow_isolated = True  # Required for compound nodes

        super(LeakyPipe, self).__init__(*args, **kwargs)

        # Define the internal nodes. The parent of the nodes is defined to identify
        # them as sub-nodes.
        self.inflow = Link(self.model, name="{} In".format(self.name), parent=self)
        self.outflow = Link(self.model, name="{} Out".format(self.name), parent=self)
        self.leak = Output(self.model, name="{} Leak".format(self.name), parent=self)

        # Connect the internal nodes
        self.inflow.connect(self.outflow)
        self.inflow.connect(self.leak)

        # Define the properties of the leak (demand and benefit)
        self.leak.max_flow = leakage
        self.leak.cost = leakage_cost

    def iter_slots(self, slot_name=None, is_connector=True):
        # This is required so that connecting to this node actually connects to the
        # outflow sub-node, and connecting from this node actually connects to the
        # input sub-node
        if is_connector:
            yield self.outflow
        else:
            yield self.inflow

    def after(self, timestep):
        # Make the flow on the compound node appear as the flow _after_ the leak
        self.commit_all(self.outflow.flow)
        # Make sure save is done after setting aggregated flow
        super(LeakyPipe, self).after(timestep)

    @classmethod
    def load(cls, data, model):
        del data["type"]
        leakage = data.pop("leakage")
        leakage_cost = data.pop("leakage_cost", None)
        return cls(model, leakage, leakage_cost, **data)
