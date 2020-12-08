# prerequist:
'''! git clone https://github.com/sauravhbp/track
! cd track
! pip install imgaug
'''



# IMPORTING REQUIRED LIBRARIES

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import keras
from keras.models import Sequential
from keras.optimizers import Adam
from keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from imgaug import augmenters as iaa
import cv2
import pandas as pd
import ntpath
import random

# IMPORT DATASET 

datadir = 'track'
columns = ['center', 'left', 'right', 'steering', 'throttle', 'reverse', 'speed']
data = pd.read_csv(os.path.join(datadir, 'driving_log.csv'), names = columns)
pd.set_option('display.max_colwidth', -1)
data.head()

# REMOVING WHOLE PATH LOCATION FROM THE DATASET LEFT RIGHT AND CENTER COLUMN

def path_leaf(path):
  head, tail = ntpath.split(path)
  return tail
data['center'] = data['center'].apply(path_leaf)
data['left'] = data['left'].apply(path_leaf)
data['right'] = data['right'].apply(path_leaf)
data.head()

# MAKING A HISTOGRAM TO SHOW THE DATASET , THE STEERING ANGLE AT A POSTION 

num_bins = 25
samples_per_bin = 400
hist, bins = np.histogram(data['steering'], num_bins)
center = (bins[:-1]+ bins[1:]) * 0.5
plt.bar(center, hist, width=0.05)
plt.plot((np.min(data['steering']), np.max(data['steering'])), (samples_per_bin, samples_per_bin))
print('total data:', len(data))

# REMOVING BIASNESS OF DATA AS THE MAJOR MEDIAN STEERING ANGLE AS IT IS 0 FOR MOST OF TIME IS CAR GOES STRAIGHT 

remove_list = []
for j in range(num_bins):
  list_ = []
  for i in range(len(data['steering'])):
    if data['steering'][i] >= bins[j] and data['steering'][i] <= bins[j+1]:
      list_.append(i)
  list_ = shuffle(list_)
  list_ = list_[samples_per_bin:]
  remove_list.extend(list_)
 
print('removed:', len(remove_list))
data.drop(data.index[remove_list], inplace=True)
print('remaining:', len(data))

# STANDARIZED STEERING ANGLE HISTOGRAM

hist, _ = np.histogram(data['steering'], (num_bins))
plt.bar(center, hist, width=0.05)
plt.plot((np.min(data['steering']), np.max(data['steering'])), (samples_per_bin, samples_per_bin))

# SPLITTING TEST TRAIN SPLIT WITH LINKING CSV FILE WITH ACTUAL IMAGE FILE

print(data.iloc[1])
def load_img_steering(datadir, df):
  image_path = []
  steering = []
  for i in range(len(data)):
    indexed_data = data.iloc[i]
    center, left, right = indexed_data[0], indexed_data[1], indexed_data[2]
    # center image
    image_path.append(os.path.join(datadir, center.strip()))
    steering.append(float(indexed_data[3]))
    # left image
    image_path.append(os.path.join(datadir,left.strip()))
    steering.append(float(indexed_data[3])+0.15)
    # right image
    image_path.append(os.path.join(datadir,right.strip()))
    steering.append(float(indexed_data[3])-0.15)
  image_paths = np.asarray(image_path)
  steerings = np.asarray(steering)
  return image_paths, steerings

image_paths, steerings = load_img_steering(datadir + '/IMG', data)
X_train, X_valid, y_train, y_valid = train_test_split(image_paths, steerings, test_size=0.2, random_state=6)
print('Training Samples: {}\nValid Samples: {}'.format(len(X_train), len(X_valid)))

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].hist(y_train, bins=num_bins, width=0.05, color='blue')
axes[0].set_title('Training set')
axes[1].hist(y_valid, bins=num_bins, width=0.05, color='red')
axes[1].set_title('Validation set')


# IMAGE AUGMENTATION IE RESCALING AND REMOVING IMAGE NOISE 

#	zoomed image as corners are noise and visualise with subplot

def zoom(image):
  zoom = iaa.Affine(scale=(1, 1.3))							# range of zoomed in upto 30 , it select random between no zoom to 30% in zoom  
  image = zoom.augment_image(image)
  return image
# visualize zoomed 
'''
image = image_paths[random.randint(0, 1000)]
original_image = mpimg.imread(image)
zoomed_image = zoom(original_image)
fig, axs = plt.subplots(1, 2, figsize=(15, 10))
fig.tight_layout()
axs[0].imshow(original_image)
axs[0].set_title('Original Image')
axs[1].imshow(zoomed_image)
axs[1].set_title('Zoomed Image')
'''	

def pan(image):
  pan = iaa.Affine(translate_percent= {"x" : (-0.1, 0.1), "y": (-0.1, 0.1)}) 	# move image from -10% to +10% on x axis as well as y-axis
  image = pan.augment_image(image)
  return image
# visualize panned
'''
image = image_paths[random.randint(0, 1000)]
original_image = mpimg.imread(image)
panned_image = pan(original_image)

fig, axs = plt.subplots(1, 2, figsize=(15, 10))
fig.tight_layout()

axs[0].imshow(original_image)
axs[0].set_title('Original Image')

axs[1].imshow(panned_image)
axs[1].set_title('Panned Image')
'''

def img_random_brightness(image):
    brightness = iaa.Multiply((0.2, 1.2))						# brightness of image
    image = brightness.augment_image(image)
    return image
# visualize brightness
'''
image = image_paths[random.randint(0, 1000)]
original_image = mpimg.imread(image)
brightness_altered_image = img_random_brightness(original_image)

fig, axs = plt.subplots(1, 2, figsize=(15, 10))
fig.tight_layout()

axs[0].imshow(original_image)
axs[0].set_title('Original Image')

axs[1].imshow(brightness_altered_image)
axs[1].set_title('Brightness altered image ')
'''

def img_random_flip(image, steering_angle):
    image = cv2.flip(image,1)								# image flip wrt x axis
    steering_angle = -steering_angle
    return image, steering_angle
# flipped image 
'''
random_index = random.randint(0, 1000)
image = image_paths[random_index]
steering_angle = steerings[random_index]


original_image = mpimg.imread(image)
flipped_image, flipped_steering_angle = img_random_flip(original_image, steering_angle)

fig, axs = plt.subplots(1, 2, figsize=(15, 10))
fig.tight_layout()

axs[0].imshow(original_image)
axs[0].set_title('Original Image - ' + 'Steering Angle:' + str(steering_angle))

axs[1].imshow(flipped_image)
axs[1].set_title('Flipped Image - ' + 'Steering Angle:' + str(flipped_steering_angle))
'''

def random_augment(image, steering_angle):						# randomly applying image augmentation with 50 % probability
    image = mpimg.imread(image)
    if np.random.rand() < 0.5:
      image = pan(image)
    if np.random.rand() < 0.5:
      image = zoom(image)
    if np.random.rand() < 0.5:
      image = img_random_brightness(image)
    if np.random.rand() < 0.5:
      image, steering_angle = img_random_flip(image, steering_angle)
    
    return image, steering_angle

# 2 row 10 column of pic data to show the difference

ncol = 2
nrow = 10

fig, axs = plt.subplots(nrow, ncol, figsize=(15, 50))
fig.tight_layout()
for i in range(10):
  randnum = random.randint(0, len(image_paths) - 1)
  random_image = image_paths[randnum]
  random_steering = steerings[randnum]
  original_image = mpimg.imread(random_image)
  augmented_image, steering = random_augment(random_image, random_steering)
  axs[i][0].imshow(original_image)
  axs[i][0].set_title("Original Image")
  axs[i][1].imshow(augmented_image)
  axs[i][1].set_title("Augmented Image")
  

# IMGAE PREPROCEESING

def img_preprocess(img):
    img = img[60:135,:,:]                         # rescaling 
    img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)	# conversion from colored image yellow uv image
    img = cv2.GaussianBlur(img,  (3, 3), 0)		# blurring the image to distinguise noise
    img = cv2.resize(img, (200, 66))			# resizing to input process is mathing pixel
    img = img/255					# normalization
    return img

# show the preprocessed and orignal image side by side
'''
image = image_paths[100]
original_image = mpimg.imread(image)
preprocessed_image = img_preprocess(original_image)
fig, axs = plt.subplots(1, 2, figsize=(15, 10))
fig.tight_layout()
axs[0].imshow(original_image)
axs[0].set_title('Original Image')
axs[1].imshow(preprocessed_image)
axs[1].set_title('Preprocessed Image')
'''

# OPERATING ON BATCH RAHTER THAN ONE IMAGE ITSELF IN ORDER TO IMPROVE THE MODEL

def batch_generator(image_paths, steering_ang, batch_size, istraining):
  
  while True:
    batch_img = []
    batch_steering = []
    
    for i in range(batch_size):
      random_index = random.randint(0, len(image_paths) - 1)
      
      if istraining:
        im, steering = random_augment(image_paths[random_index], steering_ang[random_index])
     
      else:
        im = mpimg.imread(image_paths[random_index])
        steering = steering_ang[random_index]
      
      im = img_preprocess(im)
      batch_img.append(im)
      batch_steering.append(steering)
    yield (np.asarray(batch_img), np.asarray(batch_steering)) 	# 	concept of generator: yeild 
# applying on x_train,x_val  
x_train_gen, y_train_gen = next(batch_generator(X_train, y_train, 1, 1))	# next : concept of generator
x_valid_gen, y_valid_gen = next(batch_generator(X_valid, y_valid, 1, 0))

# visualization of batch
'''
fig, axs = plt.subplots(1, 2, figsize=(15, 10))
fig.tight_layout()

axs[0].imshow(x_train_gen[0])
axs[0].set_title('Training Image')

axs[1].imshow(x_valid_gen[0])
axs[1].set_title('Validation Image')
'''

# MODEL OF CONVOLUTION NEURAL NETWORK 
# 4 step convolutions , flattening , dropout and full connections 	

def ourModel():
  model = Sequential()											# intializing the model
  model.add(Conv2D(24, kernel_size=(5,5), strides=(2,2), input_shape=(66,200,3),activation='elu'))	#  no of filter 24 , 2d conv window =[5,5],strides with 2*2 on 														   edge, input shape = image shape , activation elu : relu with 														   returing -ve value rather than 0 for -ve  
    
  model.add(Conv2D(36, kernel_size=(5,5), strides=(2,2), activation='elu'))	
  model.add(Conv2D(48, kernel_size=(5,5), strides=(2,2), activation='elu'))
  model.add(Conv2D(64, kernel_size=(3,3), activation='elu'))
  model.add(Conv2D(64, kernel_size=(3,3), activation='elu'))
  model.add(Dropout(0.5))										# drop few node or set random nodes to zero to avoid overfitting
  
  
  model.add(Flatten())											# flatting the 2d array to 1d array to process as input
  
  model.add(Dense(100, activation = 'elu'))								# adding 1st hidden layer with 100 nodes
  model.add(Dropout(0.5))										# dropping half of hidden node to impove model and remove 
  
  model.add(Dense(50, activation = 'elu'))								# add 2nd hidden layer with 50 nodes
  model.add(Dropout(0.5))
  
  model.add(Dense(10, activation = 'elu'))								# 3rd hidden layer 
  model.add(Dropout(0.5))

  model.add(Dense(1))											# o/p layer
  
  optimizer = Adam(lr=1e-3)										# adam optimizer with learning rate (10**-3)
  model.compile(loss='mse', optimizer=optimizer)							# loss mean squared error
  return model

model = ourModel()											# calling model
print(model.summary())											# print summary of the model 
# fitting the model in training set and validation set and store in variable history
history = model.fit_generator(batch_generator(X_train, y_train, 100, 1),
                                  steps_per_epoch=300, 
                                  epochs=10,
                                  validation_data=batch_generator(X_valid, y_valid, 100, 0),
                                  validation_steps=200,
                                  verbose=1,
                                  shuffle = 1)
                                  

#  VISUALIZATION 


plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.legend(['training', 'validation'])
plt.title('Loss')
plt.xlabel('Epoch')

# SAVING THE MODEL USING KERAS AND DOWNLOADING IN HDF5 FORMAT AS WE ARE ON GOOGLE COLAB
model.save('my_model.h5')
model.save('model.h5')
from google.colab import files
files.download('model.h5')										# can use pickle
