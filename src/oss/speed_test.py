import numpy as np
import cProfile, pstats, io

input_size = 2457600
#since I don't have your image, I made do with a random sample of 8bit numbers.
test_input = np.random.randint(0, 256, input_size)
#to check that we get the correct result, set input_size to 2
#and uncomment the line below
#test_input = [255, 7]

#your function for the speed comparison purposes
def intToBits(x):
    send = str(bin(x).lstrip('0b'))
    send = send.zfill(8)
    return send

#note, that in this case x is the whole array, not just one number
#to make the full use of the vectorization
#also the output is not a bitfield, but a string
#the > 0 at the end is to convert the result into booleans.
#strictly speaking it isn't necessary if you are fine with 0 1 integers.
def binary_repr(x):
    return(
    np.dstack((
    np.bitwise_and(x, 0b10000000) >> 7,
    np.bitwise_and(x, 0b1000000) >> 6,
    np.bitwise_and(x, 0b100000) >> 5,
    np.bitwise_and(x, 0b10000) >> 4,
    np.bitwise_and(x, 0b1000) >> 3,
    np.bitwise_and(x, 0b100) >> 2,
    np.bitwise_and(x, 0b10) >> 1,
    np.bitwise_and(x, 0b1)
    )).flatten() > 0)

#starting the profiler.
pr = cProfile.Profile()
pr.enable()

#the two computations that we want to compare
a = []
for i in range(input_size):
    a.append(intToBits(test_input[i]))
#print(a)
b = binary_repr(test_input)
#print(b)

#the comparison
sortby = 'cumulative'
pr.disable()
s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())