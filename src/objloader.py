#import pygame
from OpenGL.GL import *
from PIL import Image
import rospkg
 
def MTL(filename):
    contents = {}
    mtl = None
    for line in open(filename, "r"):
        if line.startswith('#'): continue
        values = line.split()
        if not values: continue
        if values[0] == 'newmtl':
            mtl = contents[values[1]] = {}
        elif mtl is None:
            raise ValueError, "mtl file doesn't start with newmtl stmt"
        elif values[0] == 'map_Kd':
            # load the texture referred to by this declaration
            mtl[values[0]] = values[1]
            #i=Image.open('../model/'+mtl['map_Kd'])
            #i.save('test_t.png')
            #imgSize = i.size
            #rawData = i.tostring()
            #image = Image.fromstring('L', imgSize, rawData).tostring()
            #image.save('test_today.png')
            
            rospack=rospkg.RosPack()
            i=Image.open(rospack.get_path('reference3d_srv')+'/model/'+mtl['map_Kd']).transpose(Image.FLIP_TOP_BOTTOM)
            image=i.convert("RGBA").tostring("raw","RGBA")
            #surf = pygame.image.load(rospack.get_path('reference3d')+'/model/'+mtl['map_Kd'])
            #image = pygame.image.tostring(surf, 'RGBA', 1)
            #ix, iy = surf.get_rect().size
            ix,iy=i.size
            texid = mtl['texture_Kd'] = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texid)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
            #glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, ix, iy, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, image)
        #else:
        #    mtl[values[0]] = map(float, values[1:])
    return contents
 
class OBJ:
    def __init__(self, filename, swapyz=False):
        """Loads a Wavefront OBJ file. """
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
 
        material = None
        self.x_min=10000
        self.y_min=10000
        self.z_min=10000
        self.x_max=-10000
        self.y_max=-10000
        self.z_max=-10000
        for line in open(filename, "r"):
            rospack=rospkg.RosPack()
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = map(float, values[1:4])
                if v[0]<self.x_min:
                    self.x_min=v[0]
                if v[0]>self.x_max:
                    self.x_max=v[0]
                if v[1]<self.y_min:
                    self.y_min=v[1]
                if v[1]>self.y_max:
                    self.y_max=v[1]
                if v[2]<self.z_min:
                    self.z_min=v[2]
                if v[2]>self.z_max:
                    self.z_max=v[2]

                if swapyz:
                    v = v[0], v[2], v[1]
                self.vertices.append(v)
            elif values[0] == 'vn':
                v = map(float, values[1:4])
                if swapyz:
                    v = v[0], v[2], v[1]
                self.normals.append(v)
            elif values[0] == 'vt':
                self.texcoords.append(map(float, values[1:3]))
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
            elif values[0] == 'mtllib':
                self.mtl = MTL(rospack.get_path('reference3d_srv')+'/model/'+values[1])
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(0)
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(0)
                self.faces.append((face, norms, texcoords, material))
 
        print "xyminmax:", self.x_min, self.x_max, self.y_min, self.y_max, self.z_min, self.z_max
        face_1=[]
        face_2=[]
        self.nx=3
        self.ny=3
        self.ratio_x=0.6
        self.ratio_y=0.6
        self.length_x=self.ratio_x*(self.x_max-self.x_min)
        self.length_y=self.ratio_y*(self.y_max-self.y_min)
        if self.nx>1:
            self.step_x=(1-self.ratio_x)*(self.x_max-self.x_min)/(self.nx-1)
        else:
            self.step_x=0
            
        if self.ny>1:
            self.step_y=(1-self.ratio_y)*(self.y_max-self.y_min)/(self.ny-1)
        else:
            self.step_y=0

        blocks=[]
        self.gl_list=[]
        self.center=[]
        for j in range(self.nx*self.ny):
            block=[]
            blocks.append(block)
            self.gl_list.append([])
            self.center.append([])
        count_out=0
        for ii in range(self.nx):
            for jj in range(self.ny):
                center=(self.x_min+self.step_x*ii+self.length_x/2, self.y_min+self.step_y*jj+self.length_y/2)
                self.center[jj*self.nx+ii]=center
        for face in self.faces:
            vertices, normals, texture_coords, material = face
            x1=self.vertices[vertices[0] - 1][0]
            x2=self.vertices[vertices[1] - 1][0]
            x3=self.vertices[vertices[2] - 1][0]
            y1=self.vertices[vertices[0] - 1][1]
            y2=self.vertices[vertices[1] - 1][1]
            y3=self.vertices[vertices[2] - 1][1]
            flag=0

            for ii in range(self.nx):
                for jj in range(self.ny):
                    if x1>=self.x_min+self.step_x*ii and x1<=self.x_min+self.step_x*ii+self.length_x and x2>=self.x_min+self.step_x*ii and x2<=self.x_min+self.step_x*ii+self.length_x and x3>=self.x_min+self.step_x*ii and x3<=self.x_min+self.step_x*ii+self.length_x and y1>=self.y_min+self.step_y*jj and y1<=self.y_min+self.step_y*jj+self.length_y and y2>=self.y_min+self.step_y*jj and y2<=self.y_min+self.step_y*jj+self.length_y and y3>=self.y_min+self.step_y*jj and y3<=self.y_min+self.step_y*jj+self.length_y:
                        blocks[jj*self.nx+ii].append(face)
                        flag=1
            if flag==0:
                count_out=count_out+1
            #blocks[4].append(face)
        print "out_count:", count_out


        #print len(self.faces), len(blocks[0]), len(blocks[1]),len(blocks[2]),len(blocks[3])
        #print self.center[0], self.center[1], self.center[2], self.center[3]
        for j in range(self.nx*self.ny):
            self.gl_list[j] = glGenLists(j+1)
            glNewList(self.gl_list[j], GL_COMPILE)
            glEnable(GL_TEXTURE_2D)
            glFrontFace(GL_CCW)
            for face in blocks[j]:
            #for face in range(len(face_2)):
                vertices, normals, texture_coords, material = face

                mtl = self.mtl[material]
                glBindTexture(GL_TEXTURE_2D, mtl['texture_Kd'])
 
                glBegin(GL_POLYGON)
                for i in range(len(vertices)):
                    #if normals[i] > 0:
                    #    glNormal3fv(self.normals[normals[i] - 1])
                    if texture_coords[i] > 0:
                        glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
                    glVertex3fv(self.vertices[vertices[i] - 1])
                glEnd()
            glDisable(GL_TEXTURE_2D)
            glEndList()

        #self.gl_list[0] = glGenLists(1)
        #glNewList(self.gl_list[0], GL_COMPILE)
        #glEnable(GL_TEXTURE_2D)
        #glFrontFace(GL_CCW)
        #for face in blocks[2]:
        ##for face in range(len(face_2)):
        #    vertices, normals, texture_coords, material = face

        #    mtl = self.mtl[material]
        #    glBindTexture(GL_TEXTURE_2D, mtl['texture_Kd'])
 
        #    glBegin(GL_POLYGON)
        #    for i in range(len(vertices)):
        #        #if normals[i] > 0:
        #        #    glNormal3fv(self.normals[normals[i] - 1])
        #        if texture_coords[i] > 0:
        #            glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
        #        glVertex3fv(self.vertices[vertices[i] - 1])
        #    glEnd()
        #glDisable(GL_TEXTURE_2D)
        #glEndList()
