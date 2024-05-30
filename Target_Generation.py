

import ipaddress
import random
import concurrent.futures


def process_item_gLip(item):
    nip=[]
    if item is not None:
        iplowbit=gLip(item)
        if iplowbit is not None:
            nip.append(iplowbit)
    return nip

def process_chunk_gLip(chunk):
    results = []
    for item in chunk:
        result = process_item_gLip(item)
        results.extend(result)
    return results

def chunked_processing_gLip(chapres, chunk_size=100):
    results = []
    chunks = [chapres[i:i+chunk_size] for i in range(0, len(chapres), chunk_size)]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_chunk_gLip, chunk) for chunk in chunks]

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.extend(result)

    return results


def process_item_gRip(item):
    nip=[]
    if item is not None:
        iprandom = gip(item)
        if iprandom is not None:
            nip.append(iprandom)
    return nip

def process_chunk_gRip(chunk):
    results = []
    for item in chunk:
        result = process_item_gRip(item)
        results.extend(result)
    return results

def chunked_processing_gRip(chapres, chunk_size=100):
    results = []
    chunks = [chapres[i:i+chunk_size] for i in range(0, len(chapres), chunk_size)]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_chunk_gRip, chunk) for chunk in chunks]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.extend(result)

    return results



def gip(prefix):
    # Parse the prefix into an IPv6Network object
    try:
        # Parse the prefix into an IPv6Network object
        network = ipaddress.IPv6Network(prefix)
    except ValueError:
        print("Invalid IPv6 prefix:", prefix)
        return None
    # Check if the prefix length is valid
    if network.prefixlen < 0 or network.prefixlen > 128:
        print("IPv6 prefix length erro")
        return None
        # Remove /128 if the prefix length is 128
    elif network.prefixlen == 128:
        ipv6_address = str(prefix).split('/')[0]
    # Generate a random host address within the network range
    else:
        host = random.randint(1, network.num_addresses)  # Exclude network and broadcast addresses
        if host <= 0:
            raise ValueError("Empty range of available IP addresses")
            return None
        # Combine the network prefix with the random host address
        ipv6_address = str(network.network_address + host)
    return ipv6_address


def gLip(prefix):
    # prefix = convert_ipv6_prefix(prefix)
    ip, iplenth = prefix.split('/')
    if ip.endswith('::'):
        ip += '1'
    else:
        segments = ip.split(':')
        segments[-1] = '1'
        ip = ':'.join(segments)
    return ip

if __name__ == '__main__':
    chapres=['2402:1e80:0:2790::/60', '2402:1e80:0:2750::/60',
            '2402:1e80:0:2720::/60', '2402:1e80:0:2760::/60',
            '2402:1e80:0:27d0::/60', '2402:1e80:0:27e0::/60',
            '2402:1e80:0:27a0::/60', '2402:1e80:0:27f0::/60',
            '2402:1e80:0:2730::/60', '2402:1e80:0:2700::/60',
            '2402:1e80:0:27b0::/60', '2402:1e80:0:2740::/60',
            '2402:1e80:0:2770::/60', '2402:1e80:0:2710::/60',
            '2402:1e80:0:2780::/60', '2402:1e80:0:27c0::/60']
    chapres = ['2402:1e80:0:2790::/69', '2402:1e80:0:2750::/65',]
    ip=chunked_processing_gRip(chapres, chunk_size=100)
    print(ip)
    ip=chunked_processing_gLip(chapres, chunk_size=100)
    print(ip)