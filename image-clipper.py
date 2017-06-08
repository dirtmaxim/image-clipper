import os
import sys
import numpy as np
import cv2

try:
    __import__("imp").find_module("dicompylercore")
    from dicompylercore import dicomparser

    dicom_support = True
except ImportError:
    dicom_support = False
    print("\"dicompylercore\" library was not found. \"image-clipper\" works without dicom support.")


# noinspection PyUnresolvedReferences
def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and not on_mouse.start:
        on_mouse.first_point = (x, y)
        on_mouse.start = True
    elif event == cv2.EVENT_MOUSEMOVE and on_mouse.start:
        on_mouse.move = True
        on_mouse.second_point = (x, y)
        canvas = on_mouse.image.copy()
        cv2.rectangle(canvas, on_mouse.first_point, on_mouse.second_point, (255, 255, 255), 2)
        cv2.imshow("image-clipper", canvas)
    elif event == cv2.EVENT_LBUTTONUP and on_mouse.start:
        if on_mouse.move:
            on_mouse.move = False
            x = on_mouse.first_point[0]
            y = on_mouse.first_point[1]
            width = on_mouse.second_point[0]
            height = on_mouse.second_point[1]

            if width < x:
                x, width = width, x

            if height < y:
                y, height = height, y

            scale_factor = on_mouse.original.shape[0] / on_mouse.image.shape[0]
            x_scaled = int(x * scale_factor)
            y_scaled = int(y * scale_factor)
            width_scaled = int(width * scale_factor)
            height_scaled = int(height * scale_factor)
            rectangle = on_mouse.image[y:height, x:width]
            rectangle_original = on_mouse.original[y_scaled:height_scaled, x_scaled:width_scaled]

            if on_mouse.final_width > 0 and on_mouse.final_height > 0:
                rectangle_original = cv2.resize(rectangle_original, (on_mouse.final_width, on_mouse.final_height))
            elif on_mouse.final_width <= 0 < on_mouse.final_height:
                rectangle_original = cv2.resize(rectangle_original,
                                                (rectangle_original.shape[1], on_mouse.final_height))
            elif on_mouse.final_width > 0 >= on_mouse.final_height:
                rectangle_original = cv2.resize(rectangle_original, (on_mouse.final_width, rectangle_original.shape[0]))

            cv2.imwrite("/Users/dirtmaxim/Desktop/scikit-learn/clips/" + str(on_mouse.number) + ".png",
                        rectangle_original)
            on_mouse.number += 1
            on_mouse.canceled = False
            labeled_image = on_mouse.image.copy()
            cv2.putText(labeled_image, "Saved. Z - cancel.", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255),
                        1)
            cv2.imshow("image-clipper", labeled_image)

            if on_mouse.show_clipped:
                cv2.imshow("clipped", rectangle)

        on_mouse.start = False


def main(argv):
    if len(argv) < 10:
        print("Usage: \"path_to_folder\" \"path_for_save\" \"position_to_start\""
              "\"save_number\" \"show_clipped\" \"open_grayscale\""
              "\"histogram_equalization\" \"final_width\" \"final_height\"")
        exit(1)

    path_to_folder = argv[1]
    path_for_save = argv[2]
    position_to_start = int(argv[3])
    save_number = int(argv[4])

    if argv[5].lower() in ["true", "1"]:
        show_clipped = True
    else:
        show_clipped = False

    if argv[6].lower() in ["true", "1"]:
        open_mode = 0
    else:
        open_mode = 1

    if argv[7].lower() in ["true", "1"]:
        histogram_equalization = True
    else:
        histogram_equalization = False

    final_width = int(argv[8])
    final_height = int(argv[9])
    walks = list(os.walk(path_to_folder))
    i = 0
    j = 0
    k = 1
    flag = False

    while i < len(walks):
        path, directories, files = walks[i]
        files = [file for file in files if not file[0] == "."]

        if flag:
            j = len(files) - 1

        while j < len(files):
            flag = False
            file = files[j]

            if k < position_to_start:
                k += 1
                j += 1
            else:
                _, extension = os.path.splitext(file)

                if extension == ".dcm" and dicom_support:
                    parsed = dicomparser.DicomParser(path + os.sep + file)
                    image = np.array(parsed.GetImage(), dtype=np.uint8)

                    if parsed.GetImageData()["photometricinterpretation"] == "MONOCHROME1":
                        image = 255 - image

                    if histogram_equalization:
                        image = cv2.equalizeHist(image)
                elif extension in [".bmp", ".pbm", ".pgm", ".ppm", ".sr", ".ras", ".jpeg", ".jpg", ".jpe", ".png",
                                   ".tiff", ".tif"]:
                    image = cv2.imread(path + os.sep + file, open_mode)

                    if histogram_equalization:
                        image = cv2.equalizeHist(image)
                else:
                    continue

                if image.shape[0] > image.shape[1]:
                    height = 512
                    width = int(height / image.shape[0] * image.shape[1])
                else:
                    width = 512
                    height = int(width / image.shape[1] * image.shape[0])

                scaled_image = cv2.resize(image, (width, height))
                cv2.imshow("image-clipper", scaled_image)
                cv2.setMouseCallback("image-clipper", on_mouse)
                on_mouse.image = scaled_image
                on_mouse.original = image
                on_mouse.path_for_save = path_for_save
                on_mouse.show_clipped = show_clipped
                on_mouse.final_width = final_width
                on_mouse.final_height = final_height

                if not hasattr(on_mouse, "number"):
                    on_mouse.number = save_number

                if not hasattr(on_mouse, "canceled"):
                    on_mouse.canceled = False

                on_mouse.start = False
                on_mouse.move = False
                code = cv2.waitKey(0)

                while code not in [2, 3, 27, 32]:
                    if code in [90, 122]:
                        if not on_mouse.canceled:
                            on_mouse.number -= 1
                            os.remove(path_for_save + os.sep + str(on_mouse.number) + ".png")
                            labeled_image = on_mouse.image.copy()
                            cv2.putText(labeled_image, "Cancelled.", (20, 20), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.5,
                                        (255, 255, 255), 1)
                            cv2.imshow("image-clipper", labeled_image)
                            on_mouse.canceled = True
                        else:
                            labeled_image = on_mouse.image.copy()
                            cv2.putText(labeled_image, "Error. Only one cancellation.", (20, 20),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                        (255, 255, 255), 1)
                            cv2.imshow("image-clipper", labeled_image)

                    code = cv2.waitKey(0)

                if code == 27:
                    print("Next file number: " + str(j + 2) + ".")
                    print("Next saved number: " + str(on_mouse.number) + ".")
                    exit(0)
                elif code in [3, 32]:
                    j += 1
                else:
                    if j > 0:
                        j -= 1
                    else:
                        if i > 0:
                            i -= 2
                            flag = True
        i += 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
