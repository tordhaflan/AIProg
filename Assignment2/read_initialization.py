def read_parameters_file():

    """ Reads input from initialize.txt and returns a list

    :return For Nim - [Game name, batch size, number of simulations, player to start, heap size,
                        max number of pices to remove, verbose]
            For Ledge - [Game name, batch size, number of simulations, player to start, initial board, verbose]
    """

    f = open("initialize.txt", "r")

    param = []

    for line in f:
        if line is not "\n":
            s = line.split(":")[1]
            s = s.strip()
            if s.isdigit():
                s = int(s)
            elif s == "true":
                s = True
            elif s == "false":
                s = False
            elif s.__contains__("["):
                s = s.strip("[")
                s = s.strip("]")
                s = s.split(",")
                s = [int(x) for x in s]

            param.append(s)

    f.close()

    if param[0] == "Nim":
        param = param[:6] + param[7:]
    else:
        param = param[:4] + param[6:]

    return param

# print(read_parameters_file())
