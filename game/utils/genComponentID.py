def calculate_least_value_nin_array(array):
    max_el = max(array)
    if max_el < 1:
        return 1
    if len(array) == 1:
        return 2 if array[0] == 1 else 1
    l = [0] * max_el
    for i in range(len(array)):
        if array[i] > 0:
            if l[array[i] - 1] != 1:
                l[array[i] - 1] = 1
    for i in range(len(l)):
        if l[i] == 0:
            return i + 1
    return i + 2
