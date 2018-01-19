import cv2
import os
import argparse
import xml.etree as ET
import xml.etree.cElementTree as etree
from PIL import Image, ImageTk


def convertxml(bboxList, imageList, im):
    #image = Image.open(imageList)
    root = etree.Element('annotation')
    etree.SubElement(root, "folder").text = str(os.path.basename(os.getcwd()))
    etree.SubElement(root, "filename").text = str(str(im).split('/')[-1])
    etree.SubElement(root, "path").text = str(im)
    source = etree.SubElement(root, "source")
    etree.SubElement(source, "database").text = "Unknown"
    size = etree.SubElement(root, "size")
    etree.SubElement(size, "width").text = str(1280)
    etree.SubElement(size, "height").text = str(720)
    etree.SubElement(size, "depth").text = "3"
    etree.SubElement(root, "segmented").text = "0"
    temp = 0
    for j in bboxList:
        object = etree.SubElement(root, "object")
        etree.SubElement(object, "name").text = "cone"#str(self.className[temp])
        etree.SubElement(object, "pose").text = "Unspecified"
        etree.SubElement(object, "truncated").text = "0"
        etree.SubElement(object, "difficult").text = "0"
        bndbox = etree.SubElement(object, "bndbox")
        etree.SubElement(bndbox, "xmin").text = str(j[0])
        etree.SubElement(bndbox, "ymin").text = str(j[1])
        etree.SubElement(bndbox, "xmax").text = str(j[2])
        etree.SubElement(bndbox, "ymax").text = str(j[3])
        temp = temp + 1
    et = ET.cElementTree.ElementTree(root)
    print(imageList)
    et.write(imageList, xml_declaration=False, encoding='utf-8', method="xml")

def loaddir(input_l_dir,input_i_dir, output):
    # get image list
    height = 720
    width = 1280
    for filename in os.listdir(input_l_dir):
        file = open(os.path.join(input_l_dir, filename), 'r')
        if '.txt' in filename:
            points = []
            print(filename)
            for line in file.readlines():
                temp = []
                x = float(line.split(" ")[1])
                y = float(line.split(" ")[2])
                w = float(line.split(" ")[3])
                h = float(line.split(" ")[4].split("/n")[0])
                print(x,y,w,h)

                filename_im = filename.split(".")[0] + ".png"
                xml_save_loc = filename.split(".")[0] + ".xml"
                xml_save = os.path.join(output, xml_save_loc)
                curr_im = cv2.imread(os.path.join(input_i_dir, filename_im))
                if curr_im is not None:
                    im_h, im_w, im_c = curr_im.shape
                    assert im_h == height
                    assert im_w == width
                x = x * width
                w = w * width
                y = y * height
                h = h * height
                xmin = x - w/2
                xmax = x + w/2
                ymin = y - h/2
                ymax = y + h/2
                temp.append(xmin)
                temp.append(ymin)
                temp.append(xmax)
                temp.append(ymax)
                points.append(temp)
                print(xmax,xmin,ymax,ymin)
                convertxml(points,xml_save, os.path.join(input_i_dir, filename_im))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_image_dir')
    parser.add_argument('--output_label_dir')
    FLAGS = parser.parse_args()

    if not os.path.exists(FLAGS.output_label_dir):
        os.mkdir(FLAGS.output_label_dir)
    input_im_dir = FLAGS.input_image_dir
    input_label_dir = input_im_dir[:-6] + "labels"
    loaddir(input_label_dir,input_im_dir,FLAGS.output_label_dir)
