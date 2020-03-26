
def read_file():

    """ Reads input from parameters.txt and returns a list

    :return: param: [size, board_type, open_cells, episodes, layers, initial_epsilon,
                            actor_learning_rate, actor_eligibility_rate, actor_discount_factor,
                            critic_learning_rate, critic_eligibility_rate, critic_discount_factor]
    """

    f = open("parameters.txt", "r")

    param = []

    for line in f:
        if line is not "\n":
            s = line.split(":")[1]
            s = s.strip()
            if s.isdigit():
                s = int(s)
            elif s.__contains__("."):
                s = float(s)
            elif s.__contains__("("):
                s = s.strip("(")
                s = s.strip(")")
                s = s.split(",")
                s = [int(x) for x in s]
            elif s == "triangle":
                s = False
            elif s == "diamond":
                s = True
            elif s == "table":
                s = True
            elif s == "NN":
                s = False

            param.append(s)
    f.close()
    return param

print(read_file())