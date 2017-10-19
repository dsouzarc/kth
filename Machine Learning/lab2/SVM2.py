from cvxopt.solvers import qp
from cvxopt.base import matrix
import numpy, pylab, random, math

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


random.seed(100)


#generating the test dataset
samplesNumber = 20
classA = [(random.normalvariate(-1.5 , 1), random.normalvariate(0.5, 1), 1.0) for i in range(samplesNumber/4)] + [(random.normalvariate(1.5, 1), random.normalvariate(0.5, 1), 1.0) for i in range (samplesNumber/4)]
classB = [(random.normalvariate(0.0 ,0.5), random.normalvariate(-0.5, 0.5), -1.0) for i in range(samplesNumber/2)]
data = classA + classB
random.shuffle(data)


#building the matrix p
kernelMatrix = numpy.zeros((samplesNumber, samplesNumber))
for i in range(samplesNumber):
	for j in range(samplesNumber):
		#decide which kernel to use in here
		#linear seems not to be working, polynomyal is better, etc.
		#kernelMatrix[i,j] = linearKernel([(data[i])[0], (data[i])[1]],[(data[j])[0], (data[j])[1]])
		kernelMatrix[i,j] = polynomialKernel([(data[i])[0], (data[i])[1]],[(data[j])[0], (data[j])[1]], 3)
		#kernelMatrix[i,j] = gausianKernel([(data[i])[0], (data[i])[1]],[(data[j])[0], (data[j])[1]], 0.5)

		#kernelMatrix[i,j] = sigmoidKernel([(data[i])[0], (data[i])[1]],[(data[j])[0], (data[j])[1]], 1, 2)

yvect = [x[2] for x in data]
P = numpy.outer(yvect, yvect) * kernelMatrix

#buliding vector q
q = numpy.ones(samplesNumber) * -1

#building vector h
h = numpy.zeros(samplesNumber)
#adding the slack variables hslack is the vector of Cs

#building matrix G
G = numpy.diag(numpy.ones(samplesNumber) * -1)
#adding the slack variables

hslacks = numpy.ones(samplesNumber) * 1  		#it is well seen for values between 0.1 and 1 (completely different values are needed for linear kernel function)
h = numpy.r_[h, hslacks]
Gslack = numpy.diag(numpy.ones(samplesNumber))
G = numpy.r_[G, Gslack]


# Solve QP problem
r = qp(matrix(P), matrix(q), matrix(G), matrix(h)) 

#extracting non zero values
alpha = numpy.array(list(r['x']))
indexes = (numpy.where(alpha > 1e-5))[0]



#indicator function
def indicator(x, y):
	res = 0
	for a in indexes:
		#res = res + (alpha[a] * yvect[a] * linearKernel([x, y], [(data[a])[0], (data[a])[1]]))
		res = res + (alpha[a] * yvect[a] * polynomialKernel([x, y], [(data[a])[0], (data[a])[1]], 3))
		#res = res + (alpha[a] * yvect[a] * gausianKernel([x, y], [(data[a])[0], (data[a])[1]], 0.5))
		#res = res + (alpha[a] * yvect[a] * sigmoidKernel([x, y], [(data[a])[0], (data[a])[1]], 1, 2))
	return res


#plotting decision boundary
xrange = numpy.arange(-4, 4, 0.05)
yrange = numpy.arange(-4, 4, 0.05)

grid = matrix([[indicator(x, y) for y in yrange] for x in xrange] )


pylab.hold(True)
pylab.plot([p[0] for p in classA], [p[1] for p in classA], 'bo')
pylab.plot([p[0] for p in classB], [p[1] for p in classB], 'ro')
pylab.contour(xrange, yrange, grid, (-1.0, 0.0, 1.0), colors=('red', 'black', 'blue'), linewidths=(1, 3, 1))
pylab.show()
