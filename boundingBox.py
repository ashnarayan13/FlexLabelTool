from tkinter import *
from PIL import Image, ImageTk
import os
import argparse
import xml.etree as ET
import xml.etree.cElementTree as etree
import cv2

# colors for the bboxes
COLORS = ['red', 'blue', 'yellow', 'pink', 'cyan', 'green', 'black']


class Labeling():
    def __init__(self, master, arguments):
        # set up the main frame
        self.parent = master
        self.parent.title("LabelTool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width=FALSE, height=FALSE)


        # initialize global state
        self.imageDir = str(arguments.input_directory)
        self.imageList = []
        self.classList = open(str(arguments.classes)).readlines()
        #print(self.classList)
        self.outDir = str(arguments.output_directory)
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None
        self.objectClass = len(self.classList)
        self.choice = int(arguments.choice)
        self.className = []

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None
        self.vl = None
        self.yolobox = []

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.ldBtn = Button(self.frame, text="Load", command=self.loaddir)
        self.ldBtn.grid(row=0, column=2, sticky=W + E)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        self.mainPanel.bind("<Button-1>", self.mouseclick)
        self.mainPanel.bind("<Motion>", self.mousemove)
        self.parent.bind("<Escape>", self.cancelbox)  # press <Espace> to cancel current bbox
        self.parent.bind("s", self.cancelbox)
        self.parent.bind("a", self.previmage)  # press 'a' to go backforward
        self.parent.bind("<space>", self.nextimage)  # press 'd' to go forward
        self.mainPanel.grid(row=1, column=1, rowspan=4, sticky=W + N)

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text='Bounding boxes:')
        self.lb1.grid(row=1, column=2, sticky=W + N)
        self.listbox = Listbox(self.frame, width=22, height=12)
        self.listbox.grid(row=2, column=2, sticky=N)
        self.btnDel = Button(self.frame, text='Delete', command=self.delbox)
        self.btnDel.grid(row=3, column=2, sticky=W + E + N)
        self.btnClear = Button(self.frame, text='ClearAll', command=self.clearbox)
        self.btnClear.grid(row=4, column=2, sticky=W + E + N)
        self.slider = Scale(self.frame, from_=0, to=self.objectClass-1, orient=HORIZONTAL)
        self.slider.grid(row=0, column=1, sticky=W + E)

        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row=5, column=1, columnspan=2, sticky=W + E)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width=10, command=self.previmage)
        self.prevBtn.pack(side=LEFT, padx=5, pady=3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width=10, command=self.nextimage)
        self.nextBtn.pack(side=LEFT, padx=5, pady=3)
        self.progLabel = Label(self.ctrPanel, text="Progress:     /    ")
        self.progLabel.pack(side=LEFT, padx=5)
        self.tmpLabel = Label(self.ctrPanel, text="Go to Image No.")
        self.tmpLabel.pack(side=LEFT, padx=5)
        self.idxEntry = Entry(self.ctrPanel, width=5)
        self.idxEntry.pack(side=LEFT)
        self.goBtn = Button(self.ctrPanel, text='Go', command=self.gotoimage)
        self.goBtn.pack(side=LEFT)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side=RIGHT)

        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(4, weight=1)

    def loaddir(self):
        # get image list
        for filename in os.listdir(self.imageDir):
            img = cv2.imread(os.path.join(self.imageDir,filename))
            if img is not None:
                self.imageList.append(os.path.join(self.imageDir,filename))
        if len(self.imageList) == 0:
            print('No .JPEG images found in the specified dir!')
            return

        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

        # set up output dir
        # self.outDir = ('/home/ashwath/PycharmProjects/labelTool/Labels/001/')
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        self.loadimage()

    def loadimage(self):
        # load image
        imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(imagepath)
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width=max(self.tkimg.width(), 400), height=max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image=self.tkimg, anchor=NW)
        self.progLabel.config(text="%04d/%04d" % (self.cur, self.total))

        # load labels
        self.clearbox()
        self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        if self.choice == 3:
            labelname = self.imagename + '.xml'
        else:
            labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        # bbox_cnt = 0
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    if self.choice ==2:
                        if i == 0:
                            continue
                    if self.choice==2:
                        tmp = [int(t.strip()) for t in line.split()]
                        self.bboxList.append(tuple(tmp))
                    if self.choice == 1:
                        yolo_points = [float(t.strip()) for t in line.split()]
                        width, height = self.img.size
                        x = yolo_points[1] * width
                        w = yolo_points[3] * width
                        y = yolo_points[2] * height
                        h = yolo_points[4] * height
                        xmin = x - w / 2
                        xmax = x + w / 2
                        ymin = y - h / 2
                        ymax = y + h / 2
                        tmp = []
                        tmp.append(yolo_points[0])
                        tmp.append(xmin)
                        tmp.append(ymin)
                        tmp.append(xmax)
                        tmp.append(ymax)
                        self.bboxList.append(tuple(tmp))
                    tmpId = self.mainPanel.create_rectangle(tmp[1], tmp[2],tmp[3], tmp[4], width=2, outline=COLORS[(len(self.bboxList) - 1) % len(COLORS)])
                    self.bboxIdList.append(tmpId)
                    self.listbox.insert(END, '(%d, %d) -> (%d, %d)' % (tmp[1], tmp[2], tmp[3], tmp[4]))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1,
                                            fg=COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])

    def saveimage(self):
        if self.choice == 1:
            self.convertyolo()
            with open(self.labelfilename, 'w') as f:
                for bbox in self.yolobox:
                    # f.write('%d ' % self.slider.get())
                    f.write(' '.join(map(str, bbox)) + '\n')
        elif self.choice == 2:
            with open(self.labelfilename, 'w') as f:
                f.write('%d\n' % len(self.bboxList))
                for bbox in self.bboxList:
                    # f.write('%d ' % self.slider.get())
                    f.write(' '.join(map(str, bbox)) + '\n')
        elif self.choice == 3:
            self.convertxml()
        elif self.choice == 4:
            self.convertcv()
            with open(self.labelfilename, 'w') as f:
                for bbox in self.yolobox:
                    # f.write('%d ' % self.slider.get())
                    f.write(' '.join(map(str, bbox)) + '\n')
        print('Image No. %d saved' % (self.cur))

    def convertyolo(self):
        image = Image.open(self.imageList[self.cur - 1])
        dw = 1. / image.width
        dh = 1. / image.height
        # print(len(self.bboxList))
        for j in self.bboxList:
            x = (j[1] + j[3]) / 2.0
            y = (j[2] + j[4]) / 2.0
            w = j[3] - j[1]
            h = j[4] - j[2]
            x = x * dw
            w = w * dw
            y = y * dh
            h = h * dh
            tmp = [j[0], x, y, w, h]
            self.yolobox.append(tuple(tmp))
    def convertcv(self):
        image = Image.open(self.imageList[self.cur - 1])
        dw = 1. / image.width
        dh = 1. / image.height
        # print(len(self.bboxList))
        for j in self.bboxList:
            x = j[1]
            y = j[2]
            w = j[3] - j[1]
            h = j[4] - j[2]
            tmp = [j[0], x, y, w, h]
            self.yolobox.append(tuple(tmp))

    def convertxml(self):
        image = Image.open(self.imageList[self.cur - 1])
        root = etree.Element('annotation')
        etree.SubElement(root, "folder").text = str(os.path.basename(os.getcwd()))
        etree.SubElement(root, "filename").text = str(str(self.imageList[self.cur-1]).split('/')[-1])
        etree.SubElement(root, "path").text = str(self.imageList[self.cur - 1])
        source = etree.SubElement(root, "source")
        etree.SubElement(source, "database").text = "Unknown"
        size = etree.SubElement(root, "size")
        etree.SubElement(size, "width").text = str(image.width)
        etree.SubElement(size, "height").text = str(image.height)
        etree.SubElement(size, "depth").text = "3"
        etree.SubElement(root, "segmented").text = "0"
        temp = 0
        for j in self.bboxList:
            object = etree.SubElement(root, "object")
            etree.SubElement(object, "name").text = str(self.className[temp])
            etree.SubElement(object, "pose").text = "Unspecified"
            etree.SubElement(object, "truncated").text = "0"
            etree.SubElement(object, "difficult").text = "0"
            bndbox = etree.SubElement(object, "bndbox")
            etree.SubElement(bndbox, "xmin").text = str(j[1])
            etree.SubElement(bndbox, "ymin").text = str(j[2])
            etree.SubElement(bndbox, "xmax").text = str(j[3])
            etree.SubElement(bndbox, "ymax").text = str(j[4])
            temp = temp + 1
        et = ET.cElementTree.ElementTree(root)
        et.write(self.labelfilename, xml_declaration=False, encoding='utf-8', method="xml")

    def mouseclick(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
        else:
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            self.bboxList.append((self.slider.get(), x1, y1, x2, y2))
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.className.append(self.classList[self.slider.get()])
            self.listbox.insert(END, '(%d, %d) -> (%d, %d)' % (x1, y1, x2, y2))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg=COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
        self.STATE['click'] = 1 - self.STATE['click']

    def mousemove(self, event):
        self.disp.config(text='x: %d, y: %d' % (event.x, event.y))
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width=2)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width=2)
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
            self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
                                                          event.x, event.y, \
                                                          width=2, \
                                                          outline=COLORS[len(self.bboxList) % len(COLORS)])

    def cancelbox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def delbox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)

    def clearbox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []
        self.yolobox = []
        self.className = []

    def previmage(self, event=None):
        self.saveimage()
        if self.cur > 1:
            self.cur -= 1
            self.loadimage()

    def nextimage(self, event=None):
        self.saveimage()
        if self.cur < self.total:
            self.cur += 1
            self.loadimage()

    def gotoimage(self):
        idx = int(self.idxEntry.get())
        if 1 <= idx <= self.total:
            self.saveimage()
            self.cur = idx
            self.loadimage()

if __name__ == '__main__':
    root = Tk()
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_directory')
    parser.add_argument('--output_directory')
    parser.add_argument('--classes')
    parser.add_argument('--choice')
    args = parser.parse_args()
    tool = Labeling(root, args)
    root.resizable(width=True, height=True)
    root.mainloop()
