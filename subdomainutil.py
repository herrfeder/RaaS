import ast

def extractFierceDict(fo):

    dict_buffer = []
    temp_dict = {}
    start_dict = False
    in_dict = False
    for line in fo:
        line = line.rstrip(",")

        for el in line.split(","):

            if in_dict:
                dict_buffer.append(el)

                if el.endswith('}'):
                    start_dict = False
                    in_dict = False
                    temp_dict.update(ast.literal_eval(",".join(dict_buffer)))
                    dict_buffer = []

            if start_dict:

                if el.startswith('{'):
                    in_dict = True
                    dict_buffer.append(el)

                    if el.endswith('}'):
                        start_dict = False
                        in_dict = False
                        temp_dict.update(ast.literal_eval(",".join(dict_buffer)))
                        dict_buffer = []

            if el == 'Nearby:':
                start_dict = True

    temp_dict = { v.rstrip("."):k for k,v in temp_dict.items() }

    return temp_dict


