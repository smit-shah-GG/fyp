import concurrent.futures
import pandas as pd
import tensorflow as tf

# Load keywords from Excel
def load_keywords_from_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        print("Columns in the Excel file:", df.columns.tolist())  # Print the columns to check
        df.columns = df.columns.str.strip()  # Strip whitespace from column names

        # Create a list to hold keywords and their corresponding resource allocations
        keywords = []
        for _, row in df.iterrows():
            # Extract keyword and resources, assuming they are in the right format
            resource = (int(row['CPU']), int(row['GPU']), int(row['TPU']))
            keywords.append((row['Keyword'], *resource))  # Add keyword and resource tuple to the list
        
        return keywords  # Return the list of keywords
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Return None in case of an error



# Load CNN snippets to be executed
cnn_snippets = [
    """import tensorflow as tf
from tensorflow.keras import layers, models

def create_cnn_model(input_shape):
    model = models.Sequential()
    model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.Flatten())
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(10, activation='softmax'))
    return model""",
    
    """def compile_and_train_model(model, train_images, train_labels, epochs=10):
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        model.fit(train_images, train_labels, epochs=epochs)""",
    
    """def evaluate_model(model, test_images, test_labels):
        test_loss, test_acc = model.evaluate(test_images, test_labels, verbose=2)
        print(f'\\nTest accuracy: {test_acc}')""",
    
    """def load_and_preprocess_data():
        (train_images, train_labels), (test_images, test_labels) = tf.keras.datasets.cifar10.load_data()
        train_images = train_images.astype('float32') / 255.0
        test_images = test_images.astype('float32') / 255.0
        return train_images, train_labels, test_images, test_labels"""
]

# Default resource allocation
default_resource = (1, 0, 0)  # CPU, GPU, TPU

def label_and_allocate(snippet, keywords):
    """Label the code snippet and allocate resources based on keywords."""
    resources = []
    for keyword, cpu, gpu, tpu in keywords:
        if keyword in snippet:
            resource = {
                'keyword': keyword,
                'CPU': bool(cpu),
                'GPU': bool(gpu),
                'TPU': bool(tpu)
            }
            resources.append(resource)
    return resources

# Function to run each CNN snippet
def run_snippet(snippet):
    print(f"Executing snippet: {snippet[:30]}...")  # Print a preview of the snippet
    exec(snippet)  # Execute the snippet
    return "Execution completed."

def master(file_path):
    keywords = load_keywords_from_excel(file_path)
    if keywords is None:
        print("Failed to load keywords.")
        return  # Stop further execution if keywords are not loaded

    print("Loaded keywords:", keywords)  # Debug print to show loaded keywords
    labeled_resources = []
    
    # Label each snippet and allocate resources
    for snippet in cnn_snippets:
        resources = label_and_allocate(snippet, keywords)
        labeled_resources.append((resources, snippet))
    
    # Using ThreadPoolExecutor to simulate slave execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(run_snippet, snippet): resources for resources, snippet in labeled_resources}
        for future in concurrent.futures.as_completed(futures):
            resources = futures[future]
            try:
                result = future.result()
                print(f"Resources used (CPU, GPU, TPU): {resources} -> {result}")
            except Exception as e:
                print(f"Error executing snippet: {e}")


if __name__ == '__main__':
    # Specify the path to your Excel file
    excel_file_path = 'resource_allocation_dataset.xlsx'
    master(excel_file_path)







# import concurrent.futures
# import pandas as pd
# import tensorflow as tf

# # Load keywords from Excel
# def load_keywords_from_excel(file_path):
#     try:
#         df = pd.read_excel(file_path)
#         print("Columns in the Excel file:", df.columns.tolist())  # Print the columns to check
#         df.columns = df.columns.str.strip()  # Strip whitespace from column names

#         # Create a list to hold keywords and their corresponding resource allocations
#         keywords = []
#         for _, row in df.iterrows():
#             # Extract keyword and resources, assuming they are in the right format
#             resource = (int(row['CPU']), int(row['GPU']), int(row['TPU']))
#             keywords.append((row['Keyword'], *resource))  # Add keyword and resource tuple to the list
        
#         return keywords  # Return the list of keywords
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None  # Return None in case of an error



# # Load CNN snippets to be executed
# cnn_snippets = [
#     """import tensorflow as tf
# from tensorflow.keras import layers, models

# def create_cnn_model(input_shape):
#     model = models.Sequential()
#     model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape))
#     model.add(layers.MaxPooling2D((2, 2)))
#     model.add(layers.Conv2D(64, (3, 3), activation='relu'))
#     model.add(layers.MaxPooling2D((2, 2)))
#     model.add(layers.Conv2D(64, (3, 3), activation='relu'))
#     model.add(layers.Flatten())
#     model.add(layers.Dense(64, activation='relu'))
#     model.add(layers.Dense(10, activation='softmax'))
#     return model""",
    
#     """def compile_and_train_model(model, train_images, train_labels, epochs=10):
#         model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
#         model.fit(train_images, train_labels, epochs=epochs)""",
    
#     """def evaluate_model(model, test_images, test_labels):
#         test_loss, test_acc = model.evaluate(test_images, test_labels, verbose=2)
#         print(f'\\nTest accuracy: {test_acc}')""",
    
#     """def load_and_preprocess_data():
#         (train_images, train_labels), (test_images, test_labels) = tf.keras.datasets.cifar10.load_data()
#         train_images = train_images.astype('float32') / 255.0
#         test_images = test_images.astype('float32') / 255.0
#         return train_images, train_labels, test_images, test_labels"""
# ]

# # Default resource allocation
# default_resource = (1, 0, 0)  # CPU, GPU, TPU

# # Function to label and allocate resources based on keywords
# def label_and_allocate(snippet, keywords):
#     for keyword, cpu, gpu, tpu in keywords:
#         if keyword in snippet:
#             return (cpu, gpu, tpu)
#     return default_resource

# # Function to run each CNN snippet
# def run_snippet(snippet):
#     print(f"Executing snippet: {snippet[:30]}...")  # Print a preview of the snippet
#     exec(snippet)  # Execute the snippet
#     return "Execution completed."

# def master(file_path):
#     keywords = load_keywords_from_excel(file_path)
#     if keywords is None:
#         print("Failed to load keywords.")
#         return  # Stop further execution if keywords are not loaded

#     print("Loaded keywords:", keywords)  # Debug print to show loaded keywords
#     labeled_resources = []
    
#     # Label each snippet and allocate resources
#     for snippet in cnn_snippets:
#         resources = label_and_allocate(snippet, keywords)
#         labeled_resources.append((resources, snippet))
    
#     # Using ThreadPoolExecutor to simulate slave execution
#     with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
#         futures = {executor.submit(run_snippet, snippet): resources for resources, snippet in labeled_resources}
#         for future in concurrent.futures.as_completed(futures):
#             resources = futures[future]
#             try:
#                 result = future.result()
#                 print(f"Resources used (CPU, GPU, TPU): {resources} -> {result}")
#             except Exception as e:
#                 print(f"Error executing snippet: {e}")


# if __name__ == '__main__':
#     # Specify the path to your Excel file
#     excel_file_path = 'resource_allocation_dataset.xlsx'
#     master(excel_file_path)
