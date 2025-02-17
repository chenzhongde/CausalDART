from bartpy.bartpy.node import TreeNode, DecisionNode, LeafNode


class TreeMutation(object):
    """
    An encapsulation of a change to be made to the tree.
    Constructed of three components
      - the node to be changed
      - what it should be changed to
      - a string name of the kind of change (normally grow or prune)
    """

    def __init__(self, kind: str, existing_node: TreeNode, updated_node: TreeNode):
        #print("enter bartpy/bartpy/mutation.py TreeMutation __init__")
        self.kind = kind
        self.existing_node = existing_node
        self.updated_node = updated_node
        #print("-exit bartpy/bartpy/mutation.py TreeMutation __init__")

    def __str__(self):
        #print("enter bartpy/bartpy/mutation.py TreeMutation __str__")
        output = "{} - {} => {}".format(self.kind, self.existing_node, self.updated_node)
        #print("-exit bartpy/bartpy/mutation.py TreeMutation __str__")
        return output


class PruneMutation(TreeMutation):

    def __init__(self, existing_node: DecisionNode, updated_node: LeafNode):
        #print("enter bartpy/bartpy/mutation.py PruneMutation __init__")
        if not type(existing_node) == DecisionNode or not existing_node.is_prunable():
            raise TypeError("Pruning only valid on prunable decision nodes")
        super().__init__("prune", existing_node, updated_node)
        #print("-exit bartpy/bartpy/mutation.py PruneMutation __init__")


class GrowMutation(TreeMutation):

    def __init__(self, existing_node: LeafNode, updated_node: DecisionNode):
        #print("enter bartpy/bartpy/mutation.py GrowMutation __init__")
        if type(existing_node) != LeafNode:
            raise TypeError("Can only grow Leaf nodes")
        super().__init__("grow", existing_node, updated_node)
        #print("-exit bartpy/bartpy/mutation.py GrowMutation __init__")