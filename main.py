import cv2, os, re, pickle
from argparse import ArgumentParser
from shutil import rmtree

parser = ArgumentParser()
parser.add_argument('--image_dir', action='store', required=True, help='dataset path')
parser.add_argument('--save_dir', action='store', required=True, help='dataset path')
args = parser.parse_args()

if os.path.exists(args.save_dir):
	rmtree(args.save_dir)
os.makedirs(args.save_dir)

def extract_minutiae(im_path, save_path):

	im = cv2.cvtColor(cv2.imread(im_path), cv2.COLOR_BGR2GRAY)
	cv2.imwrite('temporary_greyscale.png', im)
	
	os.makedirs('temporary_output')
	command = "./mindtct -m1 temporary_greyscale.png temporary_output/output"
	os.system(command)
	
	with open('temporary_output/output.min') as f:
		lines = f.readlines()
		lines = [x.strip() for x in lines]

	num_minutiae, minutiae = int(lines[2].split(' ')[0]), []
	for line in lines[4:]:
		symbols = re.split('[:;, ]', line)
		symbols = list(filter(None, symbols))
		minutia_type = symbols[5]
		if minutia_type == "BIF":
			minutia_type = 'bifurcation'
		elif minutia_type == "RIG":
			minutia_type = 'ridge_ending'
		else:
			raise CorruptFileError("Unknown minutiae type '{}'".format(minutia_type))

		# [im, x, y, angle, minutiae type, quality]
		cur_minutiae = [im_path, int(symbols[1]), int(symbols[2]), float(symbols[3]) * 11.25, minutia_type, float(symbols[4])]
		minutiae.append(cur_minutiae)

	if len(minutiae) != num_minutiae:
		raise CorruptFileError("The file declared there would be  {} minutiae, but only read {}.".format(num_minutiae, len(minutiae)))

	dirr = '/'.join(save_path.split('/')[:-1])
	if not os.path.exists(dirr):
		os.makedirs(dirr)
	with open(save_path, 'wb') as fp:
		pickle.dump(minutiae, fp)

	# with open (save_path, 'rb') as fp:
	   #  minutiae = pickle.load(fp)

	rmtree('temporary_output')
	os.system('rm temporary_greyscale.png')
	# except:
	# 	print("Error: ", im_path)

for root, dirs, files in os.walk(args.image_dir):
	for file in files:
		if file.endswith(('.bmp', '.tif', '.jpg', 'jpeg', '.png')):
			source_path = os.path.join(root, file)
			save_path = os.path.join(args.save_dir, source_path[len(args.image_dir):].lstrip('/'))
			save_path = '.'.join(save_path.split('.')[:-1] + ['txt'])
			extract_minutiae(source_path, save_path)