import numpy as np
from cpmpy import *
from cpmpy.solvers import *
from cpmpy_hakank import * 

def print_solution(a):
    """
    Print the solution.
    """
    # The selected intervals, as indices in each interval list
    xval = a[0].value()
    n = len(xval)
    #print(xval)
    # The selected intervals, as intervals
    sols = [intervals[i][xval[i]] for i in range(n)]
    print(sols)
    print(flush=True)
    return sols

def reduce_overlaps(intervals):
    
    # Convert the list of intervals to a list of flattened lists
    # for use with Element below.
    intervals_flatten = []
    for interval in intervals:
        intervals_flatten.append(cpm_array(flatten_lists(interval))) #list of cpm arrays
    intervals_flatten = cpm_array(intervals_flatten) #cpm_array[cpm_array[interval]]
    
    # We need all values to create the domains of the selected interval 
    # values
    all_values = flatten_lists(intervals_flatten) #cpmpy_hakank all interval's values
    max_val = max(all_values) #max value in the intervals
    min_val = min(all_values) #min value in the intervals
    
    n = len(intervals) #intervals size
    lens = [len(interval) for interval in intervals] #size of each interval

    #
    # Decision variables
    #
    model = Model()

    # x[i] is the selected interval for the i'th interval list
    # This creates the 5 interval variables that can have values from 0 to 13
    x = intvar(0,max(lens),shape=n,name="x") #intvar(0, max size  for each of the 5 interval variables = 13, shape = number of intervals, name to give the variables )
    
    # Reduce the domain (the possible values) of each interval list
    # (since they have different lengths)
    for i in range(n):
        model += [x[i] < lens[i]] #add constraints to the to the interval variables, limit each variable value

    # starts[i] is the start value of the i'th selected interval
    starts = intvar(min_val,max_val,shape=n,name="starts")
    # ends[i] is the end value of the i'th selected interval    
    ends   = intvar(min_val,max_val,shape=n,name="ends")

    #
    # Main constraints:
    #  - Pick exactly one of the intervals from each intervals list
    #  - Ensure that there are no overlaps between any of selected intervals.
    #

    # get the values of the selected intervals
    for i in range(n):
        # Use Element to obtain the start and end values of the selected 
        # interval. We have to use the following construct with Element 
        # since CPMPy does not (yet) support this syntax:
        #    starts[i] = intervals[x[i],0]
        #    ends[i]   = intervals[x[i],1]
        model += [starts[i] == Element(intervals_flatten[i],x[i]*2+0), # corresponds to: starts[i] = intervals[x[i],0]
                  ends[i]   == Element(intervals_flatten[i],x[i]*2+1), # corresponds to: ends[i]   = intervals[x[i],1]
                  ]

    # Ensure that the i'th selected interval don't overlap with
    # the rest of the intervals (the j'th interval)
    for i in range(n):
        for j in range(i+1,n):           
            # Ensure that the start value of one interval is not inside the other interval
            # model += [~( (starts[i] > starts[j]) & (starts[i] < ends[j])),
            #         ~( (starts[j] > starts[i]) & (starts[j] < ends[i])) ]
            model += [~((starts[i] > starts[j]) & (starts[i] < ends[j])), 
                      ~((starts[j] > starts[i]) & (starts[j] < ends[i]))]

    # Print all solutions.
    # This method is defined in http://hakank.org/cpmpy/cpmpy_hakank.py
    # ortools_wrapper(model,[x],print_solution)
    # Collect the solutions in an array
    solutions = []
    def get_solution(a):
        xval = a[0].value()
        # print(xval)
        sol = [intervals[i][xval[i]] for i in range(n)]
        # print("sol:",sol)        
        solutions.append(sol)
    ortools_wrapper2(model,[x],get_solution)
        
    return np.array(solutions)
