'''
Created on Nov 6, 2022

@author: myuey
'''
import numpy as np
import pandas as pd
import open3d as o3d
import matplotlib.pyplot as plt
import os
import cv2
from tqdm import tqdm
from stereo_rectification import loop_zhang as lz



def initial_load(tMod,folder, kL_file = "kL.txt", 
                 kR_file = "kR.txt", R_file = "R.txt", 
                 t_file = "t.txt",skiprow = 2, delim = " "):
    '''
    Loads camera constant matrices and related data from text files. 


    Parameters
    ----------
    tMod : float
        translation vector correction constant
    folder : string, optional
        Folder that matrices are stored in, ending in '/'.

    Returns
    -------
    kL : np array of shape (3,3), float
        left camera matrix.
    kR : np array of shape (3,3), float
        right camera matrix.
    r_vec : np array of shape (3,3), float
        rotation matrix between cameras.
    t_vec : np array of shape (3,1), float
        translation vector between cameras.

    '''
    kL = np.loadtxt(folder + kL_file, skiprows=skiprow, delimiter = delim)
    kR = np.loadtxt(folder + kR_file, skiprows=skiprow, delimiter = delim)
    r_vec = np.loadtxt(folder + R_file, skiprows=skiprow, delimiter = delim)
    t_vec = np.loadtxt(folder + t_file, skiprows=skiprow, delimiter = delim)
    t_vec = t_vec[:,np.newaxis]*tMod
    return kL, kR, r_vec, t_vec

def read_pcf(inputfile):
    '''
    Reads a .pcf file with the column names=['x1', 'y1', 'x2', 'y2', 'c', 'x', 'y', 'z', 'r', 'g', 'b']
    and the data separated by spaces with the first two rows being header information/blank
    Parameters
    ----------
    inputfile : TYPE
        File path of pcf file.

    Returns
    -------
    xy1 : numpy array, float64
        x and y coordinates for the first camera, pulled from x1 and y1 columns.
    xy2 : numpy array, float64
        x and y coordinates for the second camera, , pulled from x2 and y2 columns.
    geom_arr : numpy array
        3D points, pulled from x,y,z columns. 
    col_arr : numpy array
        color values in RGB space, pulled from r,g,b columns.
    correl : numpy array
        correlation values pulled from column c. 
    '''
    df  = pd.read_table(inputfile, skiprows=2, sep = " ", names=['x1', 'y1', 'x2', 'y2', 'c', 'x', 'y', 'z', 'r', 'g', 'b'])
    geom = df[['x','y','z']]
    col = df[['r','g','b']]
    geom_arr = geom.to_numpy()
    col_arr = col.to_numpy()
    
    xy1 = df[['x1','y1']]
    xy2 = df[['x2','y2']]
    correl = df['c']
    xy1 = xy1.to_numpy()
    xy1 = np.asarray(xy1, 'float64')
    xy2 = xy2.to_numpy()
    xy2 = np.asarray(xy2, 'float64')
    correl = correl.to_numpy()
    return xy1,xy2,geom_arr,col_arr,correl
def load_color_split(folderL = "",folderR = "", ext = ""):
    imgL = []
    imgR= [] 
    resL = []
    resR = []
    for file in os.listdir(folderL):
        if file.endswith(ext):
            resL.append(file)
    resL.sort()
    for i in resL:
        
        img = plt.imread(folderL + i)
        imgL.append(img[:,:,0])
        imgL.append(img[:,:,1])
        imgL.append(img[:,:,2])
    for file in os.listdir(folderR):
        if file.endswith(ext):
            resR.append(file)  
    resR.sort()
    for i in resR:
        img = plt.imread(folderR + i)
        imgR.append(img[:,:,0])
        imgR.append(img[:,:,1])
        imgR.append(img[:,:,2])
    return np.asarray(imgL),np.asarray(imgR)
def load_images(folderL = "",folderR = "", ext = ""):
    imgL = []
    imgR = [] 
    resL = []
    resR = []
    for file in os.listdir(folderL):
        if file.endswith(ext):
            resL.append(file)
    resL.sort()
    for i in resL:
        img = plt.imread(folderL + i)
        if len(img.shape) > 2:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgL.append(img)     
    for file in os.listdir(folderR):
        if file.endswith(ext):
            resR.append(file)
    resR.sort()
    for i in resR:
        img = plt.imread(folderR + i)
        if len(img.shape) > 2:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgR.append(img)   
    return np.asarray(imgL),np.asarray(imgR)

def convert_np_ply(geo,col,file_name):
    '''
    Converts geometry and color arrays into a .ply point cloud file. 

    Parameters
    ----------
    geo : numpy array
        3D geometry points data
    col : numpy array
        color values in RGB colorspace
    file_name : string
        Name for file path to be created. Adding ".ply" to the end is not needed. 

    Returns
    -------
    None.

    '''
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(geo)
    pcd.colors = o3d.utility.Vector3dVector(col)
    
    if "." in file_name:
        file_name = file_name.split(".",1)[0]
    file_check = file_name + ".ply"
    counter = 1
    while os.path.exists(file_check):
        file_check = file_name +"(" +str(counter)+")" + ".ply"
        counter += 1
    o3d.io.write_point_cloud(file_check, pcd)
    
def conv_pts(ptsList):
    '''
    Converts points from 3D to 2D by removing the 3rd entry.
    For use after unrectifying previously rectified points

    Parameters
    ----------
    ptsList : list of 3D points

    Returns
    -------
    res_list : list of 2D points
    '''

    res_list = []
    for i in ptsList:
        res_list.append([i[0],i[1]])
    return res_list

        
def mark_points(img1,img2,pts1,pts2,xOffset,yOffset, size = 5, showBox = True):
    '''
    Marks points from lists onto images, with an optional box around the target 
    window of the pictures.

    Parameters
    ----------
    img1 : np array
        Left image
    img2 : np array
        Right image
    pts1 : list of np arrays
        List of left side points
    pts2 : list of np arrays
        List of right side points
    xOffset : int
        Distance in pixels offset from edge for x axis of window
    yOffset : int
        Distance in pixels offset from edge for y axis of window
    size : int, optional
        Diameter in pixels of points. The default is 5.
    showBox : Boolean, optional
        Controls display of window borders. The default is True.

    Returns
    -------
    None.

    '''
    print("# POINTS: " + str(len(pts1)))
    img1 = cv2.cvtColor(img1,cv2.COLOR_GRAY2BGR)
    img2 = cv2.cvtColor(img2,cv2.COLOR_GRAY2BGR)
    #place points
    for pt1,pt2 in zip(pts1,pts2):
        '''
        for i in pt1:
            if (isinstance(i, int) or (isinstance(i, float) and i.is_integer())):
                pt1_temp = pt1
                pt1_temp[0] = int(pt1[0])
                pt1 = pt1_temp
        
            

            
        '''    
        all_int = isinstance(pt1[0], int) and isinstance(pt1[1], int) and isinstance(pt2[0], int) and isinstance(pt2[1], int)
        if(all_int):
            color = tuple(np.random.randint(0,255,3).tolist())
            img1 = cv2.circle(img1,tuple(pt1),size,color,-1)
            img2 = cv2.circle(img2,tuple(pt2),size,color,-1)

                
            
    if(showBox):
        #place window boundaries    
        color1 = (255,0,0)
        imshape = img1.shape
        xLim = imshape[1]
        yLim = imshape[0]
        img1 = cv2.rectangle(img1, (xOffset,yOffset), (xLim - xOffset,yLim - yOffset), color1,1) 
        img2 = cv2.rectangle(img2, (xOffset,yOffset), (xLim - xOffset,yLim - yOffset), color1,1) 
    
    plt.subplot(121),plt.imshow(img1)
    plt.subplot(122),plt.imshow(img2)
    plt.show()
    plt.imshow(img1)
    plt.show()
    plt.imshow(img2)
    plt.show()
    

def feature_corr(img1,img2, color = False, thresh = 0.8):
    '''
    Applies SIFT feature detection and FLANN knn feature correlation to find pairs of matching points between two images

    Parameters
    ----------
    img1 : np array
        First image to search for matches in
    img2 : np array
        Second image to search for matches in
    color : Boolean, optional
        Boolean to control if the images are in color or grayscale (single intensity channel)
        The default is False.
    thresh : float, optional
        Threshold for two points to be considered a match. 
        Higher values will lead to more points, but more errors.  The default is 0.8.

    Returns
    -------
    pts1 : np array
        2D points from image 1
    pts2 : np array
        2D points from image 2
    col_vals : np array
        Color values for the matched points in RGB space, found by averaging the two matches.
        If image is grayscale and color argument is False, 
        the single intensity channel will be duplicated twice to shift it into RGB space
    F : np array of shape (3,3)
        fundamental matrix calculated from matching points using LMEDS algorithm      
    '''
    #identify feature points to correlate
    sift = cv2.SIFT_create()

    # find the keypoints and descriptors with SIFT
    sp1, des1 = sift.detectAndCompute(img1,None)
    sp2, des2 = sift.detectAndCompute(img2,None)

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=50)

    flann = cv2.FlannBasedMatcher(index_params,search_params)
    matches = flann.knnMatch(des1,des2,k=2)

    pts1 = []
    pts2 = []

    for i,(m,n) in enumerate(matches):
        if m.distance < thresh*n.distance:
            pts2.append(sp2[m.trainIdx].pt)
            pts1.append(sp1[m.queryIdx].pt)

    pts1 = np.int32(pts1)
    pts2 = np.int32(pts2)
    F, mask = cv2.findFundamentalMat(pts1,pts2,cv2.FM_8POINT)

    #Remove outliers

    pts1 = pts1[mask.ravel()==1]
    pts2 = pts2[mask.ravel()==1]
    pts_val1 = []
    pts_val2 = []
    for i in range(len(pts1)):
        p1 = pts1[i]
        p2 = pts2[i]
        s = img1.shape
        if not (p1[0] >= s[0] or p1[1] >= s[1] or p2[0] >= s[0] or p2[1] >= s[1]):
            pts_val1.append(p1)
            pts_val2.append(p2)
    pts1 = np.asarray(pts_val1)
    pts2 = np.asarray(pts_val2)

    #Copy point color values to array

    col_vals = []
    for i,j in zip(pts1,pts2):
        c1 = img1[i[0]][i[1]]/255
        c2 = img2[j[0]][j[1]]/255
        c_val = (c1+c2)/2
        col_vals.append(c_val)
    if (color):
        col_vals = np.asarray(col_vals)
    else:
        col_vals = np.asarray(col_vals)
        col_vals = np.column_stack((col_vals,col_vals,col_vals))
    
    
    col_vals = np.asarray(col_vals)
    return pts1,pts2,col_vals,F    
def pair_list_corr(img_listL,img_listR, color = False, thresh = 0.8):
    '''
    

    Parameters
    ----------
    img_listL : list of np arrays
        list of images for left side
    
    img_listR : list of np arrays
        list of images for right side
    
    color : Boolean, optional
        Boolean to control if the images are in color or grayscale (single intensity channel)
        The default is False.
    thresh : float, optional
        Threshold for two points to be considered a match. 
        Higher values will lead to more points, but more errors.  The default is 0.8.

    Returns
    -------
    pts1 : np array
        2D points from image 1
    pts2 : np array
        2D points from image 2
    col_vals : np array
        Color values for the matched points in RGB space, found by averaging the two matches.
        If image is grayscale and color argument is False, 
        the single intensity channel will be duplicated twice to shift it into RGB space

    '''
    pts1 = []
    pts2 = []
    col_res = []
    for i,j in tqdm(zip(img_listL,img_listR)):
        res1,res2,col, F = feature_corr(i,j, color, thresh)
        for a,b,c in zip(res1,res2,col):
            pts1.append(a)
            pts2.append(b)
            col_res.append(c)
    return pts1,pts2,col_res

def triangulate(pt1, pt2, r_vec, t_vec, kL_inv, kR_inv):
    '''
    Triangulates the 3D point in real space of 2 points in image space.

    Parameters
    ----------
    pt1 : np array/iterable
        Left 2D point
    pt2 : np array/iterable
        Right 2D point
    r_vec : np array of shape (3,3)
        rotation matrix between cameras
    t_vec : np array of shape (3,1)
        translation vector between cameras
    kL_inv : np array of shape (3,3), float
        Inverse left camera matrix.
    kR_inv : np array of shape (3,3), float
        Inverse right camera matrix.

    Returns
    -------
    res: np array
        3D point

    '''


    #Convert points to column vectors from row vectors and make them 3D

    p1 = np.asarray([[pt1[0]],[pt1[1]],[1]])
    p2 = np.asarray([[pt2[0]],[pt2[1]],[1]])
    #Take inverses of camera matrices and multiply points to transform image points into vectors from camera center
    #Apply transform for right camera points
    v1 = kL_inv @ p1
    v2 = r_vec@(kR_inv @ p2) + t_vec
    #Calculate distances along each vector for closest points, then sum and halve for midpoints

    
    phi = (t_vec[0,0]-v1[0,0]*t_vec[2,0])/(v1[0,0]*v2[2,0]-v2[0,0])
    
    lam = t_vec[2,0]+phi*v2[2,0]
    
    res = [(lam*v1[0,0]+phi*v2[0,0])/2,(lam*v1[1,0]+phi*v2[1,0])/2,(lam*v1[2,0]+phi*v2[2,0])/2]
    
    return np.asarray(res)
def triangulate_solve():
    pass
def triangulate_list(pts1, pts2, r_vec, t_vec, kL_inv, kR_inv):
    '''
    Applies the triangulate function to all points in a list.

    Parameters
    ----------
    pts1 : list of np arrays
        list of left points
    pts2 : list of np arrays 
        list of right points
    r_vec : np array of shape (3,3)
        rotation matrix between cameras
    t_vec : np array of shape (3,1)
        translation vector between cameras
    kL_inv : np array of shape (3,3), float
        Inverse left camera matrix.
    kR_inv : np array of shape (3,3), float
        Inverse right camera matrix.

    Returns
    -------
    res : np array
        3D points in array form for each pair of 2D points

    '''
    res = []
    for i,j in zip(pts1,pts2):
        res.append(triangulate(i,j,r_vec, t_vec, kL_inv, kR_inv))
    return res

def multi_bin_convert_list(imgList,vals, conv_type = np.int32):
    '''
    Converts images in list to lists of binary images 
    based on a list of threshold values
        
    Parameters
    ----------
    imgList : list of np arrays
        list of images to convert to binary
    vals : list of ints
        list of threshold values to check against
    conv_type : type of resulting images. Defaults to np.int32

    Returns
    -------
    bin_list : list of np arrays
        list of binary images. Can be 3 dimensional if vals input has multiple entries

    '''
    bin_list = []
    for i in imgList:
        res_entry = []
        for j in vals:
            res = np.zeros_like(i)
            res[i>j] = 1
            res = res.astype(conv_type)
            res_entry.append(res)
        bin_list.append(res_entry)
    return bin_list

def disp_map(image_shape,pts1,pts2):
    '''
    Generates disparity map from points and result shape

    Parameters
    ----------
    image_shape : Tuple 
        shape of image to map
    pts1 : list of np arrays
        left image points
    pts2 : list of np arrays
        right image points

    Returns
    -------
    res : np array
        Disparity map image

    '''
    res = np.zeros(image_shape)
    for i,j in zip(pts1,pts2):
        dist = int(abs(j[0] - i[0]))
        res[int(i[1]),int(i[0])] = dist
    return res



def rectify_pair(imgL,imgR,F):
    '''
    Rectifies a pair of images using the Loop-Zhang algorithm. 
    
    Parameters
    ----------
    imgL : np array
        left image
    imgR : np array
        right image
    F : np array of shape (3,3)
        Fundamental matrix 

    Returns
    -------
    img1 : np array
        rectified left image 
    img2 : np array
        rectified right image
    H1 : np array of shape (3,3)
        Rectification matrix of left image 
    H2 : np array of shape (3,3)
        Rectification matrix of right image
    '''
    imshape = imgL.shape
    H1 = None
    H2 = None
    revshape = (imshape[1],imshape[0])
    H1, H2 = lz.stereo_rectify_uncalibrated(F, revshape)
    img1 = cv2.warpPerspective(imgL, H1, revshape)
    img2 = cv2.warpPerspective(imgR, H2, revshape)
    return img1,img2, H1, H2

def rectify_lists(imgL,imgR,F):
    '''
    Applies rectify_pair to paired lists of images

    Parameters
    ----------
    imgL : List of left images
 
    imgR : List of right images

    F : numpy array of shape (3,3)
        Fundamental matrix
 

    Returns
    -------
    res_listL : List of rectified left images
    res_listR : List of rectified right images

    '''
    res_listL = []
    res_listR = []
    for i,j in zip(imgL,imgR):
        res1,res2,a,b = rectify_pair(i,j, F)
        res_listL.append(res1)
        res_listR.append(res2)
    return res_listL, res_listR

def mask_inten_list(avg_img, img_list, thresh_val):
    '''
    Masks images in list based on a threshold. All regions where the average of the stack
    below the threshold will be set to 0. 

    Parameters
    ----------
    avg_img : np array
        Image holding average values across the stack
    img_list : list of np arrays
        list of images
    thresh_val : int
        threshold value to check against

    Returns
    -------
    res_list : list of np arrays
        list of masked images

    '''
    mask = np.ones_like(avg_img)
    mask[avg_img < thresh_val] = 0   
    res_list = []
    for i in img_list:
        res_list.append(i*mask)
    return res_list            
        
def gen_color_arr(ref_imageL, ref_imageR, ptsL, ptsR):
    '''
    Returns array of colors pulled from ref_images in the same order as the points in pts. 

    Parameters
    ----------
    ref_imageL and ref_imageR : uint8 array 
        Image data array
    ptsL and ptsR : integer array or list of arrays/tuples
        2D points
        
    Returns
    -------
    res: Numpy array of float RGB colors 

    '''
    res = []
    for i,j in zip(ptsL,ptsR):
        valL = np.asarray([0,0,0])
        valR = np.asarray([0,0,0])
        a = int(np.round(i[0]))
        b = int(np.round(i[1]))
        if(a<ref_imageL.shape[0] and b < ref_imageL.shape[1] and a > 0 and b > 0):
            col = ref_imageL[a,b]/255
            valL = np.asarray([col,col,col])
        c = int(np.round(j[0]))
        d = int(np.round(j[1]))
        if(c<ref_imageR.shape[0] and d < ref_imageR.shape[1] and c > 0 and d > 0):
            col = ref_imageR[c,d]/255
            valR = np.asarray([col,col,col]) 
        entry = np.mean([valL, valR], axis = 0)
        if entry[0] >= 1 or entry[0] < 0:
            entry = np.asarray([0.0,0.0,0.0])
        res.append(entry)
        
    return np.asarray(res)


def gen_color_arr_black(pts_len):
    res = []
    for i in range(pts_len):
        val = np.asarray([0.0,0.0,0.0])
        res.append(val)
    return np.asarray(res, dtype = np.float32)

def conv_rect_map_list(disp_map, HL, HR):
    '''
    Converts a rectified image disparity map into a pair of 
    point lists for the two original images that were used to create the map
    
    Parameters
    ----------
    disp_map : np array
        grayscale image (single intensity value) indicating point disparities
    HL : np array of shape (3,3)
        Rectification matrix for left image
    HR : TYPE
        Rectification matrix for right image

    Returns
    -------
    ptsL : np array
        3D points with third dimension very close to 1 for left image
    ptsR : np array
        3D points with third dimension very close to 1 for right image

    '''
    imshape = disp_map.shape
    pts1 = []
    pts2 = []
    for i in range(imshape[0]):
        for j in range(imshape[1]):
            val = disp_map[i,j]
            pts1.append(np.asarray([i,j]))
            pts2.append(np.asarray([i+val,j]))
    ptsL = []
    ptsR = []
    hL_inv = np.linalg.inv(HL)
    hR_inv = np.linalg.inv(HR)
    for a,b in zip(pts1,pts2):
        sL = HL[2,0]*a[0] + HL[2,1] * a[1] + HL[2,2]
        pL = hL_inv @ np.asarray([[a[0]],[a[1]],[sL]])
        sR = HR[2,0]*b[0] + HR[2,1] * b[1] + HR[2,2]
        pR = hR_inv @ np.asarray([[b[0]],[b[1]],[sR]])
        ptsL.append([pL[0,0],pL[1,0],pL[2,0]])
        ptsR.append([pR[0,0],pR[1,0],pR[2,0]])
    return ptsL,ptsR
def load_imgs_1_dir(folder, ext):
    image_list = []
    res = []
    
    for file in os.listdir(folder):
        if file.endswith(ext):
            res.append(file)
    res.sort()
    for i in res:
        img = cv2.imread(folder + i)
        image_list.append(img)
    return image_list
def calibrate_single(images, ext, rows, columns, world_scaling):

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    #coordinates of squares in the checkerboard world space
    objp = np.zeros((rows*columns,3), np.float32)
    objp[:,:2] = np.mgrid[0:rows,0:columns].T.reshape(-1,2)
    objp = world_scaling* objp
    width = images[0].shape[1]
    height = images[0].shape[0]
    #Pixel coordinates of checkerboards
    imgpoints = [] # 2d points in image plane.
 
    #coordinates of the checkerboard in checkerboard world space.
    objpoints = [] # 3d point in real world space
    chkfrm_list = []
    for frame in images:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #find the checkerboard
        
        ret, corners = cv2.findChessboardCorners(gray, (rows, columns), cv2.CALIB_CB_ADAPTIVE_THRESH)
        if ret == True:
            
            #Convolution size used to improve corner detection. Don't make this too large.
            conv_size = (11, 11)
 
            #opencv can attempt to improve the checkerboard coordinates
            corners = cv2.cornerSubPix(gray, corners, conv_size, (-1, -1), criteria)
            checkframe = cv2.drawChessboardCorners(frame, (rows,columns), corners, ret)
            chkfrm_list.append(checkframe)
            objpoints.append(objp)
            imgpoints.append(corners)
            
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, (width, height), None, None)
    
    return mtx,dist

def calibrate_cameras(kL_folder, kR_folder, ext, rows, columns, world_scaling):
    #load images from each folder in numerical order
    images1 = load_imgs_1_dir(kL_folder, ext)
    images2 = load_imgs_1_dir(kR_folder, ext)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.0001)
    #coordinates of squares in the checkerboard world space
    objp = np.zeros((rows*columns,3), np.float32)
    objp[:,:2] = np.mgrid[0:rows,0:columns].T.reshape(-1,2)
    objp = world_scaling* objp
    #frame dimensions. Frames should be the same size.
    width = images1[0].shape[1]
    height = images1[0].shape[0]
    
    #Apply the opencv camera calibration function  to get kL, kR, R, and t
    #calibrate single cameras to get matrices and distortions
    mtx1, dist_1 = calibrate_single(images1, ext, rows, columns, world_scaling)
    mtx2, dist_2 = calibrate_single(images2, ext, rows, columns, world_scaling)
    
    
    #Pixel coordinates of checkerboards
    imgpoints_left = [] # 2d points in image plane.
    imgpoints_right = []
    objpoints = []
    for frame1, frame2 in zip(images1, images2):
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        c_ret1, corners1 = cv2.findChessboardCorners(gray1, (rows,columns), None)
        c_ret2, corners2 = cv2.findChessboardCorners(gray2, (rows,columns), None)
 
        if c_ret1 == True and c_ret2 == True:
            corners1 = cv2.cornerSubPix(gray1, corners1, (11, 11), (-1, -1), criteria)
            corners2 = cv2.cornerSubPix(gray2, corners2, (11, 11), (-1, -1), criteria)
            objpoints.append(objp)
            imgpoints_left.append(corners1)
            imgpoints_right.append(corners2)
        stereocalibration_flags = cv2.CALIB_FIX_INTRINSIC
    ret, CM1, dist1, CM2, dist2, R, T, E, F = cv2.stereoCalibrate(objpoints, imgpoints_left, imgpoints_right, mtx1, dist_1,
                                                                 mtx2, dist_2, (width, height), criteria = criteria, flags = stereocalibration_flags)
    return mtx1, mtx2, dist_1, dist_2, CM2, R, T

def undistort(images, mtx, dist):
    img_dim = images[0]
    ho,wo = img_dim.shape
    new_mtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (wo,ho), 1, (wo,ho))
    images_res = []
    for img in images:
        # undistort
        dst = cv2.undistort(img, mtx, dist, None, new_mtx)
        # crop the image
        x, y, w, h = roi
        dst = np.asarray(dst[y:y+h, x:x+w])
        images_res.append(dst)
    return new_mtx, images_res

def corr_calibrate(corr_points):
    pass