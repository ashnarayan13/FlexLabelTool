# labelTool

This is a labeling tool to label objects to train neural networks. 


## Requirements
The project requires

* python3
* tkinter
* pillow
* xml
* opencv
* argparse

## Run tool

To run the tool. Use the `run.sh` script to run the samples.

or

`python3 boundingBox.py --input_directory=/path/to/images --output_directory=/path/to/output --classes=/path/to/class_list.txt --choice=3` 

set `--choice` to 1 for YOLO darknet format

> class x y w h

set `--choice` to 2 for imagenet format without XML

> number of bounding boxes
> x1 y1 x2 y2

set `--choice` to 3 for Pascal VOC format with XML output

Do not press back when using `--choice` 1 and 3 as they are not converted back to x y coordinates to display and hence will delete the labels

The `--classes` parameter needs a text file with the class names. It picks up the class name to add to the XML.

## Acknowledgements

The base code if from https://github.com/puzzledqs/BBox-Label-Tool
