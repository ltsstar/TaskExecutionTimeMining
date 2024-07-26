import collections
import numpy as np

class Parser:
    def __init__(self):
        self.f_dr_bart_mean = open('dr_bart_mean.txt')
        self.f_dr_bart_prec = open('dr_bart_prec.txt')

    def parse_variables(self, f):
        number_variables = int(f.readline())
        variable_items = collections.defaultdict(list)
        for i in range(number_variables):
            number_items = int(f.readline())
            for j in range(number_items):
                item = float(f.readline())
                variable_items[i].append(item)
            f.readline()
        return variable_items

    def parse_trees(self, f, variables):
        number_trees = int(f.readline()) # x_i
        dimensions_x = int(f.readline()) # p
        n_mh_samples = int(f.readline()) # nd

        trees = []
        for i in range(n_mh_samples):
            for j in range(number_trees):
                tree = self.parse_tree(dimensions_x, f, variables)
                trees.append(tree)
                f.readline()
        return (number_trees, dimensions_x, n_mh_samples), trees

    def parse_tree(self, dimensions_x, f, variables):
        num_nodes = int(f.readline())
        nodes = dict()
        for i in range(num_nodes):
            elements = f.readline().split()
            if len(elements) != dimensions_x:
                raise Exception()
            node = Node(*elements)
            node.cut_value = variables[node.variable][node.cut_point]
            nodes[node.id] = node
            if node.id == 1:
                continue
            if node.id % 2 == 0:
                nodes[node.parent_id].left_child = node
            else:
                nodes[node.parent_id].right_child = node
        return Tree(nodes)


    def parse_mean(self):
        variables = self.parse_variables(self.f_dr_bart_mean)
        self.f_dr_bart_mean.readline()
        tree_variables, trees = self.parse_trees(self.f_dr_bart_mean, variables)
        iterate_trees = [IterateTrees(trees[i:i + tree_variables[0]]) for i in range(0, len(trees), tree_variables[0])]
        return variables, iterate_trees

    def parse_prec(self):
        variables = self.parse_variables(self.f_dr_bart_prec)
        self.f_dr_bart_prec.readline()
        tree_variables, trees = self.parse_trees(self.f_dr_bart_prec, variables)
        iterate_trees = [IterateTrees(trees[i:i + tree_variables[0]]) for i in range(0, len(trees), tree_variables[0])]
        return variables, iterate_trees

class Node:
    def __init__(self, id, variable, cut_point, mu):
        self.id = int(id)
        self.variable = int(variable)
        self.cut_point = int(cut_point)
        self.mu = float(mu)
        self.parent_id = int(self.id/2)
        self.left_child = None
        self.right_child = None

class Tree:
    def __init__(self, nodes):
        self.nodes = nodes

    def get_bottom_node(self, x_row : list[float]):
        current = self.nodes[1]
        previous = None
        while current.left_child != None:
            if x_row[current.variable] < current.mu:
                previous = current
                current = current.left_child
            else:
                previous = current
                current = current.right_child
        return previous

class IterateTrees:
    def __init__(self, trees : list[Tree]):
        self.trees = trees

    def fit_i(self, x_row : list[float]):
        res = 0
        for tree in self.trees:
            res += tree.get_bottom_node(x_row).mu
        return res

    def fit_i_mult(self, x_row : list[float]):
        res = 1
        for tree in self.trees:
            res *= tree.get_bottom_node(x_row)
        return res

    '''
    Generate prediction for the ith mcmc iterate
    '''
    def predict_i(self, desired_x_rows : list[list]):
        res = []
        for x_row in desired_x_rows:
            res.append(self.fit_i(x_row))
        return res

    '''
    Generate prediction for the ith mcmc iterate
    '''
    def predict_prec_i(self, desired_x_rows : list[list]):
        res = collections.defaultdict(lambda: 0)
        for x in desired_x_rows:
            res[x] += fit_i_mult(x)
        return res


class AllTrees:
    def __init__(self, mean_trees : list[IterateTrees], prec_trees : list[IterateTrees]):
        self.mean_trees = mean_trees
        self.prec_trees = prec_trees

    def predict(self, des_x : list[float]):
        res = []
        for mean_tree in mean_trees:
            res.append(mean_tree.predict_i(des_x))
        return res



def proba(x_matrix : list[list], trees : AllTrees, ucuts : list[list[float]]):
    logprobs = [np.diff(np.array([0] + ucuts_i + [1])) for ucuts_i in ucuts ]
    mids = [np.array([0] + ucuts_i) + np.diff(np.array([0] + ucuts_i + [1])) / 2 for ucuts_i in ucuts]

    for x_row in x_matrix:
        phistar = 1

        des = [[[m] + x_row for m in mid] for mid in mids]
        mu = [trees.predict(x) for x in des]

        phi = [
                [phistar[i-1] * predict_prec_i(x) for i in range(1, len(ucuts)+1)]
            for x in x_matrix
            ]
        for ucut in ucuts:
            phistar

if __name__ == '__main__':
    p = Parser()
    mean_cut_variables, mean_trees = p.parse_mean()
    prec_cut_variables, prec_trees = p.parse_prec()
    at = AllTrees(mean_trees, prec_trees)
    ucuts = [[0.0001, 0.0591, 0.1551, 0.2445, 0.2750, 0.3306, 0.3797, 0.4687, 0.6034, 0.7795, 0.7934, 0.9162, 0.9999],
             [0.0001, 0.0591, 0.1551, 0.2445, 0.2528, 0.2750, 0.2806, 0.3306, 0.3797, 0.4687, 0.6034, 0.7795, 0.7934, 0.9162, 0.9999]]
    proba([[10000, 5, 1]], at, ucuts)
    print('suc')