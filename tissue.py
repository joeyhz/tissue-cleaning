import yaml, os, glob, argparse
from PIL import Image
import numpy as np
import scipy.stats as ss
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('--stack', type=str, required=True)
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()

print(f'Running analysis of stack "{args.stack}"')

try:
    with open('config.yaml') as f:
        config_list = yaml.load(f, Loader=yaml.FullLoader)
        prob_threshold = config_list["prob_threshold"]
        dark_filter = config_list["dark_filter"]
        white_filter = config_list["white_filter"]
        mean = config_list["mean"]
        std = config_list["std"]
        norm = ss.norm(mean, std)
        print(f'Using Mean={mean} and Standard Deviation={std}')
except Exception as e:
    print("Error loading config file:")
    print(e)
    raise Exception("Error loading config file")

folder_path = 'stacks\\' + args.stack
for filename in glob.glob(os.path.join(folder_path, '*.*')):
    print(f'\nProcessing image "{filename}"')
    img = np.array(Image.open(filename))
    img = np.add.reduce(img, -1) # convert colored image to brightness scale 0-765
    if args.debug:
        mx, my = img.shape[0]//2, img.shape[1]//2
        center = img[mx-50:mx+50, my-50:my+50]
        print(f'    [DEBUG] Center: mean={np.mean(center)}, std={np.std(center)}')
    img = img.flatten()
    if args.debug:
        num_1_std = img[np.abs(img-mean) < std].shape[0]
        print(f'    [DEBUG] Num pixels within 1 std of uncleared mean: {num_1_std}')
        print('    [DEBUG] Plotting image histogram')
        plt.hist(img)
        plt.show() 
    img = img[img > dark_filter]
    img = img[img < white_filter]
    dist = norm.pdf(img)
    mean_pr = np.mean(dist) 
    print(f'    Mean uncleared Pr: {round(mean_pr*100, 4)}%')
    if mean_pr < prob_threshold:
        print('    Result: Clearing complete!')
    else:
        print('    Result: Clearing incomplete')

    
    


