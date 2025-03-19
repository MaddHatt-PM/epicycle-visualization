import numpy as np
from matplotlib import rc
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.font_manager import fontManager
import svgpathtools
import os

SAMPLE_N = 256
CIRCLE_N = 32
T = np.linspace(0, 2*np.pi, SAMPLE_N+1)

SAVE_FRAMES = False
SAVE_RESULTS = True

COLORS = {
    'dark': {
        'theme': 'dark_background',
        'path' : '#00FFFF',
        'circles' : '#FFFFFF33'
    },
    'light': {
        'theme': 'bmh',
        'path': '#FF5733',
        'circles': '#00000033' 
    }
}
CIRCLE_LINE_WIDTH = 1
TRACEPATH_LINE_WIDTH = 2.5
SINE_LINE_WIDTH = 2
ACTIVE_COLORS = COLORS['light']



# font_list = sorted([f.name for f in fontManager.ttflist])
# print("Available fonts:")
# for font in font_list:
#     print(font)


def square_trajectory():
    r = (((0.0*np.pi<=T) * (T<=0.5*np.pi)) * 1/np.cos(T-0.25*np.pi) +
         ((0.5*np.pi<T) * (T<=1.0*np.pi)) * 1/np.cos(T-0.75*np.pi) +
         ((1.0*np.pi<T) * (T<=1.5*np.pi)) * 1/np.cos(T-1.25*np.pi) +
         ((1.5*np.pi<T) * (T<=2.0*np.pi)) * 1/np.cos(T-1.75*np.pi))
    return np.cos(T) * r, np.exp(T * 1j) * r

def butterfly_trajectory():
    x = np.sin(T) * (np.exp(np.cos(T)) - 2 * np.cos(4*T) - np.pow(np.sin(T/12), 5) )
    y = np.cos(T) * (np.exp(np.cos(T)) - 2 * np.cos(4*T) - np.pow(np.sin(T/12), 5))
    return x, y

def sample_svg(svg_filepath):
    # Verify that the file exists
    if not os.path.exists(svg_filepath):
        raise FileNotFoundError(f"SVG file not found: {svg_filepath}")
        
    # Retrieve the 1st path from the SVG
    paths, _ = svgpathtools.svg2paths(svg_filepath)
    path = svgpathtools.parse_path(paths[0])
    path_length = path.length()
    
    # Calculate the step size for equal spacing
    step = path_length / (SAMPLE_N - 1) if SAMPLE_N > 1 else path_length
    step = path_length / (SAMPLE_N - 1) if SAMPLE_N > 1 else path_length
    
    # Sample points at equal intervals
    x = []
    y = []
    for i in range(SAMPLE_N):
        # Calculate distance along the path
        distance = i * step
        
        # Get the point at this distance
        point = path.point(path.ilength(distance))
        
        # Convert complex number to x, y coordinates
        x.append(point.real)
        y.append(point.imag)
    
    x = np.array(x)
    y = np.array(y)
    x = np.subtract(x, (np.max(x) - np.min(x)) / 2) # Center horizontally
    y = np.subtract(y, (np.max(y) - np.min(y)) / 2) # Center vertically
    y *= -1 # Flip graphic vertically due to how SVGs work

    return x,y

def xi_trajectory():
    x, y = sample_svg('xi.svg')
    # print(len(all_points))
    # x = np.array(all_points[::2])  # Take every even-indexed element (0, 2, 4, ...)
    # y = np.array(all_points[1::2]) * -1
    return x, y

def render_plot(x, y):
    '''Prepare coordinates'''
    z = x + y*1j  # Appending 'j' to a number makes it imaginary
    Z = np.fft.fft(z, SAMPLE_N) / SAMPLE_N  # Transform data into frequency domain and then normalize
    k_sorted = np.argsort(-np.abs(Z))  # Sort Z's indices by frequency's negative amplitude
    Z = Z[k_sorted] # Apply sorted indicies

    '''Initialize plots'''
    goldenRatio = 1.619
    figMultiplier = 10
    fig = plt.figure(figsize=(goldenRatio*figMultiplier, 0.8 * figMultiplier))
    plt.tight_layout(w_pad=-2)
    gridspec = GridSpec(2,2, figure=fig, width_ratios=[1.619,1], height_ratios=[1,1], hspace=0.4, wspace=0.1)

    '''Epicycle plot'''
    epicycle_plt = fig.add_subplot(gridspec[:,0])  # Create epicycle subplot that spans 2 rows
    epicycle_plt.set_title(f'Epicycle Approximation with {CIRCLE_N} Circles')
    epicycle_plt.set_xlabel('Real Component', labelpad=16)
    epicycle_plt.set_ylabel('Imaginary Component', labelpad=16)
    epicycle_plt.set_aspect('equal', adjustable='box')  # Make epicycle_plt square
    epicycle_plt.set_box_aspect(1)  # Make epicycle_plt square (unsure why both are needed)

    plt.plot(x, y, 'gray', linewidth=0)[0]  # Base plot to draw on top of
    
    tracer_points = []
    tracer_color = ACTIVE_COLORS['path']
    tracer_path = plt.plot([], [], tracer_color, linewidth=TRACEPATH_LINE_WIDTH)[0]

    circles = []
    circle_color = ACTIVE_COLORS['circles']
    for _ in range(CIRCLE_N):
        circles.append(plt.plot([], [], circle_color, linewidth=CIRCLE_LINE_WIDTH)[0])

    '''Real plot'''
    real_plot = fig.add_subplot(gridspec[0, 1])
    real_plot.set_title("Real component")
    real_plot.set_xlim(0, 2 * np.pi)
    real_plot.set_ylim(-np.max(np.abs(Z)), np.max(np.abs(Z)))
    real_plot.set_xlabel('Time', labelpad=2, fontsize=13)
    real_plot.set_ylabel('Magnitude', labelpad=2, fontsize=13)
    # real_plot.set_ylim(-2, 2) 
    real_points = []
    real_color = ACTIVE_COLORS['path']
    real_path = plt.plot([], [], real_color, linewidth=SINE_LINE_WIDTH)[0]

    '''Imaginary Plot'''
    imaginary_plot = fig.add_subplot(gridspec[1, 1])
    imaginary_plot.set_title("Imaginary component")
    imaginary_plot.set_xlabel('Time', labelpad=2, fontsize=13)
    imaginary_plot.set_ylabel('Magnitude', labelpad=2, fontsize=13)
    imaginary_plot.set_xlim(0, 2 * np.pi)
    imaginary_plot.set_ylim(-2, 2)
    imaginary_points = []
    imaginary_color = ACTIVE_COLORS['path']
    imaginary_path = plt.plot([], [], imaginary_color, linewidth=SINE_LINE_WIDTH)[0]
    
    if SAVE_FRAMES:
        save_dir = f'Renders--{SAMPLE_N}Samples--{CIRCLE_N}Circle'
        os.makedirs(save_dir, exist_ok=True)

    if SAVE_RESULTS:
        save_dir = f'EndResults--{SAMPLE_N}Samples'
        os.makedirs(save_dir, exist_ok=True)


    for i in range(len(Z)+1):
        # compute the IDFT sum, but with descending magnitudes # DOUBLE CHECK LATER
        centers = np.pad(np.cumsum(Z * np.exp(1j * k_sorted * T[i])), [1,0])

        for k in range(CIRCLE_N):
            circles[k].set_data(
                np.abs(Z[k]) * np.cos(T) + centers[k].real,
                np.abs(Z[k]) * np.sin(T) + centers[k].imag)
        
        endpoint = [centers[k].real, centers[k].imag]
        tracer_points.append(endpoint)
        tracer_path.set_data(*zip(*tracer_points))

        real_points.append([i/SAMPLE_N * 2*np.pi, centers[k].real])
        real_path.set_data(*zip(*real_points))
        real_ylim = np.max([np.abs(real_plot.get_ylim()[1]), np.abs(centers[k].real * 1.1)])
        real_plot.set_ylim(-real_ylim, real_ylim)

        imaginary_points.append([i/SAMPLE_N * 2*np.pi, centers[k].imag])
        imaginary_path.set_data(*zip(*imaginary_points))
        imaginary_ylim = np.max([np.abs(imaginary_plot.get_ylim()[1]), np.abs(centers[k].imag * 1.1)])
        imaginary_plot.set_ylim(-imaginary_ylim, imaginary_ylim)

        if SAVE_FRAMES:
            plt.savefig(f'{save_dir}/{SAMPLE_N}S-{CIRCLE_N}C--{i:03}',
                        dpi=300,
                        bbox_inches='tight')
        


        plt.draw()
        if SAVE_RESULTS is False:
            plt.pause(1/60)

    if SAVE_RESULTS:
        plt.savefig(f'{save_dir}/{CIRCLE_N:03}C',
            dpi=300,
            bbox_inches='tight')

    plt.pause(0.1)
    plt.close()



if __name__ == '__main__':
    plt.style.use(ACTIVE_COLORS['theme'])
    plt.rcParams.update({
        'font.size': 12,
        # "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["SF Pro Display"],
        'axes.titleweight': 'bold',
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        'savefig.facecolor': 'white',  # Important when saving
    })
    # x, y = square_trajectory()
    # x, y = butterfly_trajectory()
    x, y = sample_svg('xi.svg')
    for i in range(48, 64):
        CIRCLE_N = i
        render_plot(x, y)