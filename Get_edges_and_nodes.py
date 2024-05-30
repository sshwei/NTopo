from concurrent.futures import ThreadPoolExecutor
import os
from log import logger

class Topo:
    def __init__(self):
        # self.node_dict = {}
        self.edge_dict = {}
        self.target_dict = {}
        self.node_set=set()

    def parse_yarrp_output(self,YARRP_OUTPUT_DIR) -> tuple:
        topology_dict = {}

        with open(YARRP_OUTPUT_DIR, 'r') as f:
            with open(YARRP_OUTPUT_DIR, 'r') as f:
                for line in f.readlines():
                    if line.startswith('# Pkts:'):
                        packets = int(line.split(':')[1].strip())
                    if line[0] != '#':
                        lst = line.split()
                        try:
                            # target, hop, ttl, rttl = lst[0], lst[6], int(lst[5]), int(lst[11])
                            target, hop, ttl = lst[0], lst[6], int(lst[5])
                        except IndexError:
                            print(f"Error: list index out of range in file {YARRP_OUTPUT_DIR}, line {line}")
                            continue

                        # self.node_dict[hop] = rttl
                        self.target_dict[hop] = target

                        # if hop != target:
                        self.node_set.add(hop)
                        if target not in topology_dict:
                            topology_dict[target] = {}
                        topology_dict[target][ttl] = hop

        for target, v in topology_dict.items():
            a = sorted([[ttl, hop] for ttl, hop in v.items()] + [[10000, target]])

            for i in range(len(a) - 1):
                src_ttl, src = a[i]
                dst_ttl, dst = a[i + 1]

                if src_ttl + 1 == dst_ttl:
                    self.edge_dict[(src, dst)] = 1
                else:
                    self.edge_dict[(src, dst)] = 0

                self.target_dict[(src, dst)] = target

        # nodes = [{'addr': node, 'rttl': rttl, 'target': self.target_dict[node]} for node, rttl in
        #          self.node_dict.items()]
        # edges = [{'src': src, 'dst': dst, 'real': real, 'target': self.target_dict[(src, dst)]} for (src, dst), real in
        #          self.edge_dict.items()]
        nodes = [node for node in self.node_set]
        edges = [(src, dst) for (src, dst), _ in self.edge_dict.items()]
        return nodes, edges,packets


def write_lists_to_files(list1, list2, file1, file2):
    with open(file1, 'w') as f1:
        f1.writelines("{}\n".format(item) for item in list1)
    with open(file2, 'w') as f2:
        f2.writelines("{}\n".format(item) for item in list2)



def process_file(file,directory):
    file_path = os.path.join(directory, file)
    topo = Topo()
    try:
        result = topo.parse_yarrp_output(file_path)
        return result[0], result[1],result[2]
    except Exception as e:
        print("Error occurred while processing file", file, ":", e)
        return None, None,None


if __name__ == '__main__':

    Nodes = '/home/lihongwei/topo/fish/compare/Topominerv1/data/nodes.txt'
    Edges = '/home/lihongwei/topo/fish/compare/Topominerv1/data/edges.txt'
    directory = r"/home/lihongwei/topo/fish/compare/Topominerv1/data/random/"
    file_list = [file for file in os.listdir(directory) if file.startswith("yarrp")]
    nodes_set = set()
    edges_set = set()
    packets=0
    with ThreadPoolExecutor(max_workers=4) as executor:
        try:
            results = list(executor.map(lambda file: process_file(file, directory), file_list))
        except Exception as e:
            print("Error occurred:", e)
            exit(1)

        for file, result in zip(file_list, results):
            if result is not None:
                nodes, edges,pt = result
                if nodes is not None and edges is not None and pt is not None:
                    nodes_set.update(set(nodes))
                    edges_set.update(set(edges))
                    packets+=pt
                    print("Processed file:", file)
                else:
                    print("Skipped file:", file)
            else:
                print("Skipped file:", file)

        write_lists_to_files(nodes_set, edges_set, Nodes, Edges)
        logger.info(f"Results written to files:{Nodes}, {Edges}.")
        logger.info(f"Number of nodes is {len(nodes_set)},Number of edges is {len(edges_set)}.")
