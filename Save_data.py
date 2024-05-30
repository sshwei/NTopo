
import datetime
import time


def save_proportion(prefix_dict,sample_counts,total_samples,lentotalprefixes):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    output_file="data/proportion"+ timestamp +".txt"
    with open(output_file, "w") as file:
        for key, count in zip(prefix_dict.keys(), sample_counts):
            proportion = count / total_samples
            totalproportion=count/lentotalprefixes
            result = f"Prefix Length: {key},Number of Prefixes Selected: {count},Proportion to total sampling: {proportion:.2%},Proportion of all prefixes:{totalproportion:.2%}"
            file.write(result + "\n")


def save_result(result_name,result):
    timestamp = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    result_file = "data/"+result_name+ timestamp +".txt"
    with open(result_file, "w") as file:
        string_result = [str(item) for item in result]
        file.write("\n".join(list(string_result)) + "\n")