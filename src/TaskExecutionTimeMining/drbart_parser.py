import collections
import numpy as np
import scipy
import math
import json

class Parser:
    def __init__(self, dir : str = '', strict = True):
        self.f_dr_bart_mean = open(dir + 'dr_bart_mean.txt')
        self.f_dr_bart_prec = open(dir + 'dr_bart_prec.txt')
        self.ucut_file = open(dir + 'ucuts.json')
        self.phistar_file = open(dir + 'phistar.json')
        self.encoding_file = open(dir + 'encoding.json')
        self.strict = strict

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
                print(i,j)
                tree = self.parse_tree(f, variables)
                trees.append(tree)
                f.readline()
        return (number_trees, dimensions_x, n_mh_samples), trees

    def parse_tree(self, f, variables):
        num_nodes = int(f.readline())
        nodes = dict()
        for i in range(num_nodes):
            elements = f.readline().split()
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
    
    def parse_encoding(self):
        enc = json.load(self.encoding_file)
        self.encoding_name_to_id = [dict(zip(e, list(range(1,len(e)+1)))) for e in enc]
        self.encoding_id_to_name = [dict(zip(list(range(1,len(e)+1)), e)) for e in enc]
        return self.encoding_name_to_id, self.encoding_id_to_name
    
    def get_encoding(self, x : list):
         if self.strict:
            return [self.encoding_name_to_id[i][j] for i, j in zip(range(len(x)), x)]
         else:
            return [self.encoding_name_to_id[i][j] if i < len(self.encoding_name_to_id) and j in self.encoding_name_to_id[i].keys()
                    else 0
                    for i, j in zip(range(len(x)), x)]
    
    def get_encodings(self, x : list[list]):
        return [self.get_encoding(x_row) for x_row in x]


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
        for des_x, mean_tree in zip(des, self.mean_trees):
            p_i = mean_tree.predict_i(des_x)
            res.append(p_i)
        return res
    
    def predict_prec(self, phi_star : list[float], des : list[list[float]]):
        res = []
        for des_x, prec_tree in zip(des, self.prec_trees):
            p_i = prec_tree.predict_prec_i(des_x)
            res.append(p_i)
        weighted_res = []
        for phi, r in zip(phi_star, res):
            weighted_res.append(phi * r)
        return weighted_res

class DRBART:
    def __init__(self, parser : Parser = None,
                 parser_dir : str = '',
                 strict_parser = True):
        if not parser:
            self.parser = Parser(parser_dir, strict_parser)
        self.mean_cut_variables, self.mean_trees = self.parser.parse_mean()
        self.prec_cut_variables, self.prec_trees = self.parser.parse_prec()
        self.phi_star = self.parser.parse_phistar()
        self.ucuts = self.parser.parse_ucuts()
        self.parser.parse_encoding()
        self.all_trees = AllTrees(self.mean_trees, self.prec_trees)
        

    def _logsumexp(self, tmp):
        m = np.max(tmp, axis=0)
        tmp -= m
        #dirty fix: -inf - (-inf) = 0 and not NaN
        tmp = np.where(np.isnan(tmp), 0, tmp)
        tmp = np.exp(tmp)
        tmp = np.sum(tmp, axis=0)
        tmp = m + np.log(tmp)
        return tmp

    def _dmixnorm(self, ygrid, logprob, sigma, mu):
        res = []
        tmp = np.empty((len(logprob), len(ygrid)))
        for i, (m, s, lp) in enumerate(zip(mu, sigma, logprob)):
            n = scipy.stats.norm.pdf(ygrid, loc=m, scale=s)
            lo = np.log(n)
            r = np.full(len(ygrid), lp) + lo
            tmp[i] = r

        res = self._logsumexp(tmp)
        return res

    def _post_fun(self, ygrid, mus, sigma, logprobs):
        res = []
        for mu_i, sigma_i, logprob_i in zip(mus, sigma, logprobs):
            res.append(self._dmixnorm(ygrid, logprob_i, sigma_i, mu_i))
        return res
    
    def proba(self, ygrid : list[float], x_categorical : list[list], x_continous : list[list]):
        x_rows_decoded = [k[0] + k[1] for k in zip(x_categorical, x_continous)]
        x_encoded_categorical = self.parser.get_encodings(x_categorical)
        x_rows = [k[0] + k[1] for k in zip(x_encoded_categorical, x_continous)]
        res = self.proba_enc(ygrid, x_rows)
        return list(zip(x_rows_decoded, res))

    def sample(self, x_categorical : list, x_continous : list, n : int = 1):
        x_rows_decoded = x_categorical + x_continous
        x_encoded_categorical = self.parser.get_encoding(x_categorical)
        x_rows = x_encoded_categorical + x_continous
        res = self.sample_enc(x_rows, n)
        return (x_rows_decoded, res)

    def proba_enc(self, ygrid : list[float], x_matrix : list[list]):
        logprobs = [np.log(np.diff(np.array([0] + ucuts_i + [1]))) for ucuts_i in self.ucuts ]
        mids = [np.array([0] + ucuts_i) + np.diff(np.array([0] + ucuts_i + [1])) / 2 for ucuts_i in self.ucuts]

        res = []
        for x_row in x_matrix:
            des = [[[m] + x_row for m in mid] for mid in mids]
            mu = self.all_trees.predict(des)

            phi = self.all_trees.predict_prec(self.phi_star, des)
            sigma = [[1 / math.sqrt(p) for p in ph] for ph in phi]
            r = self._post_fun(ygrid, mu, sigma, logprobs)
            probas = np.exp(r)

            r = np.mean(probas, axis=0)
            #mean probs
            res.append(r)
        return res

    def sample_enc(self, x : list, n : int):
        logprobs = [np.log(np.diff(np.array([0] + ucuts_i + [1]))) for ucuts_i in self.ucuts ]
        mids = [np.array([0] + ucuts_i) + np.diff(np.array([0] + ucuts_i + [1])) / 2 for ucuts_i in self.ucuts]

        res = []
        for i in range(n):
            selected_it = np.random.choice(np.arange(len(self.phi_star)), size=1, p=np.array(self.phi_star) / np.sum(self.phi_star))[0]

            pr = [np.exp(lp) for lp in logprobs]
            m = np.random.choice(mids[selected_it], size=1, p=pr[selected_it])[0]
            des = [m] + x

            mean = self.all_trees.mean_trees[selected_it].fit_i(des)
            prec = self.all_trees.prec_trees[selected_it].fit_i_mult(des)
            prec_2 = 1 / math.sqrt(prec)

            r = np.random.normal(loc = mean, scale = prec_2)
            res.append(r)
        return res


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    d = DRBART(parser_dir = '../../models/artificial/resource_concept_duration_seconds-day_resource-count_activity-count/')
    y_grid = np.linspace(0, 100000, 10000)
    x_cat = [['Joe', 'REPAIR',
            #Joe  '1'  Karsten  Jane  Clark
              0,   1,   0,       0,    0,
            #DIAGNOSIS REPAIR
              1,        0],
              ['Joe', 'REPAIR',
            #Joe  '1'  Karsten  Jane  Clark
              0,   0,   0,       1,    0,
            #DIAGNOSIS REPAIR
              1,        0]]
    x_cont = [[3600*8], [3600*8]]
    #h = d.sample(x_cat[0], x_cont[0], 100000)

    #plt.hist(h[1], bins=300, density=True)
    r = d.proba(y_grid, x_cat, x_cont)

    for j, i in r:
        plt.plot(y_grid, i, label=str(j))
    plt.legend(loc="upper left")
    plt.grid(True)
    plt.xlabel("x") 
    plt.ylabel("y")
    #plt.show()
    plt.savefig('test.svg')
    print(r)