import matplotlib.pyplot as plt

# Coordinates of the rectangle points
x1,y1 = 1,2
x2,y2 = 2,2
x3,y3 = 1,1
x4,y4 = 2,1
x5,y5 = 1.5,2
x6,y6 = 1.5,1
rectangle_points = [(x1,y1), (x2,y2), (x3,y3), (x4,y4), (x5,y5), (x6,y6)]

# Coordinate of the interior point
xv, yv = 1.5, 1.5
interior_point = (xv, yv)

# Unzip the rectangle points into x and y coordinates
x_rect, y_rect = zip(*rectangle_points)

Iv = 1

def get_I5I6(Iv,alpha, beta):
    if alpha > 0.5:
        I5 = 2*Iv * (1 - alpha) * (1 - beta)
        I6 = 2*Iv * (1 - alpha) * beta
    else:
        I5 = 2*Iv * alpha * (1 - beta)
        I6 = 2*Iv * alpha * beta  
    return I5, I6

# Plot the rectangle points
def on_click(event):
    if event.inaxes:
        interior_point = (event.xdata, event.ydata)
        alpha = (interior_point[0] - x1) / (x2 - x1)
        beta = (interior_point[1] - y1) / (y4 - y1)
        I1 = (1-alpha) * (1-beta) * Iv
        I2 = alpha * (1-beta) * Iv
        I3 = (1-alpha) * beta * Iv
        I4 = alpha * beta * Iv
        I5, I6 = get_I5I6(Iv, alpha, beta)

        if I1 < 0 or I2 < 0 or I3 < 0 or I4 < 0 or I5 < 0 or I6 < 0:
            I1, I2, I3, I4, I5, I6 = 0, 0, 0, 0, 0, 0
        
        print(f'I1: {I1:.2f}, I2: {I2:.2f}, I3: {I3:.2f}, I4: {I4:.2f}')
        print(f'I5: {I5:.2f}, I6: {I6:.2f}')
        plt.cla()
        plt.scatter(x_rect, y_rect, color='blue', label='Rectangle Points')
        plt.scatter(*interior_point, color='red', label='Interior Point')
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.title('Rectangle Points and Interior Point')
        plt.legend()
        plt.grid(True)
        plt.draw()

fig, ax = plt.subplots()
fig.canvas.mpl_connect('button_press_event', on_click)
plt.scatter(x_rect, y_rect, color='blue', label='Rectangle Points')

# Plot the interior point
plt.scatter(*interior_point, color='red', label='Interior Point')

# Add labels and title
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Rectangle Points and Interior Point')
plt.legend()

# Show the plot
plt.grid(True)
plt.show()