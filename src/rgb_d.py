#!/usr/bin/env python


import rospy
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
from sensor_msgs.msg import Image as Image_msgs
from reference3d_srv.srv import *

import sys
#import pygame
#from pygame.locals import *
#from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import cv2
import numpy
import time
import math
import rospkg
 
# IMPORT OBJECT LOADER
from objloader import *
from cv_bridge import CvBridge
from time import sleep

#glutInit('pipikk')    
#glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
#glutInitWindowSize(188,120)
#glutCreateWindow('test')

#glutSetWindow(1)
#rospack=rospkg.RosPack()
#obj = OBJ(rospack.get_path('reference3d_srv')+'/model/level_1_0_0.obj') 

def handle_render(req):
    global tx,ty,tz,rx,ry,rz,rd,flag
    global img,img2
    tx=req.tx
    ty=req.ty
    tz=req.tz
    rx=req.rx
    ry=req.ry
    rz=req.rz
    rd=req.rd
    flag=False
    while flag==False:
        print "waiting"
        sleep(0.001)

    bridge = CvBridge()
    #return RenderResponse(numpy.array(img2), numpy.array(img))
    return RenderResponse(bridge.cv2_to_imgmsg(numpy.array(img2), "mono8"), bridge.cv2_to_imgmsg(numpy.array(img), "mono8"))

    #print "window",window
    #global obj
    #viewport = (188,120)
    #FOV=55####FOV of the height (tan (FOV/2)=(height-c_y)/f_y)
    #far=120.0
    #near=3
    ###########################################
    #
    #glutInit('pipikk')
    #glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    #glutInitWindowSize(188,120)
    #glutCreateWindow('test')
    #glMatrixMode(GL_PROJECTION)
    #glLoadIdentity()
    #width, height = viewport
    #gluPerspective(FOV, width/float(height), near, far)
    #glEnable(GL_DEPTH_TEST)
    ##glEnable(GL_CULL_FACE)
    ##glCullFace(GL_BACK)
    #glMatrixMode(GL_MODELVIEW)



if __name__ == '__main__':


    print 'pipikk_main'
    rospy.init_node('reference3d_server')
    s=rospy.Service('render_two_reference_images', Render, handle_render)
    #glutIdleFunc(rospy.spin())
    #rospy.spin()
    #print 'pipikk_rosspin'

    viewport = (188,120)
    FOV=55####FOV of the height (tan (FOV/2)=(height-c_y)/f_y)
    far=120.0
    near=3
    ##########################################
    width, height = viewport
    glutInit('pipikk')
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(width,height)
    glutCreateWindow('srv')
    #glutSetWindow(1)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV, width/float(height), near, far)
    glEnable(GL_DEPTH_TEST)
    #glEnable(GL_CULL_FACE)
    #glCullFace(GL_BACK)
    glMatrixMode(GL_MODELVIEW)
    rospack=rospkg.RosPack()
    obj = OBJ(rospack.get_path('reference3d_srv')+'/model/level_2_0_0.obj')
    #glutDisplayFunc(handle_render)
    #r=rospy.Rate(60)

    global flag,img,img2
    flag=True
    print "service ready"
    while not rospy.is_shutdown():
        if flag==False:
            print "start rendering"
            print tx,ty,tz,rd,rx,ry,rz
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            glRotate(rd, rx, ry, -rz)
            glTranslate(tx, ty, -tz)
            #glRotate(rd, rx, ry, rz)
            #glTranslate(tx, ty, tz)
            
            index=0
            distance=math.sqrt((-tx-obj.center[0][0])*(-tx-obj.center[0][0])+(-ty-obj.center[0][1])*(-ty-obj.center[0][1]))
            for ii in range(obj.nx):
                for jj in range(obj.ny):
                    if math.sqrt((-tx-obj.center[jj*obj.nx+ii][0])*(-tx-obj.center[jj*obj.nx+ii][0])+(-ty-obj.center[jj*obj.nx+ii][1])*(-ty-obj.center[jj*obj.nx+ii][1]))<distance:
                        index=jj*obj.nx+ii
                        distance=math.sqrt((-tx-obj.center[jj*obj.nx+ii][0])*(-tx-obj.center[jj*obj.nx+ii][0])+(-ty-obj.center[jj*obj.nx+ii][1])*(-ty-obj.center[jj*obj.nx+ii][1]))
                        #print "ii,jj", ii, jj


            print "index:", index
            glCallList(obj.gl_list[index])
            #pygame.display.flip()
            glutSwapBuffers()
            data = glReadPixels(0, 0, width, height, GL_DEPTH_COMPONENT, GL_UNSIGNED_BYTE)
            data2 = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
            img2= Image.fromstring('RGB', (width, height), data2)
            img = Image.fromstring('L', (width, height), data)
            img2 = img2.transpose(Image.FLIP_TOP_BOTTOM)
            img2 = img2.convert('L')
            img = img.transpose(Image.FLIP_TOP_BOTTOM)

            print "stop rendering"
            flag=True
        else:
            sleep(0.001)




            #return RenderResponse(img2,img)
            #return RenderResponse(bridge.cv2_to_imgmsg(numpy.array(img2), "mono8"), bridge.cv2_to_imgmsg(numpy.array(img), "mono8"))
            #pub1.publish(bridge.cv2_to_imgmsg(numpy.array(img2), "mono8"))
            #pub2.publish(bridge.cv2_to_imgmsg(numpy.array(img), "mono8"))
            #r.sleep()
