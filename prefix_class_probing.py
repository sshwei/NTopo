from log import *
from Target_Generation import *
import time
from traceip import *
from Precess_topo_path import *



def clsass_prefixes(pfixes):
    if len(pfixes)>0:
        prefixes_by_length = {}
        for pfix in pfixes:
            if pfix is not None:
                prefix_length = int(pfix.split('/')[-1])
                if prefix_length in prefixes_by_length:
                    prefixes_by_length[prefix_length].append(pfix)
                else:
                    prefixes_by_length[prefix_length] = [pfix]
        return prefixes_by_length
    else:
        logger.info("prefixes is none")
        return None
    
def Class_prefix_by_length_probing(prefixes_by_length,packets,flag,alise_db,Round,Disadd,Disalise,totalbudget):
    prelendict={}
    node_set=set()
    edge_set=set()
    alise_set=set()
    comprefix_set=set()
    as_set=set()
    Prx=[]
    for length, prfs in prefixes_by_length.items():
        lenprefixes=len(prfs)
        Len=int(length)
        if (Len >= 32 and Len <=64) and lenprefixes >0:
            if flag:
                add_by_prefix_class=chunked_processing_gLip(prfs, chunk_size=1000)
                logger.info(f"generating target addresses completed for this class prefix: [/{length}]... ")
            else:
                add_by_prefix_class=chunked_processing_gRip(prfs, chunk_size=1000)   
                logger.info(f"generating target addresses completed for this class prefix: [/{length}]... ")
            if len(add_by_prefix_class)>0:
                start_timeA=time.time()
                random.shuffle(add_by_prefix_class)#Randomly order target addresses to avoid ICMPv6 rate limiting
                packet,node,edge,topolist,alise_prefix=trcacert(add_by_prefix_class,Round,alise_db)
                compre,tempas=topo_AS_Comprefix(get_New_ipdict(topolist))
                comprefix_set.update(compre)
                as_set.update(tempas)
                Newnode=node-Disadd
                Newalise=alise_prefix-Disalise
                temdisnum=len(Newnode)+len(Newalise)
                prelendict[Len]=int(round(temdisnum/packet * 100, 2))
                node_set.update(node)
                edge_set.update(edge)
                alise_set.update(alise_prefix)
                packets+=packet
                end_timeB=time.time()
                elapsed_time=end_timeB-start_timeA
                logger.info(f"duration:{elapsed_time:.2f}s,This type [/{length}] of target address has been detected.")
                logger.info(f"Prefixes with length [/{length}],New Discovered interface number:{temdisnum},detecting rate of change to prefix:{round(temdisnum/packet * 100, 2)}% ")
                if packets>totalbudget:
                    break
        else:
            Prx.extend(prfs)
    if len(Prx)>0:
        if flag:
                add_by_prefix_class=chunked_processing_gLip(Prx, chunk_size=1000)
                logger.info(f"generating target addresses completed for this class prefix... ")
        else:
            add_by_prefix_class=chunked_processing_gRip(prfs, chunk_size=1000)   
            logger.info(f"generating target addresses completed for this class prefix... ")
        if len(add_by_prefix_class)>0:
            start_timeA=time.time()
            random.shuffle(add_by_prefix_class)#Randomly order target addresses to avoid ICMPv6 rate limiting
            packet,node,edge,topolist,alise_prefix=trcacert(add_by_prefix_class,Round,alise_db)
            compre,tempas=topo_AS_Comprefix(get_New_ipdict(topolist))
            comprefix_set.update(compre)
            as_set.update(tempas)
            Newnode=node-Disadd
            Newalise=alise_prefix-Disalise
            temdisnum=len(Newnode)+len(Newalise)
            node_set.update(node)
            edge_set.update(edge)
            alise_set.update(alise_prefix)
            packets+=packet
            end_timeB=time.time()
            elapsed_time=end_timeB-start_timeA
            logger.info(f"duration:{elapsed_time:.2f}s,This type of target address has been detected.")
            logger.info(f"New Discovered interface number:{temdisnum},detecting rate of change to prefix:{round(temdisnum/packet * 100, 2)}% ")
    return packets,node_set,edge_set,alise_set,comprefix_set,as_set,prelendict

