import os
import os.path as osp
import random
import numpy as np
import cv2
import torch
import matplotlib.pyplot as plt

# sampleSeqLength = 16
this_dir = osp.dirname(__file__)
person_sequence = osp.join(this_dir, "..", "data", "i-LIDS-VID", "sequences")
optical_sequence = osp.join(this_dir, "..", "data", "i-LIDS-VID-OF-HVP", "sequences")

im_mean = [124, 117, 104]
im_std = [0.229, 0.224, 0.225]

def same_pair(batch_number, sampleSeqLength, is_train=True):

    image_cam1 = os.listdir(osp.join(person_sequence,"cam1",str(batch_number)))
    optical_cam1 = os.listdir(osp.join(optical_sequence,"cam1",str(batch_number)))
    image_cam2 = os.listdir(osp.join(person_sequence,"cam2",str(batch_number)))
    optical_cam2 = os.listdir(osp.join(optical_sequence,"cam2",str(batch_number)))
    # print batch_number
    image_cam1.sort()
    image_cam2.sort()
    optical_cam1.sort()
    optical_cam2.sort()
    len_cam1 = len(image_cam1)
    len_cam2 = len(image_cam2)
    actualSampleSeqLen = sampleSeqLength
    startA = int(random.random()* ((len_cam1 - actualSampleSeqLen) + 1))   
    startB = int(random.random()* ((len_cam2 - actualSampleSeqLen) + 1)) 
    # print startA,startB
    netInputA = np.zeros((56, 40, 5, actualSampleSeqLen), dtype=np.float32)
    netInputB = np.zeros((56, 40, 5, actualSampleSeqLen), dtype=np.float32)
    #########for debug not using optical#############
    # netInputA = np.zeros((56, 40, 3, actualSampleSeqLen), dtype=np.float32)
    # netInputB = np.zeros((56, 40, 3, actualSampleSeqLen), dtype=np.float32)


    for m in range(actualSampleSeqLen):
        img_file = os.path.join(person_sequence,"cam1",str(batch_number),image_cam1[startA+m])
        img = cv2.imread(img_file)/ 255.0
        img = cv2.resize(img,(40,56))
        # BGR TO YUV
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
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
        
        optical_file = os.path.join(optical_sequence,"cam1",str(batch_number),optical_cam1[startA+m])
        optical = cv2.imread(optical_file)/ 255.0
        optical = cv2.resize(optical,(40,56))
        m3  = np.mean(optical[:,:,1]) 
        m4  = np.mean(optical[:,:,2])
        v3  = np.sqrt(np.var(optical[:,:,1])) 
        v4  = np.sqrt(np.var(optical[:,:,2])) 
        netInputA[:, :, 3, m] = (optical[:,:,1]-m3)/np.sqrt(v3)
        netInputA[:, :, 4, m] = (optical[:,:,2]-m4)/np.sqrt(v4)

    for m in range(actualSampleSeqLen):
        img_file = os.path.join(person_sequence,"cam2",str(batch_number),image_cam2[startB+m])
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
        optical_file = os.path.join(optical_sequence,"cam2",str(batch_number),optical_cam2[startB+m])
        optical = cv2.imread(optical_file)/ 255.0
        optical = cv2.resize(optical,(40,56))
        m3  = np.mean(optical[:,:,1]) 
        m4  = np.mean(optical[:,:,2])
        v3  = np.sqrt(np.var(optical[:,:,1])) 
        v4  = np.sqrt(np.var(optical[:,:,2])) 
        netInputA[:, :, 3, m] = (optical[:,:,1]-m3)/np.sqrt(v3)
        netInputA[:, :, 4, m] = (optical[:,:,2]-m4)/np.sqrt(v4)

    netInputA = np.transpose(netInputA, (3,2,0,1))
    netInputB = np.transpose(netInputB, (3,2,0,1))
    # labelA = getLabel(batch_number)
    # labelB = getLabel(batch_number)
    # label_same = np.zeros(1, dtype=np.uint8)
    # label_same[0] = 1
    # label_same = torch.from_numpy(label_same)
    label_same = 1
    return netInputA,netInputB,label_same


def different_pair(trainID, sampleSeqLength, is_train=True):
    
    # trainID_random = random.shuffle(trainID)
    train_probe_num ,train_gallery_num = random.sample(range(150), 2)
    # print train_probe
    train_probe = trainID[train_probe_num]
    train_gallery = trainID[train_gallery_num]
    image_cam1 = os.listdir(osp.join(person_sequence,"cam1",str(train_probe)))
    optical_cam1 = os.listdir(osp.join(optical_sequence,"cam1",str(train_probe)))
    image_cam2 = os.listdir(osp.join(person_sequence,"cam2",str(train_gallery)))
    optical_cam2 = os.listdir(osp.join(optical_sequence,"cam2",str(train_gallery)))
    image_cam1.sort()
    image_cam2.sort()
    optical_cam1.sort()
    optical_cam2.sort()
    len_cam1 = len(image_cam1)
    len_cam2 = len(image_cam2)
    actualSampleSeqLen = sampleSeqLength
    startA = int(random.random()* ((len_cam1 - actualSampleSeqLen) + 1))    
    startB = int(random.random()* ((len_cam2 - actualSampleSeqLen) + 1)) 
    # print startA,startB
    netInputA = np.zeros((56, 40, 5, actualSampleSeqLen), dtype=np.float32)
    netInputB = np.zeros((56, 40, 5, actualSampleSeqLen), dtype=np.float32)
    # netInputA = np.zeros((56, 40, 3, actualSampleSeqLen), dtype=np.float32)
    # netInputB = np.zeros((56, 40, 3, actualSampleSeqLen), dtype=np.float32)
    # labelA = np.zeros(sampleSeqLength, dtype=np.uint8)
    # labelB = np.zeros(sampleSeqLength, dtype=np.uint8)

    for m in range(actualSampleSeqLen):
        img_file = os.path.join(person_sequence,"cam1",str(train_probe),image_cam1[startA+m])
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
        optical_file = os.path.join(optical_sequence,"cam1",str(train_probe),optical_cam1[startA+m])
        optical = cv2.imread(optical_file)/ 255.0
        optical = cv2.resize(optical,(40,56))
        m3  = np.mean(optical[:,:,1]) 
        m4  = np.mean(optical[:,:,2])
        v3  = np.sqrt(np.var(optical[:,:,1])) 
        v4  = np.sqrt(np.var(optical[:,:,2])) 
        netInputA[:, :, 3, m] = (optical[:,:,1]-m3)/np.sqrt(v3)
        netInputA[:, :, 4, m] = (optical[:,:,2]-m4)/np.sqrt(v4)
        # labelA[m] = train_probe_num

    for m in range(actualSampleSeqLen):
        img_file = os.path.join(person_sequence,"cam2",str(train_gallery),image_cam2[startB+m])
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
        optical_file = os.path.join(optical_sequence,"cam2",str(train_gallery),optical_cam2[startB+m])
        optical = cv2.imread(optical_file)/ 255.0
        optical = cv2.resize(optical,(40,56))
        m3  = np.mean(optical[:,:,1]) 
        m4  = np.mean(optical[:,:,2])
        v3  = np.sqrt(np.var(optical[:,:,1])) 
        v4  = np.sqrt(np.var(optical[:,:,2])) 
        netInputA[:, :, 3, m] = (optical[:,:,1]-m3)/np.sqrt(v3)
        netInputA[:, :, 4, m] = (optical[:,:,2]-m4)/np.sqrt(v4)
        # labelB[m] = train_gallery_num

    netInputA = np.transpose(netInputA, (3,2,0,1))
    netInputB = np.transpose(netInputB, (3,2,0,1))
    # labelA = torch.from_numpy(labelA)
    # labelB = torch.from_numpy(labelB)
    labelA = train_probe_num
    labelB = train_gallery_num


    # labelA = getLabel(train_probe)
    # labelB = getLabel(train_gallery)

    # label_same = np.zeros(1, dtype=np.uint8)
    # label_same[0] = -1
    # label_same = torch.from_numpy(label_same)
    label_same = -1
    return netInputA,netInputB,labelA,labelB,label_same

# def getLabel(batch_number):
#     #split person...
#     return int(batch_number.split('n')[1])


if __name__ == '__main__':
    
    IDs = os.listdir(osp.join(person_sequence,"cam1"))
    trainID = []
    testID  = []
    for i in range(300):
    # print IDs[i]
        if i%2 == 0:
            trainID.append(IDs[i])
        else:
            testID.append(IDs[i])
    # print trainID
    for batch_n in range(len(trainID)*2):
        if (batch_n%2 == 0): 
            # load data from same identity
            netInputA, netInputB = same_pair(trainID[batch_n/2],16) 
        else:
            # load data from different identity random
            netInputA, netInputB = different_pair(trainID,16)
    # netInputA,netInputB = different_pair(trainID,16)
    


