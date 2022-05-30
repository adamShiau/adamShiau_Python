import pickle
import json
from common import *


def t1():
    dictionary_data = {"a": 1, "b": 2}
    a_file = open("data.pkl", "wb")
    pickle.dump(dictionary_data, a_file)
    a_file.close()
    a_file = open("data.pkl", "rb")
    output = pickle.load(a_file)
    print(output)
    print(type(output))
    print(output["a"])


def t2():
    dictionary_data = {"a": 1, "b": 2}

    a_file = open("data.json", "w")
    json.dump(dictionary_data, a_file)
    a_file.close()

    a_file = open("data.json", "r")
    output = json.load(a_file)
    # output = a_file.read()
    print(output)
    print(type(output))


if __name__ == "__main__":
    # file_manager(True, "para1.txt", "r", )
    t = parameters_manager("data.json", {"A": 1, "B": 2}, 0)
    t.update_parameters("A", 1000)
