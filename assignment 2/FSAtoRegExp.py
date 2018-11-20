from random import randint
import re


class DSU():  # Disjoint Set Union data structure
    parent = dict()

    def __init__(self, vertexes):
        self.parent = dict([(v, v) for v in vertexes])

    def union_set(self, x, y):
        if x == y:
            return
        x, y = self.find_set(x), self.find_set(y)
        if randint(0, 1):
            self.parent[x] = y
        else:
            self.parent[y] = x

    def find_set(self, x):
        if self.parent[x] == x:
            return x
        self.parent[x] = self.find_set(self.parent[x])
        return self.parent[x]

    def are_in_one_set(self, x, y):
        return self.parent[x] == self.parent[y]

    def are_all_joined(self):
        return len(set([self.find_set(x) for x in self.parent.values()])) == 1


class FSA():  # Finite State Automata
    states = list()
    alpha = list()
    init_st = ""
    fin_st = list()
    trans = list()
    graph = list()  # adjacency matrix
    EPS = "eps"
    EMPTY = "{}"
    reg = None

    def __init__(self, fsa_params):
        states, alpha, init_st, fin_st, trans = fsa_params
        self.states = states
        self.alpha = alpha
        self.init_st = init_st
        self.fin_st = fin_st
        self.trans = trans
        self.create_graph()

    def print(self):
        print(self.states, self.alpha, self.init_st, self.fin_st, self.trans, self.graph)

    def is_s_in_set_of_states(self):  # E1
        return self.init_st in self.states

    def are_all_states_joint(self):  # E2
        dsu = DSU(self.states)
        for tr in self.trans:
            fr, op, to = tr.split(">")
            dsu.union_set(fr, to)
        return dsu.are_all_joined()

    def are_all_transitions_in_alpha(self): # E3
        for tr in self.trans:
            fr, op, to = tr.split(">")
            if op not in self.alpha:
                return (False, op)
        return (True, None)

    def is_init_state_is_defined(self):  # E4
        return bool(self.init_st)

    def is_deterministic(self):  # E6
        n = len(self.states)
        for i in range(n):
            moves_from_i = [op for ops in self.graph[i] for op in ops]
            if len(set(moves_from_i)) != len(moves_from_i) or self.EPS in moves_from_i:
                return False
        return True

    def create_graph(self):
        n = len(self.states)
        self.graph = [[list() for i in range(n)] for j in range(n)]

        for t in self.trans:
            fr, op, to = t.split(">")
            i = self.states.index(fr)
            j = self.states.index(to)
            self.graph[i][j].append(op)

    def to_reg_exp(self):
        n = len(self.states)
        reg = [[[str() for j in range(n)] for i in range(n)] for l in range(n + 1)]

        # Initial regular expressions (k = -1)
        for i in range(n):
            for j in range(n):
                ops = self.graph[i][j]
                if i != j:
                    if not ops:  # ops is empty
                        reg[-1][i][j] = self.EMPTY 
                    else:  # ops has at least one element
                        reg[-1][i][j] = "|".join(ops)
                else:  # i == j
                    if not ops:  # ops is empty
                        reg[-1][i][j] = self.EPS #??????????
                    else:  # ops has at least one element
                        reg[-1][i][j] = "|".join(ops) + "|" + self.EPS

        for k in range(0, n):  # k = -1, 0, 1, ..., (n-1)
            for i in range(n):
                for j in range(n):
                    a = "(" + reg[k - 1][i][k] + ")"
                    b = "(" + reg[k - 1][k][k] + ")*"
                    c = "(" + reg[k - 1][k][j] + ")|"
                    d = "(" + reg[k - 1][i][j] + ")"
                    reg[k][i][j] = a + b + c + d

        res = list()
        i = self.states.index(self.init_st)
        for final in self.fin_st:
            j = self.states.index(final)
            res.append(reg[n - 1][i][j])
        if not self.fin_st:
            return self.EMPTY
        return "|".join(res)


def proceed_data(input_data):
    states = input_data[0].strip()[8:-1].split(',')
    alpha = input_data[1].strip()[7:-1].split(',')
    init_st = input_data[2].strip()[9:-1]
    fin_st = input_data[3].strip()[8:-1].split(',')
    trans = input_data[4].strip()[7:-1].split(',')

    if len(fin_st[0]) == 0:
        del fin_st[0]
    return [states, alpha, init_st, fin_st, trans]


def is_input_file_correct(input_data):  # E5
    if len(input_data) != 5:
        return False

    s_patt = "([0-9A-Za-z]+)"
    t_patt = s_patt + ">\w+>" + s_patt
    states_patt = "states=\{(" + s_patt + ",)*" + s_patt + "\}"
    alpha_patt = "alpha=\{(\w+,)*\w+\}"
    init_st_patt = "init.st=\{" + s_patt + "?\}"
    fin_st_patt = "fin.st=\{((" + s_patt + ",)*" + s_patt + ")?\}"
    trans_patt = "trans=\{((" + t_patt + ")+(," + t_patt + ")*)?\}"

    states_check = re.fullmatch(states_patt, input_data[0])
    alpha_check = re.fullmatch(alpha_patt, input_data[1])
    init_st_check = re.fullmatch(init_st_patt, input_data[2])
    fin_st_check = re.fullmatch(fin_st_patt, input_data[3])
    trans_check = re.fullmatch(trans_patt, input_data[4])

    return states_check and alpha_check and init_st_check and fin_st_check and trans_check


def check_errors(input_data):
    if not is_input_file_correct(input_data):
        return "E5: Input file is malformed"

    fsa = FSA(proceed_data(input_data))
    if not fsa.is_s_in_set_of_states():
        return "E1: A state '{}' is not in set of states".format(fsa.init_st)
    if not fsa.are_all_states_joint():
        return "E2: Some states are disjoint"
    q = fsa.are_all_transitions_in_alpha()
    if not q[0]:
        return "E3: A transition '{}' is not represented in the alphabet".format(q[1])
    if not fsa.is_init_state_is_defined():
        return "E4: Initial state is not defined"
    if not fsa.is_deterministic():
        return "E6: FSA is nondeterministic"

    return fsa


def main():
    fin = open("fsa.txt", "r")
    fout = open("result.txt", "w")
    input_data = [x.strip() for x in fin.readlines()]
    error = check_errors(input_data)

    if type(error) == type(str()):
        output = "Error:\n" + error
    else:
        fsa = error
        output = fsa.to_reg_exp()

    print(output.rstrip(), end="", file=fout)

    fout.close()


main()
