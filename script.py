import cv2
import os 
from skimage.measure import compare_ssim
from fpdf import FPDF
from PIL import Image
import sys

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

def get_img_dir():
	"Get a new image directory (For reusage purposes)"
	base = "output"
	i = 0
	while True:
		path = os.path.join(CURRENT_PATH, f"{base}{i}")
		if not os.path.exists(path):
			return path
		i += 1

IMG_DIR = get_img_dir()
IMG_EXT = "jpg"

class PDF(FPDF):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def header(self):
		self.set_font('Arial', 'B', 8)
		self.cell(w=30, h = 0, txt = 'FCISSlideGenerator', border = 0, ln = 0, align = '', fill = False, link = 'https://github.com/mo3ist/FCISSlideGenerator')
		self.ln(20)

def difference(img1, img2):
	"Takes 2 images as numpy arrays then finds the difference percentage."
	similarity, _ = compare_ssim(img1, img2, full=True)	# compare the images
	diff_perc = 100 - (similarity*100) 
	return diff_perc

def save_imgs(img_list):
	"Saves images in the script's directory"
	if not os.path.exists(IMG_DIR):
		os.mkdir(IMG_DIR)
	for i, img in enumerate(img_list):
		cv2.imwrite(os.path.join(IMG_DIR, f"{i}.{IMG_EXT}"), img)

def get_imgs():
	"Fetches images for the pdf function"
	img_list = []
	if not os.path.exists(IMG_DIR):
		return img_list

	dir_list = os.listdir(IMG_DIR)
	for file in sorted(dir_list):
		if os.path.isfile(os.path.join(IMG_DIR, file)):
			img_list.append(os.path.join(IMG_DIR, file))
	return img_list

def imgs_to_pdf(size):
	"Convert the images in the img_dir to pdf file"
	pdf_file = PDF(unit = "pt", format = (size[0], size[1] + 40))
	for i in range(len(os.listdir(IMG_DIR))):
		img_path = os.path.join(IMG_DIR, f"{i}.{IMG_EXT}")
		pdf_file.add_page()
		pdf_file.image(img_path, 0, 40)

	pdf_file.output(os.path.join(IMG_DIR, "output.pdf"), "F")

def main(vid, diff_perc, frame_rate):
	cap = cv2.VideoCapture(vid)
	frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	success, img = cap.read()
	i = 0
	frame_list = []
	last_frame = None
	while cap.isOpened():
		# breaking the loop when cap is done
		if not success:
			cap.release()
			break
		# skip [rate] frames
		if i%frame_rate != 0:
			i += 1
			continue	# skip
		# to gray scale
		gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		# resize
		resized_img = cv2.resize(gray_img,(720,480),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)
		diff = None
		# first frame
		if not frame_list:
			frame_list.append(img)
			last_frame = resized_img
		else:
			# append if different enough
			diff = round(difference(last_frame, resized_img)) 
			if diff > diff_perc:
				frame_list.append(img)
				last_frame = resized_img

		print(f"Frame number {min(i, frame_count)}/{frame_count}, Diff {diff}, Frames : {len(frame_list)}")
		cap.set(1, i)	# read the ith frame
		
		success, img = cap.read()
		i += 1

	save_imgs(frame_list)
	size = [frame_list[0].shape[1], frame_list[0].shape[0]]
	imgs_to_pdf(size)
	print("#### Done ####")

if __name__ == "__main__":
	try:
		vid = sys.argv[1]
		diff_perc = int(sys.argv[2])
		frame_rate = int(sys.argv[3])
		main(vid, diff_perc, frame_rate)
	except:
		print("USAGE: python3 script.py video_name.mp4 <int:difference_between_frames> <int:skip_frames>")
		print("E.G.: python3 script.py video_name.mp4 5 30")