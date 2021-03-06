import os
import os.path as osp
import torch
import numpy as np
import cv2
from torch.autograd import Variable

this_dir = osp.dirname(__file__)
person_sequence = osp.join(this_dir, "..", "data", "i-LIDS-VID", "sequences")
optical_sequence = osp.join(this_dir, "..", "data", "i-LIDS-VID-OF-HVP", "sequences")


def computeCMC(testID,model):

    nPersons = len(testID)
    cmc_Matrix = torch.zeros(nPersons,nPersons)
    cmc = torch.zeros(nPersons)

    for i in range(nPersons):
        for j in range(nPersons):
            netInputA,netInputB = getTest_pair(testID,i,j,128)
            distanceA,identity_pA,identity_gA,v_pA,v_gA = model(netInputA,netInputA)
            distanceB,identity_pB,identity_gB,v_pB,v_gB = model(netInputB,netInputB)
            #only use v_pA,v_pB for compute
            v_pA = v_pA.data
            v_pB = v_pB.data
            # here we donnot use sqrt
            dst = torch.sum(torch.pow(v_pA - v_pB,2))
            cmc_Matrix[i][j] = dst
        print "now computing: ",i

    for i in range(nPersons):
        value,index = torch.sort(cmc_Matrix[i])
        for j in range(nPersons):
            if index[j] == i:
                indx = j

        for j in range(indx,nPersons):
            cmc[j] = cmc[j] + 1

    cmc = (cmc / nPersons) * 100

    cmcString = ''
    for c in range(0,50):
        cmcString = cmcString + " "+ str(int(cmc[c]))

    return cmcString


def getTest_pair(testID,train_probe_num,train_gallery_num,sampleSeqLength):

    #using sampleSeqLength 128 to compute CMC curve
    test_probe = testID[train_probe_num]
    test_gallery = testID[train_gallery_num]
    image_cam1 = os.listdir(osp.join(person_sequence,"cam1",str(test_probe)))
    optical_cam1 = os.listdir(osp.join(optical_sequence,"cam1",str(test_probe)))
    image_cam2 = os.listdir(osp.join(person_sequence,"cam2",str(test_gallery)))
    optical_cam2 = os.listdir(osp.join(optical_sequence,"cam2",str(test_gallery)))
    image_cam1.sort()
    image_cam2.sort()
    optical_cam1.sort()
    optical_cam2.sort()
    len_cam1 = len(image_cam1)
    len_cam2 = len(image_cam2)

    if len_cam1 > sampleSeqLength:
        actualSampleSeqLenA = sampleSeqLength
        startA = len_cam1-sampleSeqLength
    else:
        actualSampleSeqLenA = len_cam1
        startA = 0

    if len_cam2 > sampleSeqLength:
        actualSampleSeqLenB = sampleSeqLength
        startB = len_cam2-sampleSeqLength
    else:
        actualSampleSeqLenB = len_cam2
        startB = 0

    netInputA = np.zeros((56, 40, 5, actualSampleSeqLenA), dtype=np.float32)
    netInputB = np.zeros((56, 40, 5, actualSampleSeqLenB), dtype=np.float32)

    for m in range(actualSampleSeqLenA):
        img_file = os.path.join(person_sequence,"cam1",str(test_probe),image_cam1[startA+m])
        img = cv2.imread(img_file)/ 255.0
        img = cv2.resize(img,(40,56))

        img_yuv = np.zeros((56,40,3), dtype=np.float64)
        img_yuv[:,:,0] = 0.299*img[:,:,2] + 0.587*img[:,:,1] + 0.114*img[:,:,0]
        img_yuv[:,:,1] = (-0.14713)*img[:,:,2] + (-0.28886)*img[:,:,1] + 0.436*img[:,:,0]
        img_yuv[:,:,2] = 0.615*img[:,:,2] + (-0.51499)*img[:,:,1] + (-0.10001)*img[:,:,0]

        m0  = np.mean(img_yuv[:,:,0]) 
        m1  = np.mean(img_yuv[:,:,1])
        m2  = np.mean(img_yuv[:,:,2])
        v0  = np.sqrt(np.var(img_yuv[:,:,0]))
        v1  = np.sqrt(np.var(img_yuv[:,:,1])) 
        v2  = np.sqrt(np.var(img_yuv[:,:,2])) 
        netInputA[:, :, 0, m] = (img_yuv[:,:,0]-m0)/np.sqrt(v0)
        netInputA[:, :, 1, m] = (img_yuv[:,:,1]-m1)/np.sqrt(v1)
        netInputA[:, :, 2, m] = (img_yuv[:,:,2]-m2)/np.sqrt(v2)
        optical_file = os.path.join(optical_sequence,"cam1",str(test_probe),optical_cam1[startA+m])
        optical = cv2.imread(optical_file)/ 255.0
        optical = cv2.resize(optical,(40,56))
        m3  = np.mean(optical[:,:,1]) 
        m4  = np.mean(optical[:,:,2])
        v3  = np.sqrt(np.var(optical[:,:,1])) 
        v4  = np.sqrt(np.var(optical[:,:,2])) 
        netInputA[:, :, 3, m] = (optical[:,:,1]-m3)/np.sqrt(v3)
        netInputA[:, :, 4, m] = (optical[:,:,2]-m4)/np.sqrt(v4)

    for m in range(actualSampleSeqLenB):
        img_file = os.path.join(person_sequence,"cam2",str(test_gallery),image_cam2[startB+m])
        img = cv2.imread(img_file)/ 255.0
        img = cv2.resize(img,(40,56))

        img_yuv = np.zeros((56,40,3), dtype=np.float64)
        img_yuv[:,:,0] = 0.299*img[:,:,2] + 0.587*img[:,:,1] + 0.114*img[:,:,0]
        img_yuv[:,:,1] = (-0.14713)*img[:,:,2] + (-0.28886)*img[:,:,1] + 0.436*img[:,:,0]
        img_yuv[:,:,2] = 0.615*img[:,:,2] + (-0.51499)*img[:,:,1] + (-0.10001)*img[:,:,0]


        m0  = np.mean(img_yuv[:,:,0]) 
        m1  = np.mean(img_yuv[:,:,1])
        m2  = np.mean(img_yuv[:,:,2])
        v0  = np.sqrt(np.var(img_yuv[:,:,0]))
        v1  = np.sqrt(np.var(img_yuv[:,:,1])) 
        v2  = np.sqrt(np.var(img_yuv[:,:,2])) 
        netInputB[:, :, 0, m] = (img_yuv[:,:,0]-m0)/np.sqrt(v0)
        netInputB[:, :, 1, m] = (img_yuv[:,:,1]-m1)/np.sqrt(v1)
        netInputB[:, :, 2, m] = (img_yuv[:,:,2]-m2)/np.sqrt(v2)
        optical_file = os.path.join(optical_sequence,"cam2",str(test_gallery),optical_cam2[startB+m])
        optical = cv2.imread(optical_file)/ 255.0
        optical = cv2.resize(optical,(40,56))
        m3  = np.mean(optical[:,:,1]) 
        m4  = np.mean(optical[:,:,2])
        v3  = np.sqrt(np.var(optical[:,:,1])) 
        v4  = np.sqrt(np.var(optical[:,:,2])) 
        netInputB[:, :, 3, m] = (optical[:,:,1]-m3)/np.sqrt(v3)
        netInputB[:, :, 4, m] = (optical[:,:,2]-m4)/np.sqrt(v4)

    netInputA = np.transpose(netInputA, (3,2,0,1))
    netInputB = np.transpose(netInputB, (3,2,0,1))

    netInputA = Variable(torch.from_numpy(netInputA).float()).cuda()
    netInputB = Variable(torch.from_numpy(netInputB).float()).cuda()

    return netInputA,netInputB




