import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

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
    if len(sys.argv) == 3:
        filename = sys.argv[2]
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
    images = []
    labels = []
    # list of directories in /gtsrb
    categories = os.listdir(data_dir)
    # loop through each category (number)
    for category in categories:
        # list of directories in /gtsrb/<# of category>
        category_dir = os.path.join(data_dir, category)
        # list of images in /gtsrb/<# of category>
        category_images = os.listdir(category_dir)
        # loop through each image in a category
        for image_dir in category_images:
            # image with path /gtsrb/<category #>/<image_file_name>
            image_path = os.path.join(category_dir, image_dir)
            image = cv2.imread(image_path)
            res = cv2.resize(image, dsize=(IMG_WIDTH, IMG_HEIGHT))
            images.append(res)
            labels.append(category)

    return (images, labels)


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    model = tf.keras.models.Sequential([

        # convolution layer
        tf.keras.layers.Conv2D(
            96, (5, 5), activation='relu', input_shape=(30, 30, 3)
        ),

        # pooling layer
        tf.keras.layers.MaxPooling2D(
            pool_size=(2, 2)
        ),

        # flatten so that we can convert from 2D to 1D to feed into dense layers
        tf.keras.layers.Flatten(),

        # fully connected layers
        tf.keras.layers.Dense(512, activation='relu'),

        # dropout
        tf.keras.layers.Dropout(0.3),
        # output layer
        tf.keras.layers.Dense(NUM_CATEGORIES, activation='softmax')
    ])

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


if __name__ == "__main__":
    main()
