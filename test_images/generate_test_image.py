import numpy as np
import cv2
import os

# Create a directory for the test images if it doesn't exist
os.makedirs('test_images', exist_ok=True)

# Create a simple "soil" image (brown with some texture)
width, height = 800, 600
soil_image = np.zeros((height, width, 3), dtype=np.uint8)

# Base color for soil (brown)
soil_image[:, :] = [51, 85, 139]  # Brown in BGR format

# Add some texture and variations to make it look more like soil
for i in range(10000):
    x = np.random.randint(0, width)
    y = np.random.randint(0, height)
    r = np.random.randint(3, 7)
    color_var = np.random.randint(-20, 20, 3)
    new_color = np.clip(soil_image[y, x] + color_var, 0, 255)
    cv2.circle(soil_image, (x, y), r, new_color.tolist(), -1)

# Add some small stones and particles
for i in range(500):
    x = np.random.randint(0, width)
    y = np.random.randint(0, height)
    r = np.random.randint(1, 5)
    # Vary between light gray and dark gray
    stone_color = np.random.randint(80, 180)
    cv2.circle(soil_image, (x, y), r, [stone_color, stone_color, stone_color], -1)

# Save the image
output_path = 'test_images/soil_sample.jpg'
cv2.imwrite(output_path, soil_image)

print(f"Test soil image created at: {output_path}")

# Create a leaf image for plant health testing
leaf_image = np.zeros((height, width, 3), dtype=np.uint8)

# Base green color for healthy leaf
leaf_image[:, :] = [36, 139, 87]  # Green in BGR format

# Create leaf shape (simplified)
pts = np.array([[200, 100], [600, 100], [700, 300], [600, 500], [200, 500], [100, 300]], np.int32)
pts = pts.reshape((-1, 1, 2))
cv2.fillPoly(leaf_image, [pts], [36, 139, 87])

# Add veins
cv2.line(leaf_image, (400, 100), (400, 500), [26, 119, 67], 5)
for i in range(5):
    y = 150 + i * 80
    cv2.line(leaf_image, (400, y), (200 + i * 30, y), [26, 119, 67], 3)
    cv2.line(leaf_image, (400, y), (600 - i * 30, y), [26, 119, 67], 3)

# Add some disease spots (brown patches) for detection
for i in range(20):
    x = np.random.randint(200, 600)
    y = np.random.randint(150, 450)
    r = np.random.randint(5, 20)
    cv2.circle(leaf_image, (x, y), r, [51, 85, 139], -1)  # Brown spots

# Save the image
output_path = 'test_images/leaf_sample.jpg'
cv2.imwrite(output_path, leaf_image)

print(f"Test leaf image created at: {output_path}")

# Create a simple skin sample image for healthcare testing
skin_image = np.zeros((height, width, 3), dtype=np.uint8)

# Base color for skin (light beige)
skin_image[:, :] = [204, 213, 232]  # Light beige in BGR format

# Add some texture
for i in range(20000):
    x = np.random.randint(0, width)
    y = np.random.randint(0, height)
    r = np.random.randint(1, 3)
    color_var = np.random.randint(-10, 10, 3)
    new_color = np.clip(skin_image[y, x] + color_var, 0, 255)
    cv2.circle(skin_image, (x, y), r, new_color.tolist(), -1)

# Add a "suspicious" mole or lesion area
cv2.circle(skin_image, (400, 300), 50, [50, 50, 120], -1)  # Darker region
cv2.circle(skin_image, (400, 300), 40, [80, 80, 140], -1)  # Core
# Add some irregular borders to make it look like potential melanoma
for i in range(20):
    angle = np.random.uniform(0, 2 * np.pi)
    dist = np.random.randint(42, 55)
    x = int(400 + dist * np.cos(angle))
    y = int(300 + dist * np.sin(angle))
    cv2.circle(skin_image, (x, y), 8, [50, 50, 120], -1)

# Save the image
output_path = 'test_images/skin_sample.jpg'
cv2.imwrite(output_path, skin_image)

print(f"Test skin image created at: {output_path}")