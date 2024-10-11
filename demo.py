import math

def calculate_area(radius):
    return math.pi * radius ** 2

def calculate_circumference(radius):
    return 2 * math.pi * radius

def main():
    radius = float(input("Enter the radius of the circle: "))
    
    
    area = calculate_area(radius)
    print(f"Area of the circle: {area:.2f}")
    
    
    circumference = calculate_circumference(radius)
    print(f"Circumference of the circle: {circumference:.2f}")


if __name__ == "__main__":
    main()