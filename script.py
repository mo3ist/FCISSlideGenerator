import cv2
import os 
from time import time 
from skimage.measure import compare_ssim
from fpdf import FPDF
from PIL import Image

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
RATE = 30	# skipped frames




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
		cv2.imwrite(os.path.join(IMG_DIR, f"{i}.jpg"), img)

def get_imgs():
	"Fetches images for the pdf function"
	img_list = []
	if not os.path.exists(IMG_DIR):
		return img_list

	dir_list = os.listdir(IMG_DIR)
	for file in dir_list:
		if os.path.isfile(os.path.join(IMG_DIR, file)):
			img_list.append(os.path.join(IMG_DIR, file))

	return img_list

def imgs_to_pdf(size):
	"Convert the images in the img_dir to pdf file"
	img_list = get_imgs()
	pdf_file = FPDF(unit = "pt", format = size)
	for img in img_list:
		pdf_file.add_page()
		pdf_file.image(os.path.join(IMG_DIR, img), 0, 0)

	pdf_file.output(os.path.join(IMG_DIR, "output.pdf"), "F")

def main():
	cap = cv2.VideoCapture("vid.mp4")
	success, img = cap.read()
	i = 0
	frame_list = []
	last_frame = None
	t = time()
	while cap.isOpened():
		# breaking the loop when cap is done
		if not success:
			cap.release()
			break
		# skip [rate] frames
		if i%RATE != 0:
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
			diff = difference(last_frame, resized_img) 
			if diff > 15:
				frame_list.append(img)
				last_frame = resized_img

		# dif = difference("img1.png", "img2.png")
		print(f"Frame number {i}, Diff {diff}, Frames : {len(frame_list)}")
		cap.set(1, i)	# read the ith frame
		
		success, img = cap.read()
		i += 1

	print(f"time : {time()-t}")
	save_imgs(frame_list)
	size = [frame_list[0].shape[1], frame_list[0].shape[0]]
	imgs_to_pdf(size)
	print("Done")

if __name__ == "__main__":
	main()