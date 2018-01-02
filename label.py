import cv2
import os
import tkinter
from tkinter import *
from PIL import ImageTk, Image
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input_folder')
FLAGS = parser.parse_args()

def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder,filename))
        if img is not None:
            images.append(os.path.join(folder,filename))
    return images

def startLabel():
    global counter
    global image_paths
    im1 = cv2.imread(image_paths[counter])
    b,g,r = cv2.split(im1)
    im1 = cv2.merge((r,g,b))
    im = Image.fromarray(im1)
    #im = im.resize((600, 600), Image.ANTIALIAS)
    canvas.image = ImageTk.PhotoImage(im)
    canvas.create_image(0, 0, image=canvas.image, anchor='nw')

def addData():
    global counter
    global write_data
    write_data.write(str(image_paths[counter])+'\n')
    counter = counter +1
    canvas.delete("all")
    startLabel()

def skip_data():
    global counter
    global write_data1
    write_data1.write(str(image_paths[counter]) + '\n')
    counter = counter + 1
    canvas.delete("all")
    startLabel()

def exit_loop():
    global write_data
    global write_data1
    write_data.close()
    write_data1.close()
    initialize_nodes.destroy()

def skip_image():
    global counter
    counter = counter + 1
    canvas.delete("all")
    startLabel()

def main():
    global canvas
    global initialize_nodes
    global image_paths
    global write_data
    global write_data1
    global counter
    image_paths = load_images_from_folder(FLAGS.input_folder)
    counter = 0
    write_data = open("containers.txt", "w")
    write_data1 = open("not_containers.txt", "w")
    initialize_nodes = tkinter.Tk()
    initialize_nodes.title("Initialization")
    canvas = Canvas(initialize_nodes, width=600, height=600)
    canvas.pack()
    button = tkinter.Button(initialize_nodes, text="Start", command=startLabel)
    button1 = tkinter.Button(initialize_nodes, text="Container", command=addData)
    button2 = tkinter.Button(initialize_nodes, text="Not Container", command=skip_data)
    button3 = tkinter.Button(initialize_nodes, text="Skip", command=skip_image)
    button4 = tkinter.Button(initialize_nodes, text="Exit", command=exit_loop)
    button.pack(side=LEFT)
    button1.pack(side=LEFT)
    button2.pack(side=LEFT)
    button3.pack(side=LEFT)
    button4.pack(side=LEFT)
    initialize_nodes.mainloop()

if __name__ == '__main__':
    main()
