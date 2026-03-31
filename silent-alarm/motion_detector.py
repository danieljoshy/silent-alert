import cv2
import numpy as np


def detect_motion(prev_frame, curr_frame, threshold):
    """
    Compare two consecutive frames using Gaussian blur + pixel diff.
    Returns (motion_detected: bool, motion_score: float).
    """
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

    prev_blur = cv2.GaussianBlur(prev_gray, (21, 21), 0)
    curr_blur = cv2.GaussianBlur(curr_gray, (21, 21), 0)

    frame_diff = cv2.absdiff(prev_blur, curr_blur)
    _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    motion_score = sum(cv2.contourArea(c) for c in contours)

    return motion_score > threshold, motion_score
