import concurrent.futures
import pandas as pd
import tensorflow as tf
import time

# Initialize TPU if needed
def init_tpu():
    try:
        resolver = tf.distribute.cluster_resolver.TPUClusterResolver()  # Detect TPU
        tf.config.experimental_connect_to_cluster(resolver)
        tf.tpu.experimental.initialize_tpu_system(resolver)
        print("TPU initialized.")
        return True
    except Exception as e:
        print(f"TPU initialization failed: {e}")
        return False

# Load keywords and resource needs from Excel file
def load_keywords_from_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.strip()  # Strip whitespace from column names
        keywords = [(row['Keyword'], int(row['CPU']), int(row['GPU']), int(row['TPU'])) for _, row in df.iterrows()]
        print(f"Loaded keywords: {keywords}")
        return keywords
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Define CNN model
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

# Compile and train CNN model
def compile_and_train_model(model, train_images, train_labels, epochs=10):
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    model.fit(train_images, train_labels, epochs=epochs)

# Evaluate CNN model
def evaluate_model(model, test_images, test_labels):
    test_loss, test_acc = model.evaluate(test_images, test_labels, verbose=2)
    print(f'\nTest accuracy: {test_acc}')
    return test_acc

# Load and preprocess CIFAR-10 dataset
def load_and_preprocess_data():
    (train_images, train_labels), (test_images, test_labels) = tf.keras.datasets.cifar10.load_data()
    train_images = train_images.astype('float32') / 255.0
    test_images = test_images.astype('float32') / 255.0
    return train_images, train_labels, test_images, test_labels

# Execute a CNN snippet on the specified device and measure execution time
def run_snippet(snippet, device):
    print(f"Executing snippet on {device}")  # Print device info
    start_time = time.time()
    accuracy = None

    with tf.device(device):
        if snippet["action"] == "create_model":
            return create_cnn_model((32, 32, 3))
        elif snippet["action"] == "train_model":
            compile_and_train_model(snippet["model"], snippet["train_images"], snippet["train_labels"])
        elif snippet["action"] == "evaluate_model":
            accuracy = evaluate_model(snippet["model"], snippet["test_images"], snippet["test_labels"])

    execution_time = time.time() - start_time
    return f"Execution completed in {execution_time:.2f} seconds on {device}. Accuracy: {accuracy}" if accuracy else f"Execution completed in {execution_time:.2f} seconds on {device}."

# Decide the device based on resource availability
def get_device(cpu, gpu, tpu):
    if tpu and tf.config.list_logical_devices('TPU'):
        return '/device:TPU:0'
    elif gpu and tf.config.list_physical_devices('GPU'):
        return '/device:GPU:0'
    else:
        return '/device:CPU:0'

# Main master function for scheduling tasks
def master(file_path):
    start_time = time.time()
    keywords = load_keywords_from_excel(file_path)
    if keywords is None:
        print("Failed to load keywords.")
        return

    # Load and preprocess data for training and evaluation
    train_images, train_labels, test_images, test_labels = load_and_preprocess_data()

    # Define CNN snippets with actions
    cnn_snippets = [
        {"action": "create_model"},
        {"action": "train_model", "model": create_cnn_model((32, 32, 3)), "train_images": train_images, "train_labels": train_labels},
        {"action": "evaluate_model", "model": create_cnn_model((32, 32, 3)), "test_images": test_images, "test_labels": test_labels}
    ]

    tpu_required = any(resource[-1] for resource in keywords)
    if tpu_required:
        tpu_available = init_tpu()
        if not tpu_available:
            print("TPU is required but unavailable. Proceeding with fallback to GPU or CPU.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {}
        for snippet in cnn_snippets:
            resources = (1, 1, 1)  # Example CPU, GPU, TPU allocations
            device = get_device(*resources)
            futures[executor.submit(run_snippet, snippet, device)] = snippet

        for future in concurrent.futures.as_completed(futures):
            snippet = futures[future]
            try:
                result = future.result()
                print(f"Snippet action {snippet['action']} -> {result}")
            except Exception as e:
                print(f"Error executing snippet: {e}")

    total_execution_time = time.time() - start_time
    print(f"Total execution time for code: {total_execution_time:.2f} seconds")

# Main execution
if __name__ == '__main__':
    excel_file_path = 'resource_allocation_dataset.xlsx'  # Update with the correct path
    master(excel_file_path)