import collections
from collections import defaultdict
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
from Common_profix import *
from log import *
from Extract_prefix import get_asn



def group_ip(final_ip_list):
    ases= defaultdict(list)
    for ip in final_ip_list:
        as_number = get_asn(ip)
        if as_number and as_number!=23910: #23910 is Probe Local ASN
            ases[as_number].append(ip)
    return ases


def deduplicate_list(lst):
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def process_results(results):
    temp_dict= defaultdict(list)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(group_ip, result) for result in results]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            for key, value_list in result.items():
                for value in value_list:
                    if key in temp_dict and set(temp_dict[key]) != set(value):
                        if isinstance(temp_dict[key], list):
                            temp_dict[key].extend(value)
                        else:
                            temp_dict[key] = [temp_dict[key], value]
                    else:
                        temp_dict[key].extend(value)
    for key, value in temp_dict.items():
        temp_dict[key]= deduplicate_list(value)
    return temp_dict


def collect_ip(ip_list):
    ip_lst=[]
    if len(ip_list)>1:
        for i in range(len(ip_list)-1):
            if ip_list[i][0]!=ip_list[i+1][0]:
                ip_lst.append(ip_list[i][0]) 
    ip_lst.append(ip_list[-1][0])
    return ip_lst


def get_New_ipdict(ip_lists):
    temp_dict=collections.OrderedDict()
    if len(ip_lists)>0:
        with ProcessPoolExecutor() as executor:
            results = executor.map(collect_ip, [iplist for iplist in ip_lists])
        temp_dict=process_results(results)
        return temp_dict
    

def topo_AS_Comprefix(temp_dict):
    pres=[]
    AS=set()
    if temp_dict:
        with ProcessPoolExecutor() as executor: 
            futures = []
            for as_num, ip_lst in temp_dict.items():
                future = executor.submit(extract_common_prefix, ip_lst)
                futures.append(future)
                AS.add(as_num)
            for future in concurrent.futures.as_completed(futures):
                pr = future.result()
                pres.extend(pr)
    preset=set(pres)
    logger.info(f"Common prefix extraction complete.")
    return preset,AS
