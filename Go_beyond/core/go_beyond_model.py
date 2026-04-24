import random
from typing import Dict, Iterable, List, Sequence, Set, Tuple

import numpy as np


class SimplagionModelHigherOrder:
    """Higher-order contagion model up to dimension 3."""

    def __init__(
        self,
        node_neighbors_dict: Dict[int, Iterable[int]],
        triangles_list: Sequence[Sequence[int]],
        tetrahedra_list: Sequence[Sequence[int]],
        I_percentage: float,
    ):
        self.neighbors_dict = {
            int(node): tuple(sorted(set(neighbors)))
            for node, neighbors in node_neighbors_dict.items()
        }
        self.nodes = sorted(self.neighbors_dict.keys())
        self.N = len(self.nodes)
        self.triangles_list = [tuple(sorted(map(int, tri))) for tri in triangles_list]
        self.tetrahedra_list = [tuple(sorted(map(int, tet))) for tet in tetrahedra_list]
        self.I = int(I_percentage * self.N / 100)
        self.initial_infected_nodes = self.initial_setup()

    def initial_setup(self, fixed_nodes_to_infect=None):
        self.sAgentSet: Set[int] = set(self.nodes)
        self.iAgentSet: Set[int] = set()
        self.iList: List[int] = []
        self.t = 0

        infected_this_setup = []
        if fixed_nodes_to_infect is None:
            n_initial = min(self.I, self.N)
            for _ in range(n_initial):
                to_infect = random.choice(list(self.sAgentSet))
                self.infectAgent(to_infect)
                infected_this_setup.append(to_infect)
        else:
            for to_infect in fixed_nodes_to_infect:
                if to_infect in self.sAgentSet:
                    self.infectAgent(to_infect)
                    infected_this_setup.append(to_infect)
        return infected_this_setup

    def reset(self):
        return self.initial_setup(fixed_nodes_to_infect=self.initial_infected_nodes)

    def infectAgent(self, agent: int):
        self.iAgentSet.add(agent)
        self.sAgentSet.remove(agent)
        return 1

    def recoverAgent(self, agent: int):
        self.sAgentSet.add(agent)
        self.iAgentSet.remove(agent)
        return -1

    def run(self, t_max, beta1, beta2, beta3, mu, print_status=False):
        self.t_max = t_max

        while (
            len(self.iAgentSet) > 0
            and len(self.sAgentSet) > 0
            and self.t <= self.t_max
        ):
            newIlist = set()

            for iAgent in tuple(self.iAgentSet):
                for agent in self.neighbors_dict[iAgent]:
                    if agent in self.sAgentSet and random.random() <= beta1:
                        newIlist.add(agent)

            if beta2 > 0:
                for n1, n2, n3 in self.triangles_list:
                    infected = [n1 in self.iAgentSet, n2 in self.iAgentSet, n3 in self.iAgentSet]
                    if sum(infected) == 2:
                        if not infected[0] and n1 in self.sAgentSet and random.random() <= beta2:
                            newIlist.add(n1)
                        elif not infected[1] and n2 in self.sAgentSet and random.random() <= beta2:
                            newIlist.add(n2)
                        elif not infected[2] and n3 in self.sAgentSet and random.random() <= beta2:
                            newIlist.add(n3)

            if beta3 > 0:
                for tetrahedron in self.tetrahedra_list:
                    infected_nodes = [node for node in tetrahedron if node in self.iAgentSet]
                    susceptible_nodes = [node for node in tetrahedron if node in self.sAgentSet]
                    if len(infected_nodes) == 3 and len(susceptible_nodes) == 1:
                        if random.random() <= beta3:
                            newIlist.add(susceptible_nodes[0])

            for n_to_infect in newIlist:
                if n_to_infect in self.sAgentSet:
                    self.infectAgent(n_to_infect)

            newRlist = set()
            if len(self.iAgentSet) < self.N:
                for recoverAgent in tuple(self.iAgentSet):
                    if recoverAgent in newIlist:
                        continue
                    if random.random() <= mu:
                        newRlist.add(recoverAgent)

            for n_to_recover in newRlist:
                if n_to_recover in self.iAgentSet:
                    self.recoverAgent(n_to_recover)

            self.iList.append(len(self.iAgentSet))
            self.t += 1

        if print_status:
            print(
                "beta1",
                beta1,
                "beta2",
                beta2,
                "beta3",
                beta3,
                "Done!",
                len(self.iAgentSet),
                "infected agents left",
            )

        return self.iList

    def get_stationary_rho(self, normed=True, last_k_values=100):
        infected_list = self.iList
        if len(infected_list) == 0:
            return 0
        if normed:
            infected_list = 1.0 * np.array(infected_list) / self.N
        if infected_list[-1] == 1:
            return 1
        if infected_list[-1] == 0:
            return 0
        avg_i = np.mean(infected_list[-last_k_values:])
        return np.nan_to_num(avg_i)

