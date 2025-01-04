import cv2
import os
import numpy as np
import matplotlib.pyplot as plt

"""
@authors: Lyrie Edler and Yehonathan Barda
@date: 04/12/2024
@Copyright (c) 2024 Lyrie Edler and Yehonathan Barda. All rights reserved.
"""

def calculate_contact_angle(image_path, Params_path = False):
    """
    Calculate the contact angle of a droplet in an image.
    This function processes an image to detect a droplet and its contact angle with the surface.
    It performs several image processing steps including grayscale conversion, contrast enhancement,
    Gaussian blur, edge detection, contour detection, and line fitting to determine the contact angle.

    Parameters:
    image_path (str): The file path to the image containing the droplet.
    Params_path (str): The file path to the parameters file containing the image processing parameters. Optional.
    Returns:
    float: The contact angle in degrees if the droplet is detected and the angle is calculated successfully.
           None if the droplet is not detected or if there is an error in processing.
    Note:
    - The function displays the intermediate results of the image processing steps. Make sure that drop and surface are detected correctly.
    - Prass q continue to the next image.
    - The contact angle is calculated based on the angle between the droplet and the surface.

    If you wish to change the parameters of the image processing, you can create a txt file named "parameters.txt" with the following values:
    CLIP_LIMIT = 3.0 # Contrast Limited Adaptive Histogram Equalization (CLAHE) clip limit
    THRESHOLD1 = 50 # Canny edge detection lower threshold
    THRESHOLD2 = 150 # Canny edge detection upper threshold
    POINTS_TO_TAKE = 30  # Number of points to consider for surface line detection
    HEIGHT_THRESHOLD_START = 40 # Minimum height difference to consider a point
    HEIGHT_THRESHOLD_FINISH = 5 # Maximum height difference to consider a point
    JUMP_THRESHOLD = 2 # Maximum jump in X to consider a point
    MIN_POINTS_TO_FIND = 4 # Minimum points to consider a line

    You can also pass the path to the parameters file as a second argument to the function.

    place the file in the same directory as this file.
    
    How to take the Image:
    - The image should be taken side-on with the droplet on a flat surface.
    - The surface need to be horizontal (small angle with in the image plain is ok) and in *eye level with the camera*.
    - The droplet should be clearly visible with a distinct boundary.
    - The background should be clean and uniform to avoid interference:
        * for teflon surface, black background is recommended.
        * for copper surface, light colord background is recommended.
    - The image should be in focus and well-lit to ensure accurate detection.
    - avoid any reflections on the droplet or the surface.
    - you may need to crop the image to focus on the droplet and surface only.
    - example images are provided in the repository.

    before running this function, make sure to have the following libraries installed:
    - opencv-python
    - numpy
    - matplotlib
    - cv2
    - os
    """

    try:
        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Error: Image not found or invalid format. Path: {image_path}")
        else:
            print(f"Processing image: {image_path}")

        # Parameters for image processing
        # Define the default parameters for image processing
        CLIP_LIMIT = 3.0  # Contrast Limited Adaptive Histogram Equalization (CLAHE) clip limit
        THRESHOLD1 = 50  # Canny edge detection lower threshold
        THRESHOLD2 = 150  # Canny edge detection upper threshold
        POINTS_TO_TAKE = 30  # Number of points to consider for surface line detection
        HEIGHT_THRESHOLD_START = 40  # Minimum height difference to consider a point
        HEIGHT_THRESHOLD_FINISH = 5  # Maximum height difference to consider a point
        JUMP_THRESHOLD = 2  # Maximum jump in X to consider a point
        MIN_POINTS_TO_FIND = 4  # Minimum points to consider a line

        if Params_path:
            if os.path.exists(Params_path):
                CLIP_LIMIT, THRESHOLD1, THRESHOLD2, POINTS_TO_TAKE, HEIGHT_THRESHOLD_START, \
                HEIGHT_THRESHOLD_FINISH, JUMP_THRESHOLD, MIN_POINTS_TO_FIND = load_parameters()
            else:
                raise ValueError(f"Error: Parameters file not found. Path: {Params_path}\nUsing default parameters or internal parameters.txt file.")
            
        elif os.path.exists("parameters.txt"):  # Check if the file exists
            CLIP_LIMIT, THRESHOLD1, THRESHOLD2, POINTS_TO_TAKE, HEIGHT_THRESHOLD_START, \
            HEIGHT_THRESHOLD_FINISH, JUMP_THRESHOLD, MIN_POINTS_TO_FIND = load_parameters()
            print("Using parameters from the parameters.txt file.")



        # Step 1: Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Step 2: Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=CLIP_LIMIT, tileGridSize=(8, 8))
        enhanced_gray = clahe.apply(gray)

        # Step 3: Gaussian Blur
        blurred = cv2.GaussianBlur(enhanced_gray, (5, 5), 0)

        # Step 4: Edge Detection
        edges = cv2.Canny(blurred, THRESHOLD1, THRESHOLD2)

        # Step 5: Bridge Gaps in Edges
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        bridged_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)

        # Step 6: Find Contours
        contours, _ = cv2.findContours(bridged_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Step 7: Identify the Largest Contour (Droplet)
        droplet_contour = None
        max_area = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 500:  # Ignore very small contours
                continue

            # Check if the contour is in the upper part of the image
            x, y, w, h = cv2.boundingRect(cnt)
            if y > gray.shape[0] // 2:
                continue  # Exclude contours below the midpoint

            # Prioritize the largest contour
            if area > max_area:
                droplet_contour = cnt
                max_area = area

        if droplet_contour is not None:
            result = image.copy()
            cv2.drawContours(result, [droplet_contour], -1, (0, 255, 0), 2)  # Green for droplet

            # Step 8: Find the Highest Point on the Droplet Contour
            highest_point = tuple(droplet_contour[droplet_contour[:, :, 1].argmin()][0])
            cv2.circle(result, highest_point, 5, (0, 0, 255), -1)  # Red for highest point

            # Step 9: Search for the Surface Start Point
            x_high, y_high = highest_point
            surface_start = None
            min_distance = 10  # Minimum vertical distance from the highest point
            search_range = 6  # Allow horizontal variation

            points_in_same_x = []

            # Lets find all the points close to our x, within search_range
            for x, y in droplet_contour[:, 0, :].tolist():
                if (x_high - search_range) < x < (x_high + search_range) and (y > y_high + min_distance):
                    points_in_same_x.append((x, y))

            # Lets Find the closest point to the highest x we can find and draw from that
            closnes = 999
            for x, y in points_in_same_x:
                if abs(x_high - x) <= closnes:
                    surface_start = (x, y)
                    closnes = abs(x_high - x)

            # Fallback to Bounding Box Bottom if no surface start found
            if surface_start is None:
                print("Failed to find a valid surface start point. Using bounding box fallback.")
                x, y, w, h = cv2.boundingRect(droplet_contour)
                surface_start = (x, y + h)

            cv2.circle(result, surface_start, 5, (255, 0, 0), -1)  # Blue for surface start point

            # Step 10: Define the Surface Line
            sorted_points = droplet_contour[:, 0, :]
            sorted_points = sorted_points[sorted_points[:, 0].argsort()]
            most_right_points = np.array([pt for pt in sorted_points[-POINTS_TO_TAKE:]])
            most_left_points = np.array([pt for pt in sorted_points[:POINTS_TO_TAKE]])
            most_right_point = (int(np.mean(most_right_points[:, 0])), int(np.mean(most_right_points[:, 1])))
            most_left_point = (int(np.mean(most_left_points[:, 0])), int(np.mean(most_left_points[:, 1])))
            surface_points = np.array([most_left_point, surface_start, most_right_point])
            if len(surface_points) < 2:
                raise ValueError("Insufficient points for surface detection.")

            [vx_d, vy_d, x0_d, y0_d] = cv2.fitLine(surface_points, cv2.DIST_L2, 0, 0.01, 0.01)

            # Getting the points of the line so we can compare to them later
            angle_x_range = np.arange(x_high, most_right_point[0], 1)  # Generate x values from 0 to image width
            angle_y_range = ((vy_d / vx_d) * (angle_x_range - x0_d) + y0_d).astype(int)  # Solve for y = m(x - x0) + y0
            line_points = np.column_stack((angle_x_range, angle_y_range))

            start_index = np.where(sorted_points[:, 0] == surface_start[0])[0][0]
            tmp_sorted_from_surface_point = sorted_points[start_index:]

            # Now we remove every dot under the line
            sorted_from_surface_point = []
            for srt_x, srt_y in tmp_sorted_from_surface_point:
                try:
                    index = int(np.where(line_points[:, 0] == srt_x)[0][0])
                except Exception:
                    continue
                if line_points[index][1] < srt_y:
                    continue
                sorted_from_surface_point.append((srt_x, srt_y))

            # Getting the most close points to the line by threshold so we can draw another vector on it
            tmp_angle_points = []
            for srt_x, srt_y in sorted_from_surface_point:
                try:
                    index = int(np.where(line_points[:, 0] == srt_x)[0][0])
                except Exception:
                    continue
                if not index:
                    continue
                if int(line_points[index][1] - srt_y) < HEIGHT_THRESHOLD_FINISH:
                    continue

                if int(line_points[index][1] - srt_y) > HEIGHT_THRESHOLD_START:
                    continue
                tmp_angle_points.append((srt_x, srt_y))

            # Comparing the angle points and filtering out anything going up
            # Filter all the points going down
            filtered_angle_points = []
            filter_start = 0
            for a_x, a_y in tmp_angle_points:
                if a_y >= filter_start:
                    filtered_angle_points.append(np.array([a_x, a_y]))
                    filter_start = a_y
                else:
                    continue

            # Now filter if theres and big jumps between points on X line
            tmp_filtered_angle_points = []
            prev_point = tmp_angle_points[0][0]
            for a_x, a_y in tmp_angle_points:
                if a_x - prev_point > JUMP_THRESHOLD and len(tmp_filtered_angle_points) > MIN_POINTS_TO_FIND:
                    break
                else:
                    tmp_filtered_angle_points.append(np.array([a_x, a_y]))
                    prev_point = a_x

            filtered_angle_points = np.array(tmp_filtered_angle_points)

            # Now we fit the line for the line of the last angle
            [fvx_d, fvy_d, fx0_d, fy0_d] = cv2.fitLine(filtered_angle_points, cv2.DIST_L2, 0, 0.01, 0.01)

            droplet_slope = vy_d / vx_d

            # Step 12: Calculate the Angle Between the Droplet and the Surface
            dot_product = vx_d * fvx_d + vy_d * fvy_d
            magnitude1 = np.sqrt(vx_d**2 + vy_d**2)
            magnitude2 = np.sqrt(fvx_d**2 + fvy_d**2)
            cos_theta = dot_product / (magnitude1 * magnitude2)
            angle_rad = np.arccos(np.clip(cos_theta, -1.0, 1.0))[0]  # Clip to handle numerical issues
            angle_deg = np.degrees(angle_rad)

            print(f"Angle between the lines: {angle_deg} degrees")

            # Define points for the first line
            pt1_line1 = (int(x0_d - vx_d * 1000), int(y0_d - vy_d * 1000))
            pt2_line1 = (int(x0_d + vx_d * 1000), int(y0_d + vy_d * 1000))

            # Define points for the second line
            pt1_line2 = (int(fx0_d - fvx_d * 1000), int(fy0_d - fvy_d * 1000))
            pt2_line2 = (int(fx0_d + fvx_d * 1000), int(fy0_d + fvy_d * 1000))

            # Draw the lines
            cv2.line(result, pt1_line1, pt2_line1, (255, 0, 0), 2)  # Green for the first line
            cv2.line(result, pt1_line2, pt2_line2, (0, 0, 255), 2)  # Blue for the second line

            # Display the final result
            plt.figure(figsize=(10, 6))
            plt.imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
            plt.title("Detected Droplet and Surface Lines (Contact Angle: {:.2f}°)".format(angle_deg))
            plt.axis('off')
            plt.text(0, -45, "Press q to continue to the next image", color='white', fontsize=12, backgroundcolor='black')
            plt.show()
            return angle_deg
        else:
            raise ValueError("Droplet not detected. Please review the intermediate results.")
    except Exception as e:
        error_function(image, str(e), droplet_contour)
        return None

def load_parameters():
    open_file = open("parameters.txt", "r")
    lines = open_file.readlines()
    for line in lines:
        if "CLIP_LIMIT" in line:
            CLIP_LIMIT = float(line.split("=")[1].strip())
        if "THRESHOLD1" in line:
            THRESHOLD1 = int(line.split("=")[1].strip())
        if "THRESHOLD2" in line:
            THRESHOLD2 = int(line.split("=")[1].strip())
        if "POINTS_TO_TAKE" in line:
            POINTS_TO_TAKE = int(line.split("=")[1].strip())
        if "HEIGHT_THRESHOLD_START" in line:
            HEIGHT_THRESHOLD_START = int(line.split("=")[1].strip())
        if "HEIGHT_THRESHOLD_FINISH" in line:
            HEIGHT_THRESHOLD_FINISH = int(line.split("=")[1].strip())
        if "JUMP_THRESHOLD" in line:
            JUMP_THRESHOLD = int(line.split("=")[1].strip())
        if "MIN_POINTS_TO_FIND" in line:
            MIN_POINTS_TO_FIND = int(line.split("=")[1].strip())
    open_file.close()
    return CLIP_LIMIT, THRESHOLD1, THRESHOLD2, POINTS_TO_TAKE, HEIGHT_THRESHOLD_START, HEIGHT_THRESHOLD_FINISH, JUMP_THRESHOLD, MIN_POINTS_TO_FIND

def error_function(result, error_message, contour = None):
    print(error_message)
    # Display the intermediate result
    if contour is not None:
        cv2.drawContours(result, [contour], -1, (0, 255, 0), 2)
    plt.figure(figsize=(10, 6))
    plt.imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    plt.title("Error Occurred")
    plt.axis('off')
    plt.text(0, -55, "Press q to continue to the next image", color='white', fontsize=12, backgroundcolor='black')
    plt.text(0, 850, error_message, color='red', fontsize=16, backgroundcolor='white')
    plt.show()

if __name__ == "__main__":
    WORKING_FOLDER = '.'
    ACCEPTED_IMAGE_FORMATS = ['jpeg', 'jpg']

    for file_name in os.listdir(WORKING_FOLDER):
        if file_name.split('.')[-1] in ACCEPTED_IMAGE_FORMATS:
            calculate_contact_angle(file_name)
            print("\n")

