

def read_parameters_file():

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
            elif s.__contains__("(") and not s.__contains__("["):
                s = s.strip("(")
                s = s.strip(")")
                s = s.split(",")
                s = [int(x) for x in s]
            elif s.__contains__("["):
                x = s.split(',')
                s = []
                for i in range(0, len(x), 2):
                    x[i] = x[i].strip("[]() ")
                    x[i+1] = x[i+1].strip("[]() ")
                    s.append((int(x[i]), int(x[i+1])))
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




