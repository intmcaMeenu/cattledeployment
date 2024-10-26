import os
import cv2
import numpy as np
import tensorflow as tf
from keras.preprocessing.image import img_to_array

# Load the pre-trained model
model = tf.keras.models.load_model('cattle_app/mobilenet_v2.h5')  # Update this path
labels = ["Breed1", "Breed2", "Breed3"]  # Update with actual breed names

# Path to the dataset folder
dataset_folder = 'CowBreeds_DataSet'  # Update with your folder path

def classify_breeds():
    # Loop through images in the dataset folder
    for filename in os.listdir(dataset_folder):
        if filename.endswith(('.png', '.jpg', '.jpeg')):  # Check for image files
            image_path = os.path.join(dataset_folder, filename)
            
            # Load and preprocess the image
            image = cv2.imread(image_path)
            image = cv2.resize(image, (224, 224))
            image = img_to_array(image)
            image = np.expand_dims(image, axis=0) / 255.0
            
            # Make predictions
            preds = model.predict(image)
            breed_index = np.argmax(preds)
            breed_name = labels[breed_index]
            
            print(f'Image: {filename} - Predicted Breed: {breed_name}')

if __name__ == "__main__":
    classify_breeds()
