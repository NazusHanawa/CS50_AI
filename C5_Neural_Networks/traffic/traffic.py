import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data from https://sid.erda.dk/public/archives/daaeac0d7ce1152aea9b61d9f1e19370/published-archive.html
# Archive file: "GTSRB-Training_fixed.zip"
DATA_DIR = f"{BASE_DIR}/GTSRB/Training"
SAVE_MODEL_PATH = f"{BASE_DIR}/trained_model.keras"
MAX_IMAGES_PER_CLASS = 0 # 0: No limit

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():
    # Check command-line arguments
    # if len(sys.argv) not in [2, 3]:
    #     sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    # images, labels = load_data(sys.argv[1])
    images, labels = load_data(DATA_DIR)

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    # if len(sys.argv) == 3:
    if SAVE_MODEL_PATH:
        # filename = sys.argv[2]
        filename = SAVE_MODEL_PATH
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    images, labels = [], []
    
    for directory_name in os.listdir(data_dir):
        directory_path = f"{data_dir}/{directory_name}"
        if not os.path.isdir(directory_path):
            continue
        
        print(directory_name, end="\r")
        
        class_id = int(directory_name)
        total_class_images = 0
        for file_name in os.listdir(directory_path):
            file_path = f"{directory_path}/{file_name}"
            if not file_name.lower().endswith('.ppm'):
                continue
            
            img = cv2.imread(file_path)
            img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))
            
            images.append(img)
            labels.append(class_id)
            
            total_class_images += 1
            if MAX_IMAGES_PER_CLASS and total_class_images >= MAX_IMAGES_PER_CLASS:
                break
                
    return (images, labels)


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    model = tf.keras.models.Sequential([
        # Define input format
        tf.keras.layers.Input(shape=(IMG_WIDTH, IMG_HEIGHT, 3)),
        tf.keras.layers.Rescaling(1/255),
        
        # Convolutional layer & Max-polling layer, using 2x2 pool size.
        tf.keras.layers.Conv2D(32, (3, 3), activation="relu"),
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
        
        # Convolutional layer & Max-polling layer, using 2x2 pool size.
        tf.keras.layers.Conv2D(64, (3, 3), activation="relu"),
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
        
        # Flatten units.
        tf.keras.layers.Flatten(),
        
        # Add a hiden layer with dropout.
        tf.keras.layers.Dense(256, activation="tanh"),
        tf.keras.layers.Dropout(0.5),
        
        # Add a hiden layer with dropout.
        tf.keras.layers.Dense(128, activation="tanh"),
        tf.keras.layers.Dropout(0.5),
        
        # Add an output layer with output for all categories.
        tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax")
    ])
    
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    
    return model


if __name__ == "__main__":
    main()
    ...
