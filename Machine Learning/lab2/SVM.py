from cvxopt.solvers import qp
from cvxopt.base import matrix

import matplotlib
import pylab
import numpy

import random
import math


def generate_class_a(num_samples=5):
    """ Generates class_a of data

        :return list(tuple(double, double, double)): randomly generated data
    """

    class_a = []

    for i in range(0, num_samples):
        random_item_one = (random.normalvariate(-1.5, 1),
                            random.normalvariate(0.5, 1),
                            1.0)
        random_item_two = (random.normalvariate(1.5, 1),
                            random.normalvariate(0.5, 1),
                            1.0)
        class_a.append(random_item_one)
        class_a.append(random_item_two)

    return class_a


def generate_class_b(num_samples=10):
    """ Generates class_b of data

        :return list(tuple(double, double, double)): randomly generated data
    """

    class_b = []
    for i in range(0, num_samples):
        random_item = (random.normalvariate(0.0, 0.5),
                        random.normalvariate(-0.5, 0.5),
                        -1.0)
        class_b.append(random_item)

    return class_b


#linear kernel function
def linearKernel(x, y):
	return numpy.dot(numpy.transpose(x), y) + 1	


#polynomial kernel function
def polynomialKernel(x, y, p):
	return (numpy.dot(numpy.transpose(x), y) + 1)**p


#gausian kernel function
def gausianKernel(x, y, s):
	return math.exp(-(numpy.linalg.norm(matrix(x)-matrix(y))**2)/(2*s**2))


#sigmoid kernel function
def sigmoidKernel(x, y, k, s):
	return math.tanh(numpy.dot(k*numpy.transpose(x), numpy.subtract(y, s)))



#Same random numbers
#random.seed(100)
        
class_a = generate_class_a()
class_b = generate_class_b()

data = class_a + class_b
random.shuffle(data)

print("\n\nData: ")
print(data)

pylab.hold(True)
pylab.plot([p[0] for p in class_a], [p[1] for p in class_a], 'bo')
pylab.plot([p[0] for p in class_b], [p[1] for p in class_b], 'ro')

samplesNumber = len(data)

#building the matrix p
kernelMatrix = numpy.zeros((samplesNumber, samplesNumber))

for i in range(samplesNumber):
	for j in range(samplesNumber):
		#decide which kernel to use in here - polynomial is much better than linear
		#kernelMatrix[i,j] = linearKernel([(data[i])[0], (data[i])[1]],[(data[j])[0], (data[j])[1]])
		kernelMatrix[i,j] = polynomialKernel([(data[i])[0], (data[i])[1]],[(data[j])[0], (data[j])[1]], 4) #CHANGE THIS
		#kernelMatrix[i,j] = gausianKernel([(data[i])[0], (data[i])[1]],[(data[j])[0], (data[j])[1]], 0.5)
		#kernelMatrix[i,j] = sigmoidKernel([(data[i])[0], (data[i])[1]],[(data[j])[0], (data[j])[1]], 1, 2)


yvect = [x[2] for x in data]

P_matrix = matrix(numpy.outer(yvect, yvect) * kernelMatrix)

G_matrix = matrix(numpy.identity(samplesNumber, dtype=int) * -1.0)
Gslack = numpy.diag(numpy.ones(samplesNumber))
G_matrix = numpy.r_[G_matrix, Gslack]

q_vector = matrix([-1.0 for x in range(0, len(data))])
h_vector = matrix([0.0 for x in range(0, len(data))])

hslacks = numpy.ones * 50        #it is well seen for values between 0.1 and 1 (completely different values are needed for linear kernel function)
h_vector = numpy.r_[h_vector, hslacks]


r_dict = qp(P_matrix, q_vector, G_matrix, h_vector)
alpha_array = numpy.array(list(r_dict['x']))

non_zero_indices = numpy.where(alpha_array > 1.0 * (10 ** -5))[0]

print("\n\nAlpha list")
print(alpha_array)

print(non_zero_indices)

non_zero_data = list()
for non_zero_index in non_zero_indices:
    print(non_zero_index)
    data_tuple = data[non_zero_index]
    non_zero_data.append(data_tuple[0:2])


alpha = alpha_array
#indicator function
def indicator(x, y):
	res = 0
	for a in non_zero_indices:
		#res = res + (alpha[a] * yvect[a] * linearKernel([x, y], [(data[a])[0], (data[a])[1]]))
		res = res + (alpha[a] * yvect[a] * polynomialKernel([x, y], [(data[a])[0], (data[a])[1]], 4))
		#res = res + (alpha[a] * yvect[a] * gausianKernel([x, y], [(data[a])[0], (data[a])[1]], 0.5))
		#res = res + (alpha[a] * yvect[a] * sigmoidKernel([x, y], [(data[a])[0], (data[a])[1]], 1, 2))
	return res



#plotting decision boundary
xrange = numpy.arange(-4, 4, 0.05)
yrange = numpy.arange(-4, 4, 0.05)

grid = matrix([[indicator(x, y) for y in yrange] for x in xrange] )


pylab.hold(True)
pylab.plot([p[0] for p in class_a], [p[1] for p in class_a], 'bo')
pylab.plot([p[0] for p in class_b], [p[1] for p in class_b], 'ro')
pylab.contour(xrange, yrange, grid, (-1.0, 0.0, 1.0), colors=('red', 'black', 'blue'), linewidths=(1, 3, 1))
pylab.show()

#https://github.com/ziky90/svm/blob/master/assignment2.py
