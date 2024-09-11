from copy import deepcopy


colors  = ['cr',  'ci',   'cb', 'cg', 'cy']
nations = ['nn',  'ne',   'ns', 'nj', 'nu'] 
pets    = ['pd',  'ph',   'pz', 'pf', 'ps']
candies = ['cah', 'cak', 'cam','casn','casm']
juice   = ['jm',  'jt',   'jc', 'jo', 'jw']

domain = [1,2,3,4,5]
var_domain = {c:domain.copy() for c in colors}
var_domain.update({n:domain.copy() for n in nations})
var_domain.update({p:domain.copy() for p in pets})
var_domain.update({ca:domain.copy() for ca in candies})
var_domain.update({j:domain.copy() for j in juice})
#print(var_domain)
var_all = list(var_domain.keys())
#print(var_all)

constr_eq = [
    ('ne', 'cr'),    # The Englishman lives in the red house.
    ('ns', 'pd'),    # The Spaniard owns the dog.
    ('cak', 'cy'),   # Kit Kats are eaten in the yellow house.
    ('casm','ps'),   # The Smarties eater owns snails.
    ('casn','jo'),   # The Snickers eater drinks orange juice.
    ('nu',  'jt'),   # The Ukrainian drinks tea.
    ('nj', 'cam'),   # The Japanese eats Milky Ways.
    ('jc', 'cg'),    # Coffee is drunk in the green house.
]

constr_plus_1 = [ ('cg', 'ci')]     # The green house is immediately to the right of the ivory house.

constr_diff_1 = [ ('cb',  'nn'),     # The Norwegian lives next to the blue house.
                  ('cah', 'pf'),     # The man who eats Hershey bars lives in the house next to the man with the fox.
                  ('cak', 'ph')]     # Kit Kats are eaten in a house next to the house where the horse is kept.

constr_eq_val = [('jm',3), ('nn',1)]

def check_neq(names, var_assigned):
    if names[0] in var_assigned and names[1] in var_assigned:
        if var_assigned[names[0]] != var_assigned[names[1]]:
            #print('\t', names[0], '!=', names[1])
            return True
    return False

def check_unique(list_val):
    return len(set(list_val)) == len(list_val)
        

def check_different_values(var_assigned):
    v_c = [var_assigned[v] for v in var_assigned.keys() if v in colors]
    if len(v_c) > 1 and not check_unique(v_c):
        #print('colors not unique')
        return False
    v_n = [var_assigned[v] for v in var_assigned.keys() if v in nations]
    if len(v_n) > 1 and not check_unique(v_n):
        #print('colors not nations')
        return False
    v_p = [var_assigned[v] for v in var_assigned.keys() if v in pets]
    if len(v_p) > 1 and not check_unique(v_p):
        #print('pet not unique')
        return False
    v_j = [var_assigned[v] for v in var_assigned.keys() if v in juice]
    if len(v_j) > 1 and not check_unique(v_j):
        #print('juice not unique')
        return False
    v_ca = [var_assigned[v] for v in var_assigned.keys() if v in candies]
    if len(v_ca) > 1 and not check_unique(v_ca):
        #print('candies not unique')
        return False
    
    return True

def check_constraints(var_assigned):

    # check constraints that no two variables of the same type have the same value
    if not check_different_values(var_assigned):
        print('Not equal constraint invalid')
        return False

     # The green house is immediately to the right of the ivory house.
    if 'cg' in var_assigned and 'ci' in var_assigned:
        if var_assigned['cg'] != var_assigned['ci'] + 1:
            print('cg != ci+1')
            return False
            
    if 'nn' in var_assigned:
        # The Norwegian lives in the first house on the left.
        if var_assigned['nn'] != 1:
            return False
        # The Norwegian lives next to the blue house.
        if 'cb' in var_assigned:
            if abs(var_assigned['nn']- var_assigned['cb']) != 1:
                print('nn -cb > 1')
                return False

    # Milk is drunk in the middle house.
    if 'jm' in var_assigned and var_assigned['jm'] != 3:
        print('jm != 3')
        return False

    for c in constr_eq:
        if check_neq(c, var_assigned):
            print(c[0], '!=', c[1])
            return False


    # The man who eats Hershey bars lives in the house next to the man with the fox.
    if 'cah' in var_assigned and 'pf' in var_assigned:
        if abs(var_assigned['cah'] - var_assigned['pf']) != 1:
            print('cah - pf > 1')
            return False

    # Kit Kats are eaten in a house next to the house where the horse is kept.
    if 'cak' in var_assigned and 'ph' in var_assigned:
        if abs(var_assigned['cak']- var_assigned['ph']) != 1:
            print('cak- ph > 1')
            return False

    return True

var_unassigned = var_all
var_assigned = {}

# var_domain = {var: list domain values}
# select next variable - use the most constrained variable and least remaining values heuristics
def select_unassigned(var_domain, var_unassigned): # 
    # select the variable from unassigned with least remaining values
    size_domain = {var: len(valid_domain) for (var, valid_domain) in var_domain.items() if var in var_unassigned} 
    select_var = min(size_domain.items(), key=lambda x:x[1])
    if len(select_var) == 0:
        print('Error select unassigned', select_var)
    return select_var[0] # return the key 
    
# select the order of values for variable var
# from the least constraining one = no particular ordering
def select_value_order(var_domain, var):
    return var_domain[var] 

# update the domain of all other variables after a new assignment
# changed domain_all
def update_domain(var, val, var_domain):
    if var in colors:
        for c in colors:
            if c != var:
                var_domain[c].remove(val)
    if var in nations:
        for n in nations:
            if n != var:
                var_domain[n].remove(val)
    if var in pets:
        for p in pets:
            if p != var:
                var_domain[p].remove(val)
    if var in candies:
        for c in candies:
            if c != var:
                var_domain[c].remove(val)
    if var in juice:
        for j in juice:
            if j != var:
                var_domain[j].remove(val)

def check_domain(var_domain): # return True if all variables in var_domain have at least one valid value
    min_domain = min(var_domain.values())
    if min_domain == 0:
        return False
    else:
        return True


def print_solution(var_assigned):
    house1 = []
    house2 = []
    house3 = []
    house4 = []
    house5 = []
    print(var_assigned)
    for keys, values in var_assigned.items():
        if values == 1:
            house1.append(keys)
        if values == 2:
            house2.append(keys)
        if values == 3:
            house3.append(keys)
        if values == 4:
            house4.append(keys)
        if values == 5:
            house5.append(keys)
    print("House 1: ", house1)
    print("House 2: ", house2)
    print("House 3: ", house3)
    print("House 4: ", house4)
    print("House 5: ", house5)


def forward_checking():
    if len(var_unassigned) == 0: # you found a solution
        print_solution(var_assigned) # to be written
        return True
        
    new_var      = select_unassigned(var_domain, var_unassigned) # heuristic: chose the inner columns before the first and last column
    order_values = select_value_order(var_domain, new_var) # heuristic: bottom and top rows first

    #copy_assigned   = deepcopy(self.assigned)
    #copy_unassigned = deepcopy(self.unassigned)
    #copy_domain_all = deepcopy(self.domain_all)

    var_unassigned.remove(new_var)
    copy_domain  = deepcopy(var_domain)

    for new_val in order_values:
           
            var_assigned[new_var] = new_val
            if not check_constraints(var_assigned): # check if assignment is valid
                continue
            
            # forward checking the domain for all remaining variables
            # changes domain_all
            update_domain(var_domain, new_var, new_val)
            if check_domain(var_domain) == True: # returns True if all remaining variables have at least one valid value
                if forward_checking(): # recursive call
                    return True
           
            domain_all = copy_domain
            
         # remove assignment
    var_assigned.pop(new_var)     
    var_unassigned.append(new_var)
    return False # backtrack

forward_checking()