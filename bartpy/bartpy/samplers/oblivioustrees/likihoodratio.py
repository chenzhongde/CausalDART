from typing import List

import numpy as np

from bartpy.model import Model
from bartpy.mutation import TreeMutation, GrowMutation, PruneMutation
from bartpy.node import LeafNode, TreeNode
from bartpy.samplers.treemutation import TreeMutationLikihoodRatio
from bartpy.sigma import Sigma
from bartpy.tree import Tree


def log_grow_ratio(combined_node: LeafNode, left_node: LeafNode, right_node: LeafNode, sigma: Sigma, sigma_mu: float):
    #print("enter bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py log_grow_ratio")
    var = np.power(sigma.current_value(), 2)
    var_mu = np.power(sigma_mu, 2)
    n = combined_node.data.X.n_obsv
    n_l = left_node.data.X.n_obsv
    n_r = right_node.data.X.n_obsv

    first_term = (var * (var + n * sigma_mu)) / ((var + n_l * var_mu) * (var + n_r * var_mu))
    first_term = np.log(np.sqrt(first_term))

    left_resp_contribution = np.square(left_node.data.y.summed_y()) / (var + n_l * sigma_mu)
    right_resp_contribution = np.square(right_node.data.y.summed_y()) / (var + n_r * sigma_mu)
    combined_resp_contribution = np.square(combined_node.data.y.summed_y()) / (var + n * sigma_mu)

    resp_contribution = left_resp_contribution + right_resp_contribution - combined_resp_contribution
    output = first_term + ((var_mu / (2 * var)) * resp_contribution)
    #print("-exit bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py log_grow_ratio")
    return output


class UniformTreeMutationLikihoodRatio(TreeMutationLikihoodRatio):

    def __init__(self,
                 prob_method: List[float]=None):
        #print("enter bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio __init__")
        if prob_method is None:
            prob_method = [0.5, 0.5]
        self.prob_method = prob_method

    def log_transition_ratio(self, tree: Tree, mutation: TreeMutation):
        if mutation.kind == "prune":
            mutation: PruneMutation = mutation
            output = self.log_prune_transition_ratio(tree, mutation)
            #print("-exit bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio __init__")
            return output 
        if mutation.kind == "grow":
            mutation: GrowMutation = mutation
            output = self.log_grow_transition_ratio(tree, mutation)
            #print("-exit bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio __init__")
            return output
        else:
            raise NotImplementedError("kind {} not supported".format(mutation.kind))

    def log_tree_ratio(self, model: Model, tree: Tree, mutation: TreeMutation):
        #print("enter bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio log_tree_ratio")
        if mutation.kind == "grow":
            mutation: GrowMutation = mutation
            output = self.log_tree_ratio_grow(model, tree, mutation)
            #print("-exit bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio log_tree_ratio")
            return output
        if mutation.kind == "prune":
            mutation: PruneMutation = mutation
            output = self.log_tree_ratio_prune(model, mutation)
            #print("-exit bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio log_tree_ratio")
            return output

    def log_likihood_ratio(self, model: Model, tree: Tree, proposal: TreeMutation):
        #print("enter bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio log_likihood_ratio")
        if proposal.kind == "grow":
            proposal: GrowMutation = proposal
            log_lik = self.log_likihood_ratio_grow(model, proposal)
        elif proposal.kind == "prune":
            proposal: PruneMutation = proposal
            log_lik = self.log_likihood_ratio_prune(model, proposal)
        #else:
        #    raise NotImplementedError("Only prune and grow mutations supported")
        if type(log_lik) == np.ma.core.MaskedConstant:
            output = -np.inf
            #print("-exit bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio log_likihood_ratio")
            return output
        output = log_lik
        #print("-exit bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio log_likihood_ratio")
        return output

    @staticmethod
    def log_likihood_ratio_grow(model: Model, proposal: TreeMutation):
        #print("enter bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio log_likihood_ratio_grow")
        output = log_grow_ratio(proposal.existing_node, proposal.updated_node.left_child, proposal.updated_node.right_child, model.sigma, model.sigma_m)
        #print("-exit bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio log_likihood_ratio_grow")
        return output

    @staticmethod
    def log_likihood_ratio_prune(model: Model, proposal: TreeMutation):
        #print("enter bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio log_likihood_ratio_prune")
        output = - log_grow_ratio(proposal.updated_node, proposal.existing_node.left_child, proposal.existing_node.right_child, model.sigma, model.sigma_m)
        #print("-exit bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio log_likihood_ratio_prune")
        return output

    def log_grow_transition_ratio(self, tree: Tree, mutation: GrowMutation):
        #print("enter bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio log_grow_transition_ratio")
        prob_prune_selected = - np.log(1)
        prob_grow_selected = log_probability_split_within_tree(tree, mutation)

        prob_selection_ratio = prob_prune_selected - prob_grow_selected
        prune_grow_ratio = np.log(self.prob_method[1] / self.prob_method[0])

        output = prune_grow_ratio + prob_selection_ratio
        #print("-exit bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio log_grow_transition_ratio")
        return output

    def log_prune_transition_ratio(self, tree: Tree, mutation: PruneMutation):
        #print("enter bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio log_prune_transition_ratio")
        prob_selection_ratio = log_probability_split_within_node(GrowMutation(mutation.updated_node, mutation.existing_node))
        grow_prune_ratio = np.log(self.prob_method[0] / self.prob_method[1])

        output = grow_prune_ratio + prob_selection_ratio
        #print("-exit bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio log_prune_transition_ratio")
        return output

    @staticmethod
    def log_tree_ratio_grow(model: Model, tree: Tree, proposal: GrowMutation):
        #print("enter bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio log_tree_ratio_grow")
        denominator = log_probability_node_not_split(model, proposal.existing_node)

        prob_left_not_split = log_probability_node_not_split(model, proposal.updated_node.left_child)
        prob_right_not_split = log_probability_node_not_split(model, proposal.updated_node.right_child)
        prob_updated_node_split = log_probability_node_split(model, proposal.updated_node)
        prob_chosen_split = log_probability_split_within_tree(tree, proposal)
        numerator = prob_left_not_split + prob_right_not_split + prob_updated_node_split + prob_chosen_split

        output = numerator - denominator
        #print("-exit bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio log_tree_ratio_grow")
        return output

    @staticmethod
    def log_tree_ratio_prune(model: Model, proposal: PruneMutation):
        #print("enter bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio log_tree_ratio_prune")
        numerator = log_probability_node_not_split(model, proposal.updated_node)

        prob_left_not_split = log_probability_node_not_split(model, proposal.existing_node.left_child)
        prob_right_not_split = log_probability_node_not_split(model, proposal.existing_node.left_child)
        prob_updated_node_split = log_probability_node_split(model, proposal.existing_node)
        prob_chosen_split = log_probability_split_within_node(GrowMutation(proposal.updated_node, proposal.existing_node))
        denominator = prob_left_not_split + prob_right_not_split + prob_updated_node_split + prob_chosen_split

        output = numerator - denominator
        #print("-exit bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py UniformTreeMutationLikihoodRatio log_tree_ratio_prune")
        return output


def log_probability_split_within_tree(tree: Tree, mutation: GrowMutation) -> float:
    """
    The log probability of the particular grow mutation being selected conditional on growing a given tree
    i.e.
    log(P(mutation | node)P(node| tree)

    """
    #print("enter bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py log_probability_split_within_tree")
    prob_split_chosen = log_probability_split_within_node(mutation)
    output = prob_split_chosen
    #print("-exit bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py log_probability_split_within_tree")
    return output


def log_probability_split_within_node(mutation: GrowMutation) -> float:
    """
    The log probability of the particular grow mutation being selected conditional on growing a given node

    i.e.
    log(P(splitting_value | splitting_variable, node, grow) * P(splitting_variable | node, grow))
    """
    #print("enter bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py log_probability_split_within_node")
    splitting_variable = mutation.updated_node.most_recent_split_condition().splitting_variable
    splitting_value = mutation.updated_node.most_recent_split_condition().splitting_value
    prob_value_selected_within_variable = np.log(mutation.existing_node.data.X.proportion_of_value_in_variable(splitting_variable, splitting_value))
    output = prob_value_selected_within_variable
    #print("-exit bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py log_probability_split_within_node")
    return output


def log_probability_node_split(model: Model, node: TreeNode):
    #print("enter bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py log_probability_node_split")
    output = np.log(model.alpha * np.power(1 + node.depth, -model.beta))
    #print("-exit bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py log_probability_node_split")
    return output


def log_probability_node_not_split(model: Model, node: TreeNode):
    #print("enter bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py log_probability_node_not_split")
    output = np.log(1. - model.alpha * np.power(1 + node.depth, -model.beta))
    #print("-exit bartpy/bartpy/samplers/oblivioustrees/likihoodratio.py log_probability_node_not_split")
    return output
