import random
import argparse
from log import *
import time
from Target_Generation import *
import requests
import sys
sys.path.append('/home/tools/miniconda3/conda3/bin/lzma')
import lzma
import os
from traceip import *
import pyasn
from Precess_topo_path import *
from prefix_class_probing import *
from Prefix_Expansion import *
from Extract_prefix import *




alise_prefixes=set()
totalfrefixes=set()
Round=0
Discovered_address=set()
Discovered_edge=set()
Discovered_alise_prefix=set()
Discovered_AS=set()
packets=0
flag=True
total_reached_prefix=set()


def get_alise_prefixes():
    alise_prefixes = set()
    relative_path = 'alise_list/aliased-prefixes.txt'
    file_path = os.path.join(os.path.dirname(__file__), relative_path)
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            line = file.readline()
            while line:
                line = line.strip()
                if line and not line.startswith('#'):
                    alise_prefixes.add(line)
                line = file.readline()
        logger.info("Finish reading alias prefixes.")
    else:
        url = "https://alcatraz.net.in.tum.de/ipv6-hitlist-service/open/aliased-prefixes.txt.xz"
        download_path = os.path.join(os.path.dirname(__file__), 'alise_list/aliased-prefixes.txt.xz')
        response = requests.get(url)
        with open(download_path, 'wb') as file:
            file.write(response.content)
        logger.info("The alias list has been downloaded.")
        uncompressed_path = os.path.splitext(download_path)[0]
        with lzma.open(download_path, 'r') as compressed_file:
            with open(uncompressed_path, 'wb') as uncompressed_file:
                uncompressed_file.write(compressed_file.read())
        with open(uncompressed_path, 'r') as file:
            line = file.readline()
            while line:
                line = line.strip()
                if line and not line.startswith('#'):
                    alise_prefixes.add(line)
                line = file.readline()
        logger.info("Finish reading alias prefixes.")
    return alise_prefixes


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", type=str, help="path to target prefixes file")
    parser.add_argument("-i", type=str, help="path to prefix_db")
    parser.add_argument("-a", type=str, help="path to alise_db") #.dat
    # parser.add_argument("-o", type=str, help="path to output file")
    parser.add_argument("-b", type=int, help="Total budget for sending packets")
    # parser.add_argument("-v", type=float, help="Threshold for determining high-density areas", default=0.02)
    args = parser.parse_args()
    return args


def DB_clear(file_path):
    with open(file_path, 'w') as file:
        file.truncate(0)


def build_db(lst, filename, Round):
    file_path = os.path.abspath(filename)
    Round+=1
    file_content = ""
    if not lst:
        return file_path
    with open(file_path, 'a') as f:
        for item in lst:
            file_content += f"{item}\t{Round}\n"
        f.write(file_content)
    return file_path


def get_reached_prefix(newnodes,prefix_db):
    reachpre=set()
    for node in newnodes:
        n,prefix=prefix_db.lookup(node)
        if prefix:
            reachpre.add(prefix)
    return reachpre


def Calculate_coarse(prelendict,cor):
    total = 0.0
    count = 0
    for key, value in prelendict.items():
        total+=value
        count+=1
    if count > 0:
        average = total / count
        average = round(average* 100, 2) 
    Threshold=average
    selected_keys = [key for key, value in prelendict.items() if value >= Threshold]
    sorted_keys = sorted(selected_keys)
    cor.extend(sorted_keys)
    result_cor = []
    for num in cor:
        if num % 4 == 0:
            result_cor.append(num)
        else:
            closest_greater = num
            while closest_greater % 4 != 0:
                closest_greater += 1
            result_cor.append(closest_greater)

    result_cor = sorted(list(set(result_cor)))
    return result_cor

    

if __name__ == '__main__':
    args=parse_arguments()
    logger.info("Parameter input completed...")

    alise_prefixes=get_alise_prefixes()
    DB_clear(args.a)
    alise_db_path=build_db(alise_prefixes,args.a,Round)
    alise_db=pyasn.pyasn(alise_db_path)#Build alias prefix DB
    logger.info("Obtaining alias_list completed...")

    total_budget=args.b
    # Threshold=args.v
    # output_path=args.o
    n=4
    cor=[64]
    bigbuket=0 
    buketvol=0 
    start_time = time.time()
    logger.info("start_time:%s,Reading target prefixes",time.ctime(start_time))

    with open(args.p, "r") as f:
        for line in f:
            prefix = line.strip()
            totalfrefixes.add(prefix)
    DB_clear(args.i)
    prefix_db_path=build_db(totalfrefixes,args.i,Round)
    prefix_db=pyasn.pyasn(prefix_db_path)#Build prefix DB
    prefixes_by_length=clsass_prefixes(totalfrefixes)
    Round+=1
    logger.info(f"Start probing... round{Round}")

    if prefixes_by_length is not None:
        packet,node,edge,alise_prefix,comprefix,as_set,prelendict=Class_prefix_by_length_probing(prefixes_by_length,packets,flag,alise_db,Round,Discovered_address,Discovered_alise_prefix,total_budget)
        cor=Calculate_coarse(prelendict,cor)
        logger.info(f"Calculate coarse are {cor}")

        packets+=packet
        newnodes=node-Discovered_address
        reachpre=get_reached_prefix(newnodes,prefix_db)
        reachpre.update(comprefix)#把可达前缀和共同前缀合体
        total_reached_prefix.update(reachpre)#统计到达的前缀总量
        logger.info(f"total number of reached prefixes is {len(total_reached_prefix)}")

        excludepre=comprefix-totalfrefixes #提取前缀对比库里不存在的前缀
        expendpre=chunked_chanpre(list(reachpre), n, cor, chunk_size=1000)#扩充可达前缀
        expendpre=set(expendpre)-alise_prefixes#剔除别名前缀
        bigbuket=len(expendpre)
        logger.info("expending prefixes completed...")

        excludepre.update(expendpre-totalfrefixes)
        prefix_db_path=build_db(excludepre,args.i,Round)#存入前缀对比库
        prefix_db=pyasn.pyasn(prefix_db_path)
        logger.info("Refreshing the prefix_db completed... ")
        
        Discovered_address.update(node)
        Discovered_edge.update(edge)
        Discovered_alise_prefix.update(alise_prefix)
        Discovered_AS.update(as_set)
        end_timea = time.time()
        elapsed_time=end_timea-start_time
        logger.info(f"round:{Round}.=== Addresses cumulative discovery:{len(Discovered_address)+len(Discovered_alise_prefix)},packet cumulative sent:{packets},probing efficiency:{round((len(Discovered_address)+len(Discovered_alise_prefix)) / packets * 100, 2)}% ")
        expendpre=list(expendpre)
        prefixes_by_length=clsass_prefixes(expendpre)
        Round+=1
    flag=False #生成随机地址

    while True:
        if packets>total_budget:
            break
        
        if prefixes_by_length is not None:
            packet,node,edge,alise_prefix,comprefix,as_set,prelendict=Class_prefix_by_length_probing(prefixes_by_length,packets,flag,alise_db,Round,Discovered_address,Discovered_alise_prefix,total_budget)
            cor=Calculate_coarse(prelendict,cor)
            logger.info(f"Calculate coarse are {cor}")

            packets+=packet
            newnodes=node-Discovered_address
            reachpre=get_reached_prefix(newnodes,prefix_db)
            reachpre.update(comprefix)#把可达前缀和共同前缀合体
            total_reached_prefix.update(reachpre)#统计到达的前缀总量
            logger.info(f"total number of reached prefixes is {len(total_reached_prefix)}")

            excludepre=comprefix-totalfrefixes #提取前缀对比库里不存在的前缀
            expendpre=chunked_chanpre(list(reachpre), n, cor, chunk_size=1000)#扩充可达前缀
            expendpre=set(expendpre)-alise_prefixes
            buketvol=len(expendpre)
            logger.info("expending prefixes completed...")

            if buketvol>=bigbuket:
                bigbuket=buketvol    
            else:
                samplenum=bigbuket-buketvol
                old_pres=random_prefix(total_reached_prefix,samplenum)
                logger.info("Extracting old prefixes completed...")
                expendpre.update(old_pres)
            excludepre.update(expendpre-totalfrefixes)
            prefix_db_path=build_db(excludepre,args.i,Round)#存入前缀对比库
            prefix_db=pyasn.pyasn(prefix_db_path)
            logger.info("Refreshing the prefix_db completed... ")

            Discovered_address.update(node)
            Discovered_edge.update(edge)
            Discovered_alise_prefix.update(alise_prefix)
            Discovered_AS.update(as_set)
            end_timea = time.time()
            elapsed_time=end_timea-start_time
            logger.info(f"round:{Round}.=== Addresses cumulative discovery:{len(Discovered_address)+len(Discovered_alise_prefix)},packet cumulative sent:{packets},probing efficiency:{round((len(Discovered_address)+len(Discovered_alise_prefix)) / packets * 100, 2)}% ")
            expendpre=list(expendpre)
            prefixes_by_length=clsass_prefixes(expendpre)
            Round+=1
        else:
            break
    
    end_time=time.time()
    elapsed_time=end_time-end_time
    logger.info(f"duration:{elapsed_time:.2f}s.=== Addresses cumulative discovery:{len(Discovered_address)+len(Discovered_alise_prefix)},packet cumulative sent:{packets},edges cumulative discovery:{len(Discovered_edge)},probing efficiency:{round((len(Discovered_address)+len(Discovered_alise_prefix)) / packets * 100, 2)}% ")
    
    result_name='Discovered_address'
    save_result(result_name,Discovered_address)
    result_name='Discovered_edge'
    save_result(result_name,Discovered_edge)
    result_name='Discovered_alise_prefix'
    save_result(result_name,Discovered_alise_prefix)
    result_name='Discovered_AS'
    save_result(result_name,Discovered_AS)
    result_name='total_reached_prefix'
    save_result(result_name,total_reached_prefix)
    logger.info("Probing complete!")

