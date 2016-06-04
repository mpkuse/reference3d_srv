#!/usr/bin/env python

import sys
import rospy
from reference3d_srv.srv import *

import cv2
import time
from cv_bridge import CvBridge
from math import *

def render(tx,ty,tz,rx,ry,rz,rd):
    rospy.wait_for_service('render_two_reference_images')
    srv=rospy.ServiceProxy('render_two_reference_images', Render)
    resp=srv(tx,ty,tz,rx,ry,rz,rd)
    return(resp.rgb, resp.depth)

if __name__== "__main__":
    (tx,ty,tz,rx,ry,rz,rw)=(0,0,70,0,0,0.707,0.707)
    rd=2*acos(rw)/pi*180
    
    ts=time.time()
    (rgb,depth)=render(tx,ty,tz,rx,ry,rz,rd)
    te=time.time()
    print 'time:%2.6f' %(te-ts)

    cv_rgb=CvBridge().imgmsg_to_cv2(rgb, "rgb8")
    cv_depth=CvBridge().imgmsg_to_cv2(depth, "mono8")
    cv2.imwrite("rgb.jpg",cv_rgb)
    cv2.imwrite("depth.jpg",cv_depth)
