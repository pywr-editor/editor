from dataclasses import dataclass
from typing import TYPE_CHECKING

from pywr_editor.model import NodeConfig

if TYPE_CHECKING:
    from pywr_editor.model import ModelConfig


@dataclass
class Edges:
    model: "ModelConfig"
    """ The ModelConfig instance """

    def get_all(self) -> list[list[str]]:
        """
        Returns the list of edges.
        :return: The edge list. Each list item contains the edges as list.
        """
        return self.model.json["edges"]

    @property
    def count(self) -> int:
        """
        Returns the total number of edges.
        :return: The edges count.
        """
        return len(self.get_all())

    def get_sources(self, node_name: str) -> list[str] | None:
        """
        Returns the source nodes for the target node.
        :param node_name: The name of the source node.
        :return: The list of source node names.
        """
        edges = []
        node_names = self.model.nodes.names
        for edge in self.get_all():
            node_source = edge[0]
            target_node = edge[1]
            if target_node == node_name and node_source in node_names:
                edges.append(edge[0])

        if len(edges) == 0:
            return None

        return edges

    def get_targets(self, node_name: str) -> list[str] | None:
        """
        Returns the target nodes for the source node.
        :param node_name: The name of the source node.
        :return: The list of target node names.
        """
        edges = []
        node_names = self.model.nodes.names
        for edge in self.get_all():
            node_source = edge[0]
            target_node = edge[1]
            if node_source == node_name and target_node in node_names:
                edges.append(edge[1])

        if len(edges) == 0:
            return None

        return edges

    def add(
        self,
        source_node_name: str,
        target_node_name: str,
    ) -> None:
        """
        Adds a new edge.
        :param source_node_name: The name of the source node.
        :param target_node_name: The name of the source node.
        :return: None
        """
        self.model.json["edges"].append([source_node_name, target_node_name])
        self.model.changes_tracker.add(
            f"Added new edge from '{source_node_name}' "
            + f"to '{target_node_name}'"
        )

    def delete(
        self,
        source_node_name: str | None = None,
        target_node_name: str | None = None,
    ) -> None:
        """
        Deletes an edge by matching:
          - source node name: delete all edges whose source node matches the
            provided name.
          - target node name: delete all edges whose target node matches the
            provided name.
          - source and target node names: delete the edge with the provided
            source and target node names.
        :param source_node_name: The source node name. Optional
        :param target_node_name: The target node name. Optional.
        :return: None
        """
        if source_node_name is None and target_node_name is None:
            return

        # collect the edges to preserve, do not recursively delete items from list
        if target_node_name is None:
            edges_to_keep = [
                edge for edge in self.get_all() if edge[0] != source_node_name
            ]
        elif source_node_name is None:
            edges_to_keep = [
                edge for edge in self.get_all() if edge[1] != target_node_name
            ]
        # delete a specific edge (ignore slots)
        else:
            edges_to_keep = [
                edge
                for edge in self.get_all()
                if edge[0:2] != [source_node_name, target_node_name]
            ]

        deleted_edges = [  # for change log only
            item for item in self.get_all() if item not in edges_to_keep
        ]
        self.model.changes_tracker.add(f"Deleted edge(s) {deleted_edges}")
        self.model.json["edges"] = edges_to_keep

    def get_edge_color(self, source_node_name: str) -> str | None:
        """
        Returns the color to use for the edge, if this is set in the edge_color
        property for a source node.
        :param source_node_name: The node name.
        :return: The color name to use if available, None otherwise.
        """
        node_config = self.model.nodes.get_node_config_from_name(
            source_node_name
        )
        if node_config is not None:
            return NodeConfig(node_config).edge_color
        return None

    def find_edge_by_index(
        self, source_node_name: str, target_node_name: str
    ) -> tuple[list, int] | tuple[None, None]:
        """
        Finds the edge list and its index from the source and target node names.
        :param source_node_name: The name of the source node.
        :param target_node_name:  The name of the target node.
        :return: The edge and its index or None if the edge is not found.
        """
        for ei, edge in enumerate(self.get_all()):
            if edge[0:2] == [source_node_name, target_node_name]:
                return edge, ei
        return None, None

    def get_slot(
        self,
        source_node_name: str,
        target_node_name: str,
        slot_pos: int,
    ) -> str | int | None:
        """
        Returns the name of the slot for the edge identified by the source and target
        node names.
        :param source_node_name: The name of the source node.
        :param target_node_name:  The name of the target node.
        :param slot_pos: The slot position, 1 to set the source node slot, 2 for the
        target node.
        :return: The slot name or None if this is not available.
        """
        if slot_pos not in [1, 2]:
            raise ValueError("slot_pos can only be 1 or 2")
        edge, _ = self.find_edge_by_index(source_node_name, target_node_name)

        try:
            return edge[slot_pos + 1]
        except (IndexError, TypeError):
            return None

    def set_slot(
        self,
        source_node_name: str,
        target_node_name: str,
        slot_pos: int,
        slot_name: str | int | None,
    ) -> None:
        """
        Sets the slot name for an edge. The edge is identified by its source and target
        node names.
        :param source_node_name: The name of the source node.
        :param target_node_name:  The name of the target node.
        :param slot_pos: The slot position, 1 to set the source node slot, 2 for the
        target node.
        :param slot_name: The name of the slot. If is None, the slot is removed.
        :return: None
        """
        if slot_pos not in [1, 2]:
            raise ValueError("slot_pos can only be 1 or 2")

        # only strings or integers are allowed
        if slot_name is not None and not isinstance(slot_name, (str, int)):
            return

        # handle empty strings
        if slot_name is not None and isinstance(slot_name, str):
            slot_name = slot_name.strip()
        if slot_name == "":
            slot_name = None

        edge, ei = self.find_edge_by_index(source_node_name, target_node_name)
        if edge:
            # no slots are set
            if len(edge) == 2:
                if slot_name is None:
                    # slot already empty
                    return
                elif slot_pos == 1:
                    self.model.json["edges"][ei].append(slot_name)
                elif slot_pos == 2:
                    self.model.json["edges"][ei] += [None, slot_name]
            elif len(edge) == 3:
                if slot_pos == 1:
                    if slot_name is None:
                        self.model.json["edges"][ei] = [
                            source_node_name,
                            target_node_name,
                        ]
                    else:
                        self.model.json["edges"][ei][2] = slot_name
                elif slot_pos == 2:
                    if slot_name is not None:
                        self.model.json["edges"][ei].append(slot_name)
            elif len(edge) == 4:
                if slot_name is None:
                    if slot_pos == 1:
                        if edge[3] is not None:  # last slot is not None
                            self.model.json["edges"][ei][2] = None
                        else:
                            self.model.json["edges"][ei] = [
                                source_node_name,
                                target_node_name,
                            ]
                    elif slot_pos == 2:
                        if edge[2] is not None:  # first slot is not None
                            self.model.json["edges"][ei] = edge[0:3]
                        else:
                            self.model.json["edges"][ei] = [
                                source_node_name,
                                target_node_name,
                            ]
                else:
                    self.model.json["edges"][ei][1 + slot_pos] = slot_name

            self.model.changes_tracker.add(
                f"Changed slot '{slot_name}' at position {slot_pos} for ["
                + f"{source_node_name}, {target_node_name}]"
            )

            return
