#!/bin/python3

from __future__ import print_function
import cv2
import numpy as np
import argparse
import imutils
from .graph import *
import math
import numpy as np
from cv2 import ximgproc
import sys
from .json_convert import json_convert

from skimage import morphology


def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized


def create_walls_img(src_img):
    img = src_img

    img = cv2.bitwise_not(img)

    kernel = np.ones((5, 5), np.uint8)

    (thresh, img) = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # kernel = np.ones((7,7),np.uint8)
    # kernel = np.array([[5, -5, 5], [-5, 20, -5], [5, -5, 5]], np.uint8)

    img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

    kernel = np.ones((5, 5), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)

    imglab = morphology.label(img)
    cleaned = morphology.remove_small_objects(imglab, min_size=256, connectivity=2)

    img3 = np.zeros((cleaned.shape))  # create array of size cleaned
    img3[cleaned > 0] = 255
    img3 = np.uint8(img3)

    return img3


def draw_graph(img, g, color):
    for i in range(len(g.vertices)):
        if (g.vertices[i].active == True):
            cv2.circle(img, (g.vertices[i].x, g.vertices[i].y), 3, color, -1, 8)

    for edge in g.edges:
        cv2.line(img,
                 (g.vertices[edge.from_id].x, g.vertices[edge.from_id].y),
                 (g.vertices[edge.to_id].x, g.vertices[edge.to_id].y),
                 color,
                 1,
                 8)


def connect_graph(g, max_dist):
    for i in range(0, len(g.vertices)):
        for j in range(0, len(g.vertices)):
            x1 = g.vertices[i].x
            y1 = g.vertices[i].y
            x2 = g.vertices[j].x
            y2 = g.vertices[j].y

            # print(math.sqrt((x1 - x2)**2 + (y1 - y2)**2))
            if (math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) < max_dist):
                g.add_edge(i, j)


def pixel_crosses_line(img, x1, y1, x2, y2):
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    img_height = img.shape[0]
    img_width = img.shape[1]
    t_space = np.linspace(0.0, 1.0, num=2 * max(dx, dy))  # Just in case

    for t in t_space:
        x = t * (x2 - x1) + x1
        y = t * (y2 - y1) + y1
        # print(int(x), int(y))
        # print(img[int(y), int(x)])

        if (round(x) < img_width and round(y) < img_height and img[int(round(y)), int(round(x))] != 0):
            return True

    return False


def cut_off_edges(img, g):
    new_edges = list()

    for edge in g.edges:
        x1 = g.vertices[edge.from_id].x
        y1 = g.vertices[edge.from_id].y
        x2 = g.vertices[edge.to_id].x
        y2 = g.vertices[edge.to_id].y

        if (pixel_crosses_line(img, x1, y1, x2, y2) == False):
            new_edges.append(Edge(edge.from_id, edge.to_id))
            # pass

    g.edges = new_edges


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def ccw(A, B, C):
    return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)


def line_segs_intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


def edge_crosses_line(g, edge, lines):
    for line in lines:
        for x1, y1, x2, y2 in line:
            if (line_segs_intersect(Point(x1, y1), Point(x2, y2),
                                    Point(g.vertices[edge.from_id].x, g.vertices[edge.from_id].y),
                                    Point(g.vertices[edge.to_id].x, g.vertices[edge.to_id].y))):
                return True

    return False


def cut_off_edged_with_lines(img, g, lines):
    new_edges = list()

    for edge in g.edges:
        if (edge_crosses_line(g, edge, lines) == False):
            new_edges.append(Edge(edge.from_id, edge.to_id))
            # pass

    g.edges = new_edges


def is_vert_free(vert_id, g):
    for edge in g.edges:

        # print(edge.from_id, edge.to_id)
        if (edge.from_id != edge.to_id and (edge.from_id == vert_id or edge.to_id == vert_id)):
            return False

    return True


def remove_free_vertices(g):
    for i in range(len(g.vertices)):
        if (is_vert_free(i, g)):
            # print (1)
            g.vertices[i].active = False

    return g


# img = cv2.imread('../res/scaled/3.png', cv2.IMREAD_GRAYSCALE)
# img_col = cv2.imread('../res/scaled/3.png', cv2.IMREAD_COLOR)

# # img = image_resize(img, width=1200)
# # img_col = image_resize(img_col, width=1200)

def erode(img):
    kernel = np.ones((2, 2), np.uint8)
    res = cv2.erode(img, kernel)
    return res


def calc_line_thickness(line, distance_mask):
    for x1, y1, x2, y2 in line:
        # (x1, x2, y1, y2) = line
        mean_thickness = 0
        cntr = 0

        if (x1 == x2):
            # horizontal line
            for y in range(min(y1, y2 + 1), max(y1, y2 + 1)):
                mean_thickness += distance_mask[y, x1]
                cntr += 1
        elif (y1 == y2):
            # vertical line
            for x in range(min(x1, x2 + 1), max(x1, x2 + 1)):
                mean_thickness += distance_mask[y1, x]
                cntr += 1

        return mean_thickness / cntr if (cntr != 0) else 0


def is_line_good(line, distance_mask, threshold):
    for x1, y1, x2, y2 in line:
        if (x1 == x2):
            # horizontal line
            for y in range(min(y1, y2 + 1), max(y1, y2 + 1)):
                if (distance_mask[y, x1] != 0 and distance_mask[y, x1] < threshold):
                    return False
        elif (y1 == y2):
            # vertical line
            for x in range(min(x1, x2 + 1), max(x1, x2 + 1)):
                if (distance_mask[y1, x] != 0 and distance_mask[y1, x] < threshold):
                    return False

        return True


def remove_thin_lines(lines, distance_mask, threshold):
    new_lines = []

    for line in lines:
        # if (is_line_good(line, distance_mask, threshold)):
        if (calc_line_thickness(line, distance_mask) >= threshold):
            new_lines.append(line)

    return new_lines


def dilate(img):
    kernel = np.ones((3, 3), np.uint8)
    res = cv2.dilate(img, kernel)
    return res
