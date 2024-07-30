import collections
import numpy as np
import scipy
import math
import json

class Parser:
    def __init__(self):
        self.f_dr_bart_mean = open('dr_bart_mean.txt')
        self.f_dr_bart_prec = open('dr_bart_prec.txt')
        self.ucut_file = open('ucuts.json')
        self.phistar_file = open('phistar.json')

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
    
    def parse_ucuts(self):
        return json.load(self.ucut_file)

    def parse_phistar(self):
        return json.load(self.phistar_file)

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
        while current != None:
            if x_row[current.variable] < current.cut_value:
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
            bn = tree.get_bottom_node(x_row)
            res += bn.mu
        return res

    def fit_i_mult(self, x_row : list[float]):
        res = 1
        for tree in self.trees:
            bn = tree.get_bottom_node(x_row)
            res *= bn.mu
        return res

    '''
    Generate prediction for the ith mcmc iterate
    '''
    def predict_i(self, desired_x_rows : list[list]):
        res = []
        for x_row in desired_x_rows:
            r = self.fit_i(x_row)
            res.append(r)
        return res

    '''
    Generate prediction for the ith mcmc iterate
    '''
    def predict_prec_i(self, desired_x_rows : list[list]):
        print('predict_prec_i')
        res = []
        for x_row in desired_x_rows:
            r = self.fit_i_mult(x_row)
            res.append(r)
        return res


class AllTrees:
    def __init__(self, mean_trees : list[IterateTrees], prec_trees : list[IterateTrees]):
        self.mean_trees = mean_trees
        self.prec_trees = prec_trees

    def predict(self, des : list[list[float]]):
        res = []
        for des_x, mean_tree in zip(des, mean_trees):
            p_i = mean_tree.predict_i(des_x)
            res.append(p_i)
        return res
    
    def predict_prec(self, phi_star : list[float], des : list[list[float]]):
        res = []
        for des_x, prec_tree in zip(des, prec_trees):
            p_i = prec_tree.predict_prec_i(des_x)
            res.append(p_i)
        weighted_res = []
        for phi, r in zip(phi_star, res):
            weighted_res.append(phi * r)
        return weighted_res

def logsumexp(tmp):
    m = max(tmp)
    res = 0
    for t in tmp:
        res += np.exp(t - m)
    return m + np.log(res)

def dmixnorm(ygrid, logprob, sigma, mu):
    res = []
    for y in ygrid:
        tmp = []
        for m, s, lp in zip(mu, sigma, logprob):
            r = lp + np.log(scipy.stats.norm.pdf(y, loc=m, scale=s))
            tmp.append(r)
        res.append(logsumexp(tmp))
    return res

def post_fun(ygrid, mus, sigma, logprobs):
    res = []
    for mu_i, sigma_i, logprob_i in zip(mus, sigma, logprobs):
        res.append(dmixnorm(ygrid, logprob_i, sigma_i, mu_i))
    return res


def proba(ygrid : list[float], x_matrix : list[list], trees : AllTrees, ucuts : list[list[float]], phi_star : list[float]):
    logprobs = [np.log(np.diff(np.array([0] + ucuts_i + [1]))) for ucuts_i in ucuts ]
    mids = [np.array([0] + ucuts_i) + np.diff(np.array([0] + ucuts_i + [1])) / 2 for ucuts_i in ucuts]

    res = []
    for x_row in x_matrix:
        des = [[[m] + x_row for m in mid] for mid in mids]
        mu = trees.predict(des)

        phi = trees.predict_prec(phi_star, des)
        sigma = [[1 / math.sqrt(p) for p in ph] for ph in phi]
        r = post_fun(ygrid, mu, sigma, logprobs)
        probas = np.exp(r)

        r = np.mean(probas, axis=0)
        #mean probs
        res.append(r)
    return res

if __name__ == '__main__':
    p = Parser()
    mean_cut_variables, mean_trees = p.parse_mean()
    prec_cut_variables, prec_trees = p.parse_prec()
    phi_star = p.parse_phistar()
    ucuts = p.parse_ucuts()
    at = AllTrees(mean_trees, prec_trees)
    y_grid = np.linspace(0, 500, 250)
    x = [[10000, 5, 1], [300000, 5, 1]]
    r = proba(y_grid, x, at, ucuts, phi_star)

    import matplotlib.pyplot as plt
    for i, j in zip(r, x):
        plt.plot(y_grid, i, label=str(j))
    plt.legend(loc="upper left")
    plt.grid(True)
    plt.xlabel("x") 
    plt.ylabel("y")
    #plt.show()
    plt.savefig('test1.png')
    print(r)