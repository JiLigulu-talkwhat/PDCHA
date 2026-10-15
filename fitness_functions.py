import os
import time
import socket
import struct
import numpy as np
from petal_generator import calculate_required_r0, generate_petal_curve

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
TEMP_CURVE_DIR = os.path.join(BASE_DIR, "outputs", "temp")

L_GEOMETRY = 0.05
NUM_POINTS_FOR_CURVE = 100


class FitnessFunctions:

    def __init__(self, scaler, model, udp_sock, temp_curve_dir):
        self.scaler = scaler
        self.model = model
        self.udp_sock = udp_sock
        self.temp_curve_dir = temp_curve_dir
        self.log = None
        self.log_message = None
        self.bounds = [(0.1, 0.35), (-0.35, 0.35), (-0.35, 0.35)]

    def close(self):
        self.udp_sock.close()

    def func_a(self, x):
        x_norm = self.scaler.transform(np.array([x]))
        x_norm = x_norm.reshape(1, 3)
        y = self.model(x_norm, training=False).numpy()
        return -float(y[0][0])

    def func_b(self, x):
        target_phi, c1, c2 = x
        n1, n2 = (4, 8)
        try:
            r0, actual_phi, is_valid = calculate_required_r0(
                L=L_GEOMETRY, target_phi=target_phi, c1=c1, c2=c2, n1=n1, n2=n2
            )
            if not is_valid:
                self.log_message("invalid_geometry")
                return float("inf")
            x_coords, y_coords = generate_petal_curve(
                L=L_GEOMETRY, r0=r0, c1=c1, c2=c2, n1=n1, n2=n2, num_points=NUM_POINTS_FOR_CURVE
            )
        except Exception as e:
            self.log_message("geometry_generation_failed", e)
            return float("inf")
        unique_id = f"{time.time_ns()}_{os.getpid()}"
        temp_txt_filename = f"curve_{unique_id}.txt"
        temp_txt_filepath = os.path.join(self.temp_curve_dir, temp_txt_filename)
        try:
            with open(temp_txt_filepath, "w") as f:
                for xi, yi in zip(x_coords, y_coords):
                    f.write(f"{xi:.8f} {yi:.8f}\n")
                f.flush()
                os.fsync(f.fileno())
        except IOError as e:
            self.log_message("geometry_write_failed", e)
            return float("inf")
        send_data = os.path.abspath(temp_txt_filepath)
        self.udp_sock.sendto(send_data.encode("utf-8"), ("127.0.0.1", 3031))
        self.udp_sock.settimeout(300)
        try:
            recv = self.udp_sock.recvfrom(256)
            comsol_result = struct.unpack("d", recv[0])[0]
            try:
                os.remove(temp_txt_filepath)
            except OSError as e:
                self.log_message("geometry_cleanup_failed", temp_txt_filepath, e)
            return -comsol_result
        except socket.timeout:
            self.log_message("physics_timeout")
            return float("inf")


def create_fitness():
    import pandas as pd
    import tensorflow as tf
    from sklearn import preprocessing

    if not os.path.exists(TEMP_CURVE_DIR):
        os.makedirs(TEMP_CURVE_DIR)
    np.set_printoptions(precision=2, suppress=True)
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('', 3030))
    data = pd.read_csv(os.path.join(DATA_DIR, 'all_parameters_valid.csv'))
    data_features = np.array(data[['fai', 'c1', 'c2']])
    scaler = preprocessing.StandardScaler().fit(data_features)
    model = tf.keras.models.load_model(os.path.join(MODELS_DIR, 'NN_pc.h5'))
    return FitnessFunctions(scaler, model, udp_sock, TEMP_CURVE_DIR)
