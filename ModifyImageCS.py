import cv2 as cv
import numpy as np


def main():
    # get inputs: image, desired size, count of Aida, and desired number of threads
    image, orig_width, orig_height = get_image()
    width_in, width_cm, height_in, height_cm = get_desired_dimensions(orig_width, orig_height)
    aida_count = get_aida_inputs()
    thread_no = get_thread_count()

    # calculate number of stitches final pattern will be
    width_stitches, height_stitches = calc_stitches(width_in, height_in, aida_count)

    # for verification
    print("For final cross stitch of ", round(width_in, 1), "by", round(height_in, 1),
          "inch (", round(width_cm, 1), "by", round(height_cm, 1), " cm)")
    print("Number of stitches wide = ", width_stitches, ", and stitches high = ", height_stitches)
    print()

    # resize image
    img_resized = cv.resize(image, (width_stitches, height_stitches))
    print("Image Resized Dimensions are:", img_resized.shape[1], "by", img_resized.shape[0])
    show_image(img_resized, orig_width, orig_height)
    save_image(img_resized, 'img_resized.jpg')

    # reduce number of colours
    img_quant = quant(img_resized,thread_no)
    show_image(img_quant, orig_width, orig_height)
    save_image(img_quant, 'img_quant.jpg')

    while True:
        notRecog = 0
        isTrue = input("Do you wish to modify input variables? ('y' or 'n'): ")
        if isTrue == "n":
            break
        else:
            modSym = input("Modify width ('w'), height ('h'), Aida count ('a'), or thread number ('t'): ")
            if modSym == "w":
                isInch, isError = get_units()
                desired_input = input("Enter desired Width of cross-stitch: ")  # get width input
                desired_input = int(desired_input)
                width_in, width_cm = calc_inch_and_cm(isInch, desired_input)  # determine inch and cm values
                height_in = (width_in * orig_height) / orig_width
                height_cm = (width_cm * orig_height) / orig_width
            elif modSym == "h":
                isInch, isError = get_units()
                desired_input = input("Enter desired Height of cross-stitch: ")  # get height input
                desired_input = int(desired_input)
                height_in, height_cm = calc_inch_and_cm(isInch, desired_input)  # determine inch and cm values
                width_in = (height_in * orig_width) / orig_height
                width_cm = (height_cm * orig_width) / orig_height
            elif modSym == "a":
                aida_count = get_aida_inputs()
            elif modSym == "t":
                thread_no = get_thread_count()
            else:
                notRecog = 1
                stillModify = input("Did not recognise. Do you still want to modify? ('y' or 'n'): ")
                if stillModify == "n":
                    break

            if notRecog == 0:
                width_stitches, height_stitches = calc_stitches(width_in, height_in, aida_count)
                img_resized = cv.resize(image, (width_stitches, height_stitches))
                img_quant = quant(img_resized, thread_no)

                show_image(img_quant, orig_width, orig_height)
                save_image(img_quant, 'img_final.jpg')

                print()
                print("    Dimensions: (", round(width_in, 1), ", ", round(height_in, 1), ") inch")
                print("    Dimensions: (", round(width_cm, 1), ", ", round(height_cm, 1), ") cm")
                print("    Size in stitches: ", width_stitches, "wide by", height_stitches, "high")
                print("    Aida size: ", aida_count)
                print("    Thread count: ", thread_no)
                print()


def calc_stitches(width_in, height_in, aida_count):
    width_stitches = round(width_in * aida_count)
    height_stitches = round(height_in * aida_count)
    return width_stitches, height_stitches


def quant(image, k):
    # Reshape image into data type OpenCV K-means function can use
    img_reshape = image.reshape((-1,3))
    img_reshape = np.float32(img_reshape)
    # Apply K-means clustering to image
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    ret,label,center=cv.kmeans(img_reshape,k,None,criteria,10,cv.KMEANS_RANDOM_CENTERS)
    # Convert result into data type and shape matching the  original image
    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape(image.shape)
    return res2


def get_image():
    default_image = 'bird.jpg'
    input_path = input("Please enter path to image or 'default': ")

    if input_path == "default" or "d":
        image = cv.imread(default_image)
    else:
        image = cv.imread(input_path)

    isOpenImg = input("View image? ('y' or 'n'): ")
    if isOpenImg == "y":
        cv.imshow('image', image)
        cv.waitKey(0)
        cv.destroyAllWindows()

    height, width = image.shape[:2]
    return image, width, height


def get_desired_dimensions(img_width, img_height):
    print("Note: original image dimensions are", img_width, "by", img_height, "pixels.")
    while True:
        errorMessage = "NIL"
        isError = 0
        isWidth = 0

        dimen_input = input("Providing Width ('w') or Height ('h')? ")
        if dimen_input == "w":
            isWidth = 1
        elif dimen_input == "h":
            isWidth = 0
        else:
            isError = 1
            errorMessage = "ERROR: Did not recognise which dimension is being provided"

        isInch, isError = get_units(isError)
        if isError:
            errorMessage = "ERROR: Did not recognise units"

        if isWidth:
            desired_input = input("Enter desired Width of cross-stitch: ")  # get width input
            desired_input = int(desired_input)
            width_in, width_cm = calc_inch_and_cm(isInch, desired_input)  # determine inch and cm values
            height_in = (width_in * img_height) / img_width
            height_cm = (width_cm * img_height) / img_width
        else:
            desired_input = input("Enter desired Height of cross-stitch: ")  # get height input
            desired_input = int(desired_input)
            height_in, height_cm = calc_inch_and_cm(isInch, desired_input)  # determine inch and cm values
            width_in = (height_in * img_width) / img_height
            width_cm = (height_cm * img_width) / img_height

        if isError:
            print(errorMessage)
        else:
            break

    print("Total Width is", round(width_in, 1), " inch (", round(width_cm, 1), "cm)")
    print("Total Height is", round(height_in, 1), " inch (", round(height_cm, 1), "cm)")
    print()
    return width_in, width_cm, height_in, height_cm


def get_aida_inputs():
    aida_count = input("Aida cloth count (eg. 11 or 14): ")
    aida_count = int(aida_count)
    print()
    return aida_count


def get_thread_count():
    thread_no = input("Maximum number of threads: ")
    thread_no = int(thread_no)
    print()
    return thread_no


def get_units(isError = 0):
    units_for_size = input("Which units are dimensions provided in? [inch (i) or cm (c)]: ")
    if units_for_size == "c" or units_for_size == "C" or units_for_size == "cm":
        isInch = 0
        print("centimetres, got it")
    elif units_for_size == "i" or units_for_size == "I" or units_for_size == "inch":
        isInch = 1
        print("inches, got it")
    else:
        isError = 1
    return isInch, isError


def save_image(image, filename):
    isSave = input("Save Image? ('y' or 'n'): ")
    if isSave == 'y':
        cv.imwrite(filename, image)
        print('Image saved')
        print()


def calc_inch_and_cm(is_inch, val):
    if is_inch:
        val_inch = val
        val_cm = val * 2.54
    else:
        val_inch = val / 2.54
        val_cm = val
    return val_inch, val_cm


def show_image(image, orig_width, orig_height):
    cv.namedWindow('image', cv.WINDOW_NORMAL)
    cv.resizeWindow('image', orig_width, orig_height)
    cv.imshow('image', image)
    cv.waitKey(0)
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
