
def read_parameters_file():

    f = open("parameters.txt", "r")

    param = []

    for line in f:
        if line is not "\n":
            s = line.split(":")[1]
            s = s.strip()
            if s.isdigit():
                s = int(s)
                print(s, type(s))
            elif s.__contains__("."):
                s = s.split(".")
                dec = float(s[1])
                s = dec/100.0
                print(s, type(s))
            elif s.__contains__("("):
                s = s.strip("(")
                s = s.strip(")")
                s = s.split(",")
                s = [int(x) for x in s]
                print(s, type(s), type(s[1]))
            elif s == "triangle":
                s = False
                print(s, type(s))
            elif s == "diamond":
                s = True
                print(s, type(s))
            else:
                print(s, len(s), type(s))
            param.append(s)

    f.close()

    return param


print(read_parameters_file())



