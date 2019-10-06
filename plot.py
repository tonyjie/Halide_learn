import numpy as np
import matplotlib.pyplot as plt 
def plot_line(x, y):
    plt.figure()
    plt.plot(x, y, '--bo')
    plt.show()

# Gaussian no schedule
# y = [100*100, 1000*1000, 2000*2000, 3000*3000, 4000*4000, 5000*5000, 6400*6400] #pixels
# x = [0.9725, 1.1856, 1.52547, 2.29492, 3.3167, 4.60044, 6.918] #sec
# plt.figure()
# plt.plot(x, y, '--bo')
# plt.show() # Nearly a straight line
# print(x[-1] / y[-1]) # pixel/sec = 5920786
# Throughput = pixel/cycle = (pixel/sec) / (cycle/sec)

# Gaussian schedule
# y = [1000*1500, 2160*3840, 3000*5000, 4000*6000] #pixels
# x = [0.9394, 1.296062, 1.593595, 2.043492] #sec
# plt.figure()
# plt.plot(x, y, '--bo')
# plt.show() # Nearly a straight line
# print((y[-1] - y[0]) / (x[-1] - x[0]))

# Gaussian AOT schedule YES
# y = [0, 1000*1500, 1500*2500, 1800*3000, 2160*3840] #pixels
# x = [0, 3882370, 4728284, 5927119, 9042480] #ns
# plot_line(x, y)
# print((y[-1] - y[1]) / (x[-1] - x[1])) # 1.3167

# Harris schedule
# y = [1000*1500, 2448*3264, 3000*4000, 4000*6000, 5000*7000]
# x = [1.675784, 2.035053, 2.275155, 2.974658, 3.555448]
# plot_line(x, y)
# print((y[-1] - y[0]) / (x[-1] - x[0])) 
# # print((y[1] - y[0]) / (x[1] - x[0]))

# Harris no schedule
# y = [1000*1500, 3000*4000, 4000*6000]
# x = [1.993466, 7.451135, 13.6811]
# plot_line(x, y)
# print((y[-1] - y[0]) / (x[-1] - x[0]))

# Harris AOT schedule YES
# y = [0, 700*1200, 1000*1500, 1200*1700, 1500*2000, 1800*2500, 2448*3264]
# x = [0, 3404634, 5118940, 9063967, 17701344, 19204836, 24129127]
# plot_line(x, y)
# print((y[-1] - y[-3]) / (x[-1] - x[-3]))  # 0.77636

# Gaussian AOT schedule
y = [0, 1200*2000*3, 1500*2500*3, 1800*2800*3,  2448*3264*3]
x = [0, 7426398, 14653264, 16098306, 20044486]
plot_line(x, y)
print((y[-1] - y[2]) / (x[-1] - x[2])) # 2.35954

# Blur+Schedule
# y = [400*250, 648*482, 2000*1000, 4000*2500, 6480*4820]
# x = [0.9397468, 0.9501065, 0.969897, 1.0657695, 1.316892]
# print( (y[2]-y[0]) / (x[2] - x[0]) )
# print( (y[1]-y[0]) / (x[1] - x[0]) )
# plt.figure()
# plt.plot(x, y, '--bo')
# plt.show()

# Blur AOT split 128
# y = [0, 5000*3000, 6000*4000, 10000*7000, 15000*10000, 20000*15000]
# x = [0, 672004, 3555393, 7964829, 22451760, 40491102] # ns
# plot_line(x, y)
# print((y[-1] - y[1]) / (x[-1] - x[1])) #pixel/ns  7.1573695617113176

# Blur AOT split 8, relatively smaller input size. YES
# y = [0, 200*150, 300*200, 400*300, 648*482]
# x = [0, 70823, 91590, 178160, 345589]
# plot_line(x, y)
# print((y[-1] - y[1]) / (x[-1] - x[1])) # 1.0275507

# LinearBlur no schedule
# y = [500*800*3, 768*1280*3, 1000*1500*3, 1500*2300*3, 2000*3000*3]
# x = [1.030171, 1.099747, 1.141085, 1.375899, 1.68443]
# plot_line(x, y)
# print( (y[4] - y[2]) / (x[4] - x[2]) )

# LinearBlur AOT no schedule
# y = [0, 300*500*3, 400*600*3, 500*800*3, 768*1280*3]
# x = [0, 19436752, 23938429, 39402872, 95961144]
# plot_line(x, y)
# print((y[-1] - y[1]) / (x[-1] - x[1])) # 0.0326578

# LinearBlur AOT one-stage schedule YES
# y = [0, 300*500*3, 400*600*3, 500*800*3, 768*1280*3]
# x = [0, 1480418, 1913055, 3314343, 7074907]
# plot_line(x, y)
# print((y[-1] - y[1]) / (x[-1] - x[1])) # 0.446711


# Stencil_chain no schedule. Stencils = 3
# y = [600*1000, 1000*2000, 1536*2560, 2000*3000]
# x = [7.73117, 7.83315, 8.052272, 8.312795]
# plot_line(x, y)
# print ( (y[3] - y[1]) / (x[3] - x[1]) )

# Stencil_chain schedule. Stencils = 3
# y = [600*1000, 1000*2000, 1536*2560, 2000*3000, 3000*5000, 5000*8000, 8000*12000]
# x = [1.236519, 1.239633, 1.291215, 1.296323, 1.29543, 1.569641, 2.345245]
# plot_line(x, y)
# print( (y[-1] - y[-3]) / (x[-1] - x[-3]) )

# Stencil_chain AOT schedule Stencils = 3 YES
# y = [0, 600*1000, 800*1200, 1000*1500, 1000*2000, 1300*2000, 1536*2560]
# x = [0, 612293, 640296, 684162, 925804, 1167404, 1605119]
# plot_line(x, y)
# print( (y[-1] - y[3]) / (x[-1] - x[3]) ) # 2.640905