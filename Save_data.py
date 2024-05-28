# 学校：北京工商大学
# 姓名：李宏伟
# 日期：2024/3/26
import datetime
import time

# def save_prefixes(prefixes):
#     timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
#     filename = "data/prefixes_" + timestamp + ".txt"
#     with open(filename, 'w') as file:
#         for item in prefixes:
#             file.write(item + '\n')

# def save_generate_add(prefixes):
#     timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
#     filename = "data/generate_add_" + timestamp + ".txt"
#     with open(filename, 'w') as file:
#         for item in prefixes:
#             file.write(item + '\n')

# def save_totalprefixes(totalprefix):
#     timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     totalprefix_file="data/totalprefix"+ timestamp +".txt"
#     #Write the discovered and expanded prefix to a file
#     with open(totalprefix_file, "w") as file:
#         file.write("\n".join(list(totalprefix)) + "\n")

# def save_selectprefixes(totalprefix):
#     timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     selectprefix_file="data/selectprefix"+ timestamp +".txt"
#     #Write the discovered and expanded prefix to a file
#     with open(selectprefix_file, "w") as file:
#         file.write("\n".join(list(totalprefix)) + "\n")

def save_proportion(prefix_dict,sample_counts,total_samples,lentotalprefixes):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file="data/proportion"+ timestamp +".txt"
    with open(output_file, "w") as file:
        for key, count in zip(prefix_dict.keys(), sample_counts):
            proportion = count / total_samples
            totalproportion=count/lentotalprefixes
            result = f"Prefix Length: {key},Number of Prefixes Selected: {count},Proportion to total sampling: {proportion:.2%},Proportion of all prefixes:{totalproportion:.2%}"
            file.write(result + "\n")

# def save_Disasadd(Disasadd):
#     timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     # Write Disadd to file
#     Disadd_file = "data/Disasadd" + timestamp + ".txt"
#     with open(Disadd_file, "w") as file:
#         file.write("\n".join(list(Disasadd)) + "\n")

# def save_Alldisadd(Discoveradd):
#     timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
#     Discoveradd_file = "data/Alldisadd"+ timestamp +".txt"
#     # Write Discoveradd to file
#     with open(Discoveradd_file, "w") as file:
#         file.write("\n".join(list(Discoveradd)) + "\n")


def save_result(result_name,result):
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    result_file = "data/"+result_name+ timestamp +".txt"
    with open(result_file, "w") as file:
        string_result = [str(item) for item in result]
        file.write("\n".join(list(string_result)) + "\n")