import os
from log import *
from Save_data import *
import pyasn

YARRP_DIR='/home/tools/yarrp/yarrp'#Enter the location of yarrp's startup file
INTERFACE_NAME='ens33'
pps=5000
m=16
l=5

def use_yarrp(YARRP_INPUT_DIR: str, YARRP_OUTPUT_DIR:str ):
    cmd = 'sudo %s -i %s -I %s -t ICMP6 -m %d -r %d -o %s -n %d' % (
        YARRP_DIR, YARRP_INPUT_DIR, INTERFACE_NAME, m,pps, YARRP_OUTPUT_DIR,l)
    try:
        os.system(cmd)
    except Exception as e:
        logger.error("Failure in Calling Yarrp: %s", e)


class Topo:
    def __init__(self):
        self.edge_set = set()
        self.node_set=set()

    def parse_yarrp_output(self,YARRP_OUTPUT_DIR,alise_db) -> tuple:
        topology_dict = {}
        hop_set=set()
        alise_set=set()
        with open(YARRP_OUTPUT_DIR, 'r') as f:
            with open(YARRP_OUTPUT_DIR, 'r') as f:
                for line in f.readlines():
                    if line.startswith('# Pkts:'):
                        packets = int(line.split(':')[1].strip())
                    if line[0] != '#':
                        lst = line.split()
                        try:
                            target, hop, ttl = lst[0], lst[6], int(lst[5])
                        except IndexError:
                            print(f"Error: list index out of range in file {YARRP_OUTPUT_DIR}, line {line}")
                            continue
                        if hop not in hop_set:
                            hop_set.add(hop)
                            num, prefix = alise_db.lookup(hop)
                            if prefix is None:
                                self.node_set.add(hop)
                                if target not in topology_dict:
                                    topology_dict[target] = []
                                topology_dict[target].append([hop, ttl])
                            else:
                                alise_set.add(prefix)

        for target in topology_dict:
            topology_dict[target] = sorted(topology_dict[target], key=lambda x: x[1])
            hops = [entry[0] for entry in topology_dict[target]]  # extract hop
            for i in range(len(hops) - 1):
                hop_pair = (hops[i], hops[i+1])
                self.edge_set.add(hop_pair)
        topology_list = list(topology_dict.values())
        return packets,self.node_set,self.edge_set,topology_list,alise_set
    

    
def trcacert(addresslist,Round,alise_db):
    label = str(Round)
    timestamp = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    filenameinput = "data/targets_" + label+"_"+timestamp + "_.txt"
    with open(filenameinput, "w") as file:
         file.write("\n".join(list(addresslist)) + "\n")
    filenameoutput = "data/yarrp_" + label+"_"+timestamp + "_.txt"
    use_yarrp(filenameinput, filenameoutput)
    topo=Topo()
    packets,nodes,edges,topolist,alise_prefix=topo.parse_yarrp_output(filenameoutput,alise_db)
    return packets,nodes,edges,topolist,alise_prefix