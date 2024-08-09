import os
from ultralytics import YOLO
from PIL import Image

# Path to your trained model
model_path = '/Path/to/your/trained/model.pt'
model = YOLO(model_path)

# Folder containing the images you want to run inference on
images_folder = '/Path/to/your/images/folder'
cropped_images_folder = '/Path/to/your/cropped/folder'


for step_folder_name in os.listdir(images_folder):
    step_folder_path = os.path.join(images_folder, step_folder_name)

    for class_folder_name in os.listdir(step_folder_path):
        class_folder_path = os.path.join(step_folder_path, class_folder_name)
        
        # Create cropped folder
        cropped_class_folder_path = os.path.join(cropped_images_folder, step_folder_name, class_folder_name)
        os.makedirs(cropped_class_folder_path, exist_ok=True)
        
        for image_name in os.listdir(class_folder_path):
            image_path = os.path.join(class_folder_path, image_name)
            image = Image.open(image_path)
            image_extension = os.path.splitext(image_name)[1] 

            # Perform inference using YOLO model
            results = model.predict(image_path, save=False)

            # Iterate over each detected object
            for i, result in enumerate(results):
                for j, box in enumerate(result.boxes):
                    # Get the coordinates of the bounding box
                    xmin, ymin, xmax, ymax = box.xyxy[0].tolist()
                    
                    # Crop the image
                    cropped_image = image.crop((xmin, ymin, xmax, ymax))

                    # Save the cropped image
                    cropped_image_name = f"{os.path.splitext(image_name)[0]}_{j}{image_extension}"
                    cropped_image_path = os.path.join(cropped_class_folder_path, cropped_image_name)
                    cropped_image.save(cropped_image_path)

print("Crop images over !")
