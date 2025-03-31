import time
import tensorflow as tf
from tensorflow.keras.datasets import cifar10

def create_cnn_model(input_shape):
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(10, activation='softmax')
    ])
    return model

def compile_and_train_model(model, train_images, train_labels, epochs=10):
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    model.fit(train_images, train_labels, epochs=epochs)

def evaluate_model(model, test_images, test_labels):
    test_loss, test_acc = model.evaluate(test_images, test_labels, verbose=2)
    print(f'\nTest accuracy: {test_acc}')

def load_and_preprocess_data():
    (train_images, train_labels), (test_images, test_labels) = cifar10.load_data()
    train_images = train_images.astype('float32') / 255.0
    test_images = test_images.astype('float32') / 255.0
    return train_images, train_labels, test_images, test_labels

# Measure CNN execution time
start_time = time.time()

# Load data
train_images, train_labels, test_images, test_labels = load_and_preprocess_data()

# Create model
model = create_cnn_model((32, 32, 3))

# Compile and train model
compile_and_train_model(model, train_images, train_labels, epochs=10)  # Adjust epochs as needed

# Evaluate model
evaluate_model(model, test_images, test_labels)

# Print execution time
cnn_execution_time = time.time() - start_time
print(f"Total execution time for CNN code: {cnn_execution_time:.2f} seconds")