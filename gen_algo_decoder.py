import random
import copy
from sentence_score import sentence_value

MOD = 32
to_digit = {
    u"а": 0,
    u"б": 1,
    u"в": 2,
    u"г": 3,
    u"д": 4,
    u"е": 5,
    u"ж": 6,
    u"з": 7,
    u"и": 8,
    u"й": 9,
    u"к": 10,
    u"л": 11,
    u"м": 12,
    u"н": 13,
    u"о": 14,
    u"п": 15,
    u"р": 16,
    u"с": 17,
    u"т": 18,
    u"у": 19,
    u"ф": 20,
    u"х": 21,
    u"ц": 22,
    u"ч": 23,
    u"ш": 24,
    u"щ": 25,
    u"ъ": 26,
    u"ы": 27,
    u"ь": 28,
    u"э": 29,
    u"ю": 30,
    u"я": 31,
}

to_letter = {
    0: u"а",
    1: u"б",
    2: u"в",
    3: u"г",
    4: u"д",
    5: u"е",
    6: u"ж",
    7: u"з",
    8: u"и",
    9: u"й",
    10: u"к",
    11: u"л",
    12: u"м",
    13: u"н",
    14: u"о",
    15: u"п",
    16: u"р",
    17: u"с",
    18: u"т",
    19: u"у",
    20: u"ф",
    21: u"х",
    22: u"ц",
    23: u"ч",
    24: u"ш",
    25: u"щ",
    26: u"ъ",
    27: u"ы",
    28: u"ь",
    29: u"э",
    30: u"ю",
    31: u"я",
}


def swap_letter(a, letters_mapping):
    #import ipdb; ipdb.set_trace()
    return to_digit[letters_mapping[to_letter[a]]] if to_letter[a] in letters_mapping else a


def feed_back(a, s, op=-1):
    assert op in [1, -1]
    return (a + op * s) % MOD


def negate(a, xor_mask):
    return a ^ xor_mask


def swap_bits(a, bits_mapping):
    bits = []
    for i in range(5):
        bits.append(a % 2)
        a //= 2
    res_bits = [bits[bits_mapping[i]] for i in range(5)]
    res = 0
    for i in range(4, -1, -1):
        res *= 2
        res += res_bits[i]
    return res


def shift_bits(a, shift):
    return (a + shift) % MOD


def encrypt(s, controls_state):
    numbers = [to_digit[l] for l in s]
    prev_state = 0
    res = []
    for a in numbers:
        a = swap_letter(a, controls_state['letters_mapping'])
        a = feed_back(a, prev_state, op=controls_state['feedback_state'])
        a = negate(a, controls_state['xor_mask'])
        a = swap_bits(a, controls_state['bits_mapping'])
        a = shift_bits(a, controls_state['shift'])
        res.append(a)
        prev_state = a
    return ''.join([to_letter[a] for a in res])


def decrypt(s, controls_state):
    states = [0] + [to_digit[l] for l in s]
    prev_state = 0
    res = []
    bm = [0] * 5
    for i, j in enumerate(controls_state['bits_mapping']):
        bm[j] = i
    for i, state in enumerate(states[1:], 1):
        a = shift_bits(state, -controls_state['shift'])
        a = swap_bits(a, bm)
        a = negate(a, controls_state['xor_mask'])
        a = feed_back(a, states[i - 1], op=-controls_state['feedback_state'])
        a = swap_letter(a, controls_state['letters_mapping'])
        res.append(a)
    return ''.join([to_letter[a] for a in res])


def get_random_letter_mapping():
    n = random.randrange(16)
    r = list(range(32))
    random.shuffle(r)
    r = r[:n*2]
    res = {}
    for i in range(n):
        res[to_letter[r[i*2]]] = to_letter[r[i*2 + 1]]
        res[to_letter[r[i*2 + 1]]] = to_letter[r[i*2]]
    return res


def get_random_feedback_state():
    return (-1)**random.randrange(2)


def get_random_xor_mask():
    return random.randrange(MOD)


def get_random_bits_mapping():
    r = list(range(5))
    random.shuffle(r)
    return r


def get_random_shift():
    return random.randrange(16)


def get_random_controls_state():
    return {
        'letters_mapping': get_random_letter_mapping(),
        'feedback_state': get_random_feedback_state(),
        'xor_mask': get_random_xor_mask(),
        'bits_mapping': get_random_bits_mapping(),
        'shift': get_random_shift()
    }


def mutate_letter_mapping(letters_mapping):
    mapping = copy.deepcopy(letters_mapping)
    n = random.randrange(8)
    for _ in range(n):
        l1 = to_letter[random.randrange(32)]
        l2 = to_letter[random.randrange(32)]
        if l1 == l2:
            continue
        if l1 in mapping and l2 in mapping:
            if l2 != mapping[l1]:
                pairs = [[l1, mapping[l1]], [l2, mapping[l2]]]
                mapping[pairs[0][0]] = pairs[1][1]
                mapping[pairs[1][1]] = pairs[0][0]
                mapping[pairs[0][1]] = pairs[1][0]
                mapping[pairs[1][0]] = pairs[0][1]
            else:
                if random.random() < 0.5:
                    del mapping[l1]
                    del mapping[l2]
        elif l1 not in mapping and l2 not in mapping:
            mapping[l1] = l2
            mapping[l2] = l1
        else:
            if l1 not in mapping:
                l1, l2 = l2, l1
            assert l1 in mapping
            assert l2 not in mapping
            del mapping[mapping[l1]]
            mapping[l1] = l2
            mapping[l2] = l1

    return mapping


def mutate_feedback_state(state):
    if random.random() < 0.4:
        return (-1)**random.randrange(2)
    else:
        return state


def mutate_xor_mask(xor_mask):
    if random.random() < 0.4:
        return (xor_mask + random.randrange(-5, 6, 1)) % MOD
    else:
        return xor_mask


def mutate_bits_mapping(bits_mapping):
    mapping = copy.deepcopy(bits_mapping)
    if random.random() < 0.4:
        ind1 = random.randrange(5)
        ind2 = random.randrange(5)
        while ind2 == ind1:
            ind2 = random.randrange(5)
        c = mapping[ind1]
        mapping[ind1] = mapping[ind2]
        mapping[ind2] = c
        return mapping
    else:
        return mapping


def mutate_shift(shift):
    if random.random() < 0.4:
        return (shift + random.randrange(-5, 6, 1)) % 16
    else:
        return shift


def mutate(control_state):
    return {
        'letters_mapping': mutate_letter_mapping(control_state['letters_mapping']),
        'feedback_state': mutate_feedback_state(control_state['feedback_state']),
        'xor_mask': mutate_xor_mask(control_state['xor_mask']),
        'bits_mapping': mutate_bits_mapping(control_state['bits_mapping']),
        'shift': mutate_shift(control_state['shift'])
    }


def fitness_function(control_state, s=u'цщтюмчзхыымйыыиынщлыыъмкиегятбррйзуюштожбрющмшърпгузицфвцрдтшыжубсилуэнодхещузсныысносизпэулчзсцыекдицващнасжжрзпсйрлупыиюжрзпщмицмюжцьчянлудшюокьидхлгюяещзекфйвддцютшожюмпляллзатъфохвфвъцигянескывъмз'):
    #s = s[:80]
    return sentence_value(decrypt(s, control_state))


def lifecycle():
    current = [get_random_controls_state() for _ in range(100)]
    s = u'цщтюмчзхыымйыыиынщлыыъмкиегятбррйзуюштожбрющмшърпгузицфвцрдтшыжубсилуэнодхещузсныысносизпэулчзсцыекдицващнасжжрзпсйрлупыиюжрзпщмицмюжцьчянлудшюокьидхлгюяещзекфйвддцютшожюмпляллзатъфохвфвъцигянескывъмз'
    #s = s[:80]
    best_score = 0.0
    plateau = 0
    i = 0
    while 1:
        random_generated = [get_random_controls_state() for _ in range(100)]
        mutated = [mutate(control_state) for control_state in current]
        combined = list(sorted(current + random_generated +
                               mutated, key=fitness_function))
        assert len(combined) == 300
        # if i % 1000 == 0:
        #    current = [get_random_controls_state()
        # for _ in range(90)] + combined[-10:]
        #    print("==================================================")
        #    print("EXTINCTION")
        #    print("==================================================")
        if plateau < 1000:
            current = combined[:25] + combined[-75:]
            plateau += 1
        else:
            current = [get_random_controls_state()
                       for _ in range(90)] + combined[-15:-5]
            plateau = 0
            print("==================================================")
            print("PLATEAU")
            print("==================================================")
            #best_score = fitness_function(current[-1])
        score = fitness_function(current[-1])
        i += 1
        if score > best_score:
            best_score = score
            plateau = 0
            print("==================================================")
            print("{} {}".format(
                decrypt(s, current[-1]), best_score))
            print(current[-1])
            print("==================================================")

if __name__ == '__main__':
    lifecycle()
