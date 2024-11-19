import numpy as np
import sys

argv = [float(a) for a in sys.argv[1:]]
l1 = argv[0] # length of the first side (pixel)
n1 = argv[1] # lattice numbers of the first side
a1 = argv[2] # angle of the first side (degree)

l2 = argv[3] # length of the second side (pixel)
n2 = argv[4] # lattice numbers of the second side
a2 = argv[5] # angle of the second side (degree)

scale = argv[6] # scale parameter for the image (nm/pixel)

def get_coordinates(l1,n1,a1,l2,n2,a2,scale):
    angle_1 = a1/180*np.pi
    angle_2 = a2/180*np.pi
    length_1 = l1/n1
    length_2 = l2/n2

    x1 = length_1*np.cos(angle_1)
    y1 = length_1*np.sin(angle_1)
    x2 = length_2*np.cos(angle_2)
    y2 = length_2*np.sin(angle_2)

    x1 *= scale
    y1 *= scale
    x2 *= scale
    y2 *= scale


    return x1,y1,x2,y2

x1,y1,x2,y2 = get_coordinates(l1,n1,a1,l2,n2,a2,scale)

A = np.array([
    [x1**2, y1**2],
    [x2**2, y2**2],
    [x1*x2, y1*y2],
    ])

b =np.array([
    [17.7**2],
    [17.7**2],
    [17.7**2*np.cos(np.pi/3)],
    ])

piezo_const = np.linalg.inv(np.transpose(A)@A)@np.transpose(A)@b
piezo_const = np.sqrt(piezo_const)
piezo_const = np.around(piezo_const, 2)

print("\ncalibration coefficients (to multipy old piezo constants):")
print("x\ty")
print(f"{piezo_const[0][0]}\t{piezo_const[1][0]}")
