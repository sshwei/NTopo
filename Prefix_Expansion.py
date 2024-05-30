
import ipaddress
import concurrent.futures



def compress_prefix(prefix):
    network = ipaddress.IPv6Network(prefix)
    # Obtain compressed prefix
    compressed_prefix = network.compressed
    return compressed_prefix


def binary_to_ipv6_prefix(binary_str):
    prefix_length = len(binary_str)
    binary_str = binary_str.ljust(128, '0')
    decimal = int(binary_str, 2)
    ipv6_network = ipaddress.IPv6Network((decimal, prefix_length), strict=False)
    ipv6_prefix = ipv6_network.with_prefixlen
    return str(ipv6_prefix)

def g_prefix(ip, prefix_length,n, bounds):#在固定边界基础上，补差跨越边界
    binary_address = format(int(ip), '0128b')
    expend_pre = []
    length = 0
    
    if prefix_length is not None:
        prefix_length = int(prefix_length)
        if prefix_length>0 and prefix_length<bounds[-1]:
            if bounds is not None:
                for bound in bounds:
                    diff=bound-prefix_length
                    if diff==0:#前缀长度补差刚好被4整除
                        if n+prefix_length<=bounds[-1]:
                            for i in range(2 ** n):
                                zeros_and_ones = format(i, f'0{n}b')
                                binary_address = binary_address[:prefix_length] + zeros_and_ones
                                hexp = binary_to_ipv6_prefix(binary_address)
                                expend_pre.append(hexp)
                            break
                    elif diff>0 and diff<n:
                        temlen = prefix_length + diff
                        if n+temlen<=bounds[-1]:
                            try:
                                for i in range(2 ** n):
                                    zeros_and_ones = format(i, f'0{n}b')
                                    binary_address = binary_address[:temlen] + zeros_and_ones
                                    hexp = binary_to_ipv6_prefix(binary_address)
                                    expend_pre.append(hexp)
                            except TypeError as e:
                                print("TypeError occurred:", e)
                            break
                        else:
                            n = bounds[-1] - prefix_length
                            for i in range(2 ** n):
                                zeros_and_ones = format(i, f'0{n}b')
                                binary_address = binary_address[:prefix_length] + zeros_and_ones
                                hexp = binary_to_ipv6_prefix(binary_address)
                                expend_pre.append(hexp)
                        break
                    elif diff>n:
                        closest_greater= prefix_length
                        while closest_greater % 4 != 0:
                            closest_greater += 1
                        n=closest_greater-prefix_length
                        try:
                            for i in range(2 ** n):
                                zeros_and_ones = format(i, f'0{n}b')
                                binary_address = binary_address[:prefix_length] + zeros_and_ones
                                hexp = binary_to_ipv6_prefix(binary_address)
                                expend_pre.append(hexp)
                        except TypeError as e:
                            print("TypeError occurred:", e)
                        break
        else:
            length=0
            for i in range(2 ** length):
                zeros_and_ones = format(i, f'0{length}b')
                binary_address = binary_address[:prefix_length-1] + zeros_and_ones
                hexp = binary_to_ipv6_prefix(binary_address)
                expend_pre.append(hexp)
    return expend_pre


def process_prefix(prefix, n, cor):
    # expendedpre=[]
    pres = []
    if prefix is not None:
        prefix_parts = prefix.split('/')
        if len(prefix_parts) == 2:
            address, prefix_length = prefix_parts
        # address, prefix_length = prefix.split('/')
            ip = ipaddress.IPv6Address(address)
            pres.extend(g_prefix(ip, prefix_length, n, cor))
    return pres


def process_prefixes_chunk(prefixes, n, cor):
    pres = []
    for prefix in prefixes:
        result = process_prefix(prefix, n, cor)
        pres.extend(result)
    return pres



def chunked_chanpre(prefixes, n, cor, chunk_size=1000):
    pres = []
    chunks = [prefixes[i:i+chunk_size] for i in range(0, len(prefixes), chunk_size)]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_prefixes_chunk, chunk, n, cor) for chunk in chunks]

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            pres.extend(result)

    return list(set(pres))





if __name__ == '__main__':
    n=4
    # cor=[16,20,24,28,32,36,40,44,48,52,56,60,64]
    # prefixes=['2402:1e80:0:2700::/56']
    cor=[24,64]
    prefixes = ['2001:db8:0:10::/53','2402:1e80:0:2700::/56']
    pres=chunked_chanpre(prefixes, n, cor, chunk_size=1000)
    print(pres)
