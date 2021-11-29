import numpy as np 

# Array has the following characteristics
# n 1's and then x 0's. After x 0's we get 16K bits of data
# There may be an error where in the n 1's there is a 0. Need to avoidn this false positive

# data: directly coming from the reciever
# data_length: how many bits to return
# pattern: How many zeros after the 1's?
def find_pattern_in_set(data, data_length, pattern):
    # First find all locations of zeros
    zeros = np.where(data == 0)[0]
    if zeros.size < 1:
        raise ValueError('No 0\'s found in this set')

    # Theoretically then, the first '0' indicates the start of the data
    # Need to verify that this '0' isn't a false positives
    for zero in zeros:
        if np.sum(data[zero:zero+pattern]) > 0:
            continue
        else:
            real_start = zero + pattern
            break
    
    return data[real_start: real_start+data_length]


if __name__=='__main__':
    data = np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,0,0,0,0,0,0,1,1,1,0,0])
    data_dummy = np.array([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1])
    print(find_pattern_in_set(data, 8, 3))