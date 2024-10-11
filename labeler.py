import pandas as pd

# Load the Excel file containing keywords and their corresponding CPU, GPU, TPU values
df_keywords = pd.read_excel('resource_allocation_dataset.xlsx')

# Convert the DataFrame to a dictionary for easier access
keywords_dict = df_keywords.set_index('Keyword')[['CPU', 'GPU', 'TPU']].T.to_dict()

# Default values (1 for CPU, 0 for GPU and TPU)
default_labels = [1, 0, 0]

# Extracted snippets from the code
snippets = [
    "import math",
    "def calculate_area(radius):\n    return math.pi * radius ** 2",
    "def calculate_circumference(radius):\n    return 2 * math.pi * radius",
    "def main():\n    radius = float(input('Enter the radius of the circle: '))\n    area = calculate_area(radius)\n    print(f'Area of the circle: {area:.2f}')\n    circumference = calculate_circumference(radius)\n    print(f'Circumference of the circle: {circumference:.2f}')",
    "if __name__ == '__main__':\n    main()"
]

# Initialize a list to store the labeled snippets
labeled_snippets = []

# Process each snippet
for snippet in snippets:
    # Initialize label to default
    label = default_labels.copy()
    
    # Check for keyword matches in the snippet
    for keyword, values in keywords_dict.items():
        if keyword in snippet:
            label = [values['CPU'], values['GPU'], values['TPU']]
            break  # Exit the loop after the first match

    # Append the labeled snippet to the list
    labeled_snippets.append((snippet, label))

# Print the labeled snippets
for i, (snippet, label) in enumerate(labeled_snippets, start=1):
    print(f"Snippet {i}:")
    print(snippet)
    print(f"Label: {label}\n{'-' * 40}")
