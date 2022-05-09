from itertools import tee
#from matplotlib import pyplot as plt
import matplotlib.pyplot as plt
#import ROOT
import matplotlib as mpl
import pandas as pd
import numpy as np
#libraries for data analysis
from pprint import pprint
from collections import namedtuple
import datetime
from scipy.optimize import curve_fit
from scipy.stats import chisquare
from sklearn.metrics import mean_squared_error
#Libraries for machine learning
from tensorflow.keras.layers import Input, Dense, Dropout, Flatten, LeakyReLU, Add, Concatenate, Dot
from tensorflow.keras.models import Model
from tensorflow.keras.layers import LSTM
from tensorflow.keras.utils  import plot_model
from tensorflow.keras.layers import Layer
from tensorflow.keras import layers
from tensorflow.keras import regularizers
import seaborn as sns
#data_folder = ('/home/federico/root/root-6.24.06-install')
#data_folder = ('/gwpool/users/fdematteis')


metadata = pd.read_csv("fill_metadata_2017_10min.csv")

#----------------------------------------------------------
#transparency data for a selected iRing#
data24=np.load("iRing24new.npy")
data24_df = pd.DataFrame(data24)
data24_df.head()
mean24=[]


#compute mean transparnecy in iRings 
for i in range (0, len(data24_df.axes[1])):
    #mean of colums' entries of data_df (for each "position" in the cristal)
    mean24 = np.append(mean24, np.mean(data24_df[i]))
mean24=mean24[mean24 != -1]
metadata = metadata.iloc[:len(mean24)][mean24 != -1]

#selectin metadata for fill (locking metadata to in_fill=1)
fill=metadata["fill_num"].unique()
fill = fill[fill != 0]
nonsmooth = [5830, 5837, 5839, 5840, 5882, 5954, 5984, #6024, 
             6030, 6041,
             6057, 6084, 6089, 6090, 6091,  6096, 6105, 
             6152, 6159, 6160, 6167, 6168, 6170,  
             #6253, 6255, 
             6189, 6192, 6193,
             6263, 6318,
             6279, # non-smooth fills : 26/138
             6349
             ]
#print(len(nonsmooth))

for iev in range (0, len(nonsmooth)) :
    #print(nonsmooth[iev])
    fill = fill[fill != nonsmooth[iev]]


#test fill
#escludo fill di test
fill=fill[fill != 6371]
metadata_fill = metadata[metadata.fill_num.isin(fill)]
metadata_fill = metadata_fill[(metadata_fill.lumi_inst >= 0.0001*1e9) & (metadata_fill.lumi_inst <= 0.0004*1e9) & (metadata_fill.lumi_in_fill >= 0.1*1e9)]
fill_num = metadata_fill.fill_num.unique()
#devo togliere i fill non smooth dal dataset
print("fills esclusi dal train")
print(fill_num)

transp_fill = []
lumi_inst_0 = []
lumi_int_0 = []
#riempie il vettore di transparency
for k in fill_num:
    #in metadata fill ci sono solo i dati relativi a ifferenti fills, 
    # quindi ha la stessa dimensione della transp_fill

    #restringe metadata a quello di un solo fill (k)
    #viene fatto per ogni fill
    df = metadata_fill[metadata_fill.fill_num == k]
    transp = [mean24[i] for i in df.index.values]
    #transp ha la grandezza del dataframe ristretto al k esimo fill
    transp = transp/transp[0]
    transp_fill = np.append(transp_fill, transp)
    a = np.empty(np.size(transp))
    b = np.empty(np.size(transp))
    a.fill(df['lumi_inst'].iloc[0])
    b.fill(df['lumi_int'].iloc[0])
    lumi_inst_0 = np.append(lumi_inst_0, a)
    lumi_int_0 = np.append(lumi_int_0, b)
    #in transp_fill ci sono i dati di trasparenza normalizzata per ogni fill;
#a transp_fill corrispondono i dati matadata_fill
#me build the same:

#gets easyer data manipulation
#put metadata into arrays
instLumi = (1e-9)*metadata_fill.loc[:,'lumi_inst']
intLumiLHC = (1e-9)*metadata_fill.loc[:,'lumi_int']
infillLumi = (1e-9)*metadata_fill.loc[:,'lumi_in_fill']
lastfillLumi = (1e-9)*metadata_fill.loc[:,'lumi_last_fill']
filltime = (1e-9)*metadata_fill.loc[:,'time_in_fill']
lastpointLumi = (1e-9)*metadata_fill.loc[:, 'lumi_since_last_point']
true_time = (1e-9)*metadata_fill.loc[:, 'time']

all_inputs_train=np.stack((instLumi, infillLumi, intLumiLHC, lastfillLumi, filltime), axis=-1)
#validation dataset
filltest = 6371
metadata_6371 = metadata[metadata.fill_num == filltest]
metadata_6371 = metadata_6371[(metadata_6371.lumi_inst >= 0.0001*1e9) & (metadata_6371.lumi_inst <= 0.0004*1e9) & (metadata_6371.lumi_in_fill >= 0.1*1e9)]
transp_6371 = mean24[metadata_6371.index.values[0]:metadata_6371.index.values[0]+len(metadata_6371.axes[0])]
# normalizzo il dato di trasparenza a quella precedente al fill
transp_6371 = transp_6371/transp_6371[0]

instLumi_test = (1e-9)*metadata_6371.loc[:,'lumi_inst']
intLumiLHC_test = (1e-9)*metadata_6371.loc[:,'lumi_int']
infillLumi_test = (1e-9)*metadata_6371.loc[:,'lumi_in_fill']
lastfillLumi_test = (1e-9)*metadata_6371.loc[:,'lumi_last_fill']
filltime_test = (1e-9)*metadata_6371.loc[:,'time_in_fill']
lastpointLumi_test = (1e-9)*metadata_6371.loc[:, 'lumi_since_last_point']
true_time_test = (1e-9)*metadata_6371.loc[:, 'time']


all_inputs_test=np.stack((instLumi_test, infillLumi_test, intLumiLHC_test, lastfillLumi_test, filltime_test), axis=-1)

# Machine learning  
#DNN structure
inputs = Input(shape=(5,))

hidden1 = Dense(500, activation='leaky_relu')(inputs)#, kernel_regularizer=regularizers.l1_l2(l1=1e-10, l2=1e-10), bias_regularizer=regularizers.l2(1e-10), activity_regularizer=regularizers.l2(1e-10))(inputs)

drop1=Dropout(0.3)(hidden1)

hidden2 = Dense(300, activation='leaky_relu')(drop1)#, kernel_regularizer=regularizers.l1_l2(l1=1e-10, l2=1e-10), bias_regularizer=regularizers.l2(1e-10), activity_regularizer=regularizers.l2(1e-10))(drop1)

drop2=Dropout(0.2)(hidden2)

hidden3 = Dense(150, activation='leaky_relu')(drop2)#, kernel_regularizer=regularizers.l1_l2(l1=1e-10, l2=1e-10), bias_regularizer=regularizers.l2(1e-10), activity_regularizer=regularizers.l2(1e-10))(drop2)

#drop3=Dropout(0.2)(hidden3)
hidden4 = Dense(50, activation='leaky_relu')(hidden3)#, kernel_regularizer=regularizers.l1_l2(l1=1e-10, l2=1e-10), bias_regularizer=regularizers.l2(1e-10), activity_regularizer=regularizers.l2(1e-10))(drop2)
#drop3=Dropout(0.2)(hidden3)

outputs = Dense(1) (hidden4)#kernel_regularizer=regularizers.l1_l2(l1=1e-16, l2=1e-16), bias_regularizer=regularizers.l2(1e-16), activity_regularizer=regularizers.l2(1e-16))(hidden3)

#compile
model = Model ( inputs=inputs, outputs=outputs )
model.compile(loss='MSE', optimizer='adam')

#write the summary of the network
model.summary()

#plot the network
plot_model(
    model,
    to_file="model.png",
    show_shapes=True,
    show_layer_names=True,
    rankdir="TB",
)

all_inputs_training   = all_inputs_train
all_inputs_validation = all_inputs_test
transp_training   = transp_fill
transp_validation = transp_6371

#print(all_inputs_validation)

#now actually performing the train 
history = model.fit( all_inputs_training, transp_training, validation_data = (all_inputs_validation,transp_validation), epochs=50, verbose=0)

#plot the training loss
plt.plot( history.history["val_loss"] )
plt.plot( history.history["loss"] )
plt.show() 

# summarize history for accuracy
# plt.plot(history.history["accuracy"], label = 'train')
# plt.plot(history.history["val_accuracy"], label='test')
# plt.legend()
# plt.show()

#now test the performance of the DNN
transp_predicted_validation = model.predict(all_inputs_validation)
#plot on abs time of metadata for a selected fill_num
plt.plot(metadata_6371.time, transp_validation, ".b-", markersize=3, linewidth=0.75, label="measured")
plt.plot(metadata_6371.time, transp_predicted_validation, ".r-", markersize=3, linewidth=0.75, label="predicted")
plt.xlabel("time")
plt.ylabel("mean transparency")
plt.tick_params(labelsize=7)
plt.title("predicted & observed - fill")
plt.show()
print("lunghezza della t ")
print(len(transp_predicted_validation))


error = 0
#calcolo il mse
for i in range (0, len(transp_validation)):
    error = error + (transp_validation[i]-transp_predicted_validation[i])*(transp_validation[i]-transp_predicted_validation[i])

#mean square error: 1/N sum((O-P)^2)
mse = error/len(transp_validation)
print("mean square error for fill ")
print(mse)
