import datetime
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn import preprocessing
import warnings
warnings.filterwarnings("ignore")

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
for _d in (DATA_DIR, MODELS_DIR, OUTPUTS_DIR):
    os.makedirs(_d, exist_ok=True)

starttime = datetime.datetime.now()
data=pd.read_csv(os.path.join(DATA_DIR, 'all_parameters_valid.csv'))

import seaborn as sns
plt.figure(figsize=(8, 6))
sns.heatmap(data.corr(), annot=True, cmap='coolwarm')
plt.show()

print(data.head())
print('Data dimension:',data.shape)

amplification_factor=1
data_labels=(np.array(data[['bandgap']]))*amplification_factor
data_features=np.array(data[['fai','c1','c2']])

def normalize(array):
    mx = np.nanmax(array)
    mn = np.nanmin(array)
    t = (array-mn)/(mx-mn)
    return t


def json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f'Object of type {value.__class__.__name__} is not JSON serializable')

scaler=preprocessing.StandardScaler().fit(data_features)
data_features_normalize=scaler.transform(data_features)

data_labels_normalize=normalize(data_labels)

n_test=max(1, int(data_labels.shape[0] * 0.2))
index_test=np.random.choice(data_labels.shape[0],n_test,replace=False)
data_test_features=data_features_normalize[index_test]
data_test_labels=data_labels[index_test]

index_train=np.arange(data_labels.shape[0])
index_train=np.delete(index_train,index_test)
data_train_features=data_features_normalize[index_train]
data_train_labels=data_labels[index_train]

model=tf.keras.Sequential()

model.add(layers.Dense(16,activation='relu',bias_initializer='random_normal',
                       kernel_regularizer=tf.keras.regularizers.l2(0.03)))
model.add(layers.Dense(32,activation='relu',bias_initializer='random_normal',
                        kernel_regularizer=tf.keras.regularizers.l2(0.03)))
model.add(layers.Dense(64,activation='relu',bias_initializer='random_normal',
                        kernel_regularizer=tf.keras.regularizers.l2(0.03)))
model.add(layers.Dense(128,activation='relu',bias_initializer='random_normal',
                        kernel_regularizer=tf.keras.regularizers.l2(0.03)))
model.add(layers.Dense(256,activation='relu',bias_initializer='random_normal',
                        kernel_regularizer=tf.keras.regularizers.l2(0.03)))

model.add(layers.Dense(1,activation='linear',bias_initializer='random_normal',
                        kernel_regularizer=tf.keras.regularizers.l2(0.03)))

def custom_loss(y_actual,y_pred):
    custom_loss=((y_actual-y_pred)**2)*(y_actual)**0
    return custom_loss

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
              loss='MeanSquaredError',
              metrics=['mae'])

history = model.fit(data_train_features,data_train_labels,epochs=3000,batch_size=128)

endtime = datetime.datetime.now()
print('')
print("Total time spent: ")
print(endtime-starttime)

print('')
print('------Model summary------')
model.summary()
data_train_predict=model.predict(data_train_features)/amplification_factor
data_test_predict=model.predict(data_test_features)/amplification_factor
model.save(os.path.join(MODELS_DIR, 'NN_pc.h5'))

print('')
print('------Training set------')
print('')
print('Maximum value: ',np.max(data_labels)/amplification_factor)
print('Position: ',np.argmax(data_labels))
print('')
print('Minimum value: ',np.min(data_labels)/amplification_factor)
print('Position: ',np.argmin(data_labels))

print('')
print('------Predict value------')
print('')
print('Maximum value: ',np.max(data_train_predict))
print('Position: ',np.argmax(data_train_predict))
print('')
print('Minimum value: ',np.min(data_train_predict))
print('Position: ',np.argmin(data_train_predict))

SSR=sum((data_test_predict-data_test_labels/amplification_factor)**2)
SST=sum((np.mean(data_test_labels/amplification_factor)-data_test_labels/amplification_factor)**2)
R_2=1-SSR/SST
R_2_value = float(np.asarray(R_2).reshape(-1)[0])
print('')
print('------R^2------')
print(R_2_value)

summary_lines = []
model.summary(print_fn=summary_lines.append)
model_summary_text = '\n'.join(summary_lines)
corr = data.corr()

weights = model.get_weights()
weight_payload = {f'model_weight_{i}': weight for i, weight in enumerate(weights)}

npz_payload = {
    'elapsed_seconds': np.array([(endtime-starttime).total_seconds()]),
    'elapsed_str': np.array([str(endtime-starttime)]),
    'amplification_factor': np.array([amplification_factor]),
    'feature_names': np.array(['fai', 'c1', 'c2']),
    'index_train': index_train,
    'index_test': index_test,
    'data_train_labels': data_train_labels,
    'data_test_labels': data_test_labels,
    'data_train_predict': data_train_predict,
    'data_test_predict': data_test_predict,
    'R_2': np.array([R_2_value]),
    'corr_matrix': corr.to_numpy(),
    'corr_columns': np.array(corr.columns.tolist()),
    'history_loss': np.array(history.history.get('loss', [])),
    'history_mae': np.array(history.history.get('mae', [])),
    'model_json': np.array([model.to_json()]),
    'model_config_json': np.array([json.dumps(model.get_config(), default=json_default)]),
    'model_summary_text': np.array([model_summary_text]),
    'model_input_shape': np.array([json.dumps(list(model.input_shape))]),
    'model_output_shape': np.array([json.dumps(list(model.output_shape))]),
    'layer_names': np.array([layer.name for layer in model.layers]),
    'optimizer_class': np.array([model.optimizer.__class__.__name__]),
    'optimizer_config_json': np.array([json.dumps(model.optimizer.get_config(), default=json_default)]),
    'loss_name': np.array([str(model.loss)]),
    'metrics_names': np.array(model.metrics_names),
    'weight_names': np.array([weight.name for weight in model.weights]),
    'weight_shapes': np.array([json.dumps(list(weight.shape)) for weight in model.weights]),
    'scaler_mean': scaler.mean_,
    'scaler_scale': scaler.scale_,
    'ax_min': np.array([float(np.min(data_labels)/amplification_factor)]),
    'ax_max': np.array([float(np.max(data_labels)/amplification_factor)]),
}
npz_payload.update(weight_payload)
np.savez_compressed(os.path.join(OUTPUTS_DIR, 'nn_plot_data.npz'), **npz_payload)

plt.rcParams['xtick.direction']='in'
plt.rcParams['ytick.direction']='in'

fig=plt.figure(figsize=(4.2,4))

ax=fig.add_subplot(1,1,1)
ax_max=np.max(data_labels)/amplification_factor
ax_min=np.min(data_labels)/amplification_factor

x=np.array([ax_min,ax_max])
y1=x+(ax_max-ax_min)*0.1
y2=x-(ax_max-ax_min)*0.1
plt.fill_between(x,y1,y2,color='#3b6f7c',alpha=0.1)

ax.set_xlim(ax_min,ax_max)
ax.set_ylim(ax_min,ax_max)
ax.set_xlabel(r'$Bandgap$ by FEM',fontsize=14)
ax.set_ylabel(r'$Bandgap$ by NN',fontsize=14)

ax.plot(data_train_labels/amplification_factor,data_train_predict,'o',markersize='3',
        color='#8b5357',label='Training',alpha=1)
ax.plot(data_test_labels/amplification_factor,data_test_predict,'o',markersize='3',
        color='#123b57',label='Test',alpha=1)
ax.plot([ax_min,ax_max],[ax_min,ax_max],linewidth=0.5,ls='--',color='#8b5357',alpha=1)

plt.legend(loc='lower right',markerscale=2,frameon=False,handletextpad=0,borderaxespad=0,
           prop=font_manager.FontProperties(size=14))
fig.tight_layout() 
plt.savefig(os.path.join(OUTPUTS_DIR, 'NN_regression.png'), dpi=1000)
