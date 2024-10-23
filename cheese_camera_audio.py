import cv2
import os
import datetime
import time
import ast

from playsound import playsound
import tkinter as tk
from tkinter import messagebox
import threading
from PIL import Image, ImageTk

import speech_recognition as sr

NUM_PICTURE = 6
NUM_SAVE = 4
PHOTO_FRAME_KEY = ""
CAMERA_INDEX = 0

file_path_정답 = "C:/Users/hylee/Downloads/answer.mp3"

PHOTO_FRAME_DICT = {
    "치즈": "templates/ydp4cuts_brown.png",
    "김치": "templates/ydp4cuts.png",
}

def print_picture(fname):
    os.system(f"lpr {fname}")

def listen_for_signal():
    global PHOTO_FRAME_KEY
    r = sr.Recognizer() # 객체 설정
    mic = sr.Microphone() # 마이크 설정 : 일단은 컴에 있는 마이크로 설정
    with mic as source:
        print("Adjusting for ambient noise...")
        r.adjust_for_ambient_noise(source) 

    while True: # 무한 루프로 계속 듣기: 이해될 때까지. 다만... 
        with mic as source:
            print("Listening for signal...")
            audio = r.listen(source)
        try:
            print("Recognizing audio...")
            text = r.recognize_google(audio, language='ko-KR')
            print(f"You said: {text}")
            if "치즈" in text or "김치" in text:  # lower() : 소문자로 바꾸기
                print("signal detected!")
                playsound(file_path_정답)
                if "치즈" in text:
                    PHOTO_FRAME_KEY = "치즈"
                elif "김치" in text:
                    PHOTO_FRAME_KEY = "김치"
                threading.Thread(target=take_pictures_thread).start()
                return

        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        
def take_pictures_thread():    
    # Now take 4 pictures
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        messagebox.showerror("Error", "Failed to open camera")
        return
    pictures = []
    for i in range(NUM_PICTURE):
        time.sleep(0.1) # 여기를 나중엔 타이머로 바꿔서 소리도 추가해서 내주기!!
        ret, frame = cap.read()
        if ret:
            pictures.append(frame)
            time.sleep(0.1)

    cap.release()
    # 이거 끝나면 자동으로 display_pictures 함수 실행되게 하기
    root.after(0, display_pictures, pictures)


def display_pictures(pictures): # pictures is a list of cv2 images
    if not pictures:
        messagebox.showerror("Error", "No pictures to display")
        return
    display_window = tk.Toplevel(root)
    display_window.title(f"Select Best {NUM_SAVE} Pictures")

    frame = tk.Frame(display_window) # Make a frame inside display_window!
    frame.pack(padx=10, pady=10)

    images = []
    selected_indices =  []

    def on_select(idx):
        if idx not in selected_indices and len(selected_indices) < NUM_SAVE:
            selected_indices.append(idx)
            btns[idx].config(relief=tk.SUNKEN)
        elif idx in selected_indices:
            selected_indices.remove(idx)
            btns[idx].config(relief=tk.RAISED)

        # Enable the confirm button only when SELECTED_PICS images are selected
        if len(selected_indices) == NUM_SAVE:
            confirm_button.config(state=tk.NORMAL)
        else:
            confirm_button.config(state=tk.DISABLED)
    
    btns = []
    for idx, pic in enumerate(pictures):
        cv2image = cv2.cvtColor(pic, cv2.COLOR_BGR2RGBA) # BGR: OpenCV, RGBA: PIL. So should change the order of the channels or you'll get crazy colors.
        img = Image.fromarray(cv2image)
        img.thumbnail((200, 200))
        imgtk = ImageTk.PhotoImage(image=img)
        images.append(imgtk) # Keep a reference to prevent garbage collection
        # Create a button with the image
        btn = tk.Button(frame, image=imgtk,command=lambda idx=idx: on_select(idx))
        btn.grid(row=0, column=idx) # images are buttons, and they are placed in a single row.
        btns.append(btn)

    def confirm_selection():
        if len(selected_indices) == NUM_SAVE:
            selected_pics = [pictures[i] for i in selected_indices]
            display_window.destroy()
            # Adjust each selected picture
            adjust_imaging(selected_pics, 0)
    
    confirm_button = tk.Button(display_window, text="Confirm Selection", state=tk.DISABLED, command=confirm_selection)
    confirm_button.pack(pady=10)

    # Keep a references to prevent garbage collection: save to display_window.images !!!
    display_window.images = images

adjusted_images = []

def adjust_imaging(images, index): # Images: the complete list. index: the index of a image to handle in this function. -> will be recursive. confirm_selection(): adjust_imaging(images, 0) -> adjust_imaging(images, 0) 
    if index >= len(images):
        # All images have been adjusted; proceed to composite
        composite_image()
        return
    
    image = images[index] # The main protagonist in this function!!
    adjust_window = tk.Toplevel(root)
    adjust_window.title(f"Adjust Image {index + 1}")
    adjust_window.geometry("600x600")

    image_frame = tk.Frame(adjust_window)
    image_frame.pack(pady=10)

    controls_frame = tk.Frame(adjust_window)
    controls_frame.pack(pady=10)

    save_frame = tk.Frame(adjust_window)
    save_frame.pack(pady=10)

    def get_image():
        # I think scaling a brightness is not..so useful. So does scaling a contrast. How about just applying a predefined filter to beautify? Or give some choice on cute filters? But anyway they are not so important!!
        brightness = brightness_scale.get()
        contrast = contrast_scale.get()
        adjusted = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness) # this image is opencv image
        return adjusted
    
    def update_image(val=None):
        adjusted = get_image()
        cv2image = cv2.cvtColor(adjusted, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        img.thumbnail((500,400))
        imgtk = ImageTk.PhotoImage(image=img)
        img_label.configure(image=imgtk)
        img_label.image = imgtk # Keep a reference

    cv2image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image) # numpy array to PIL image
    img.thumbnail((500, 400)) # Resize the image inplace
    imgtk = ImageTk.PhotoImage(image=img) # open image with ImageTk.PhotoImage
    img_label = tk.Label(image_frame, image=imgtk) # NOT adjust_window (full window), but image_frame
    img_label.image = imgtk # Keep a reference
    img_label.pack() # Place the image in the window

    brightness_label = tk.Label(controls_frame, text="Brightness")
    brightness_label.grid(row=0, column=0, padx=5,pady=5)
    brightness_scale = tk.Scale(controls_frame, from_=-100, to=100, orient=tk.HORIZONTAL, length=300, command=update_image)
    brightness_scale.set(0)
    brightness_scale.grid(row=0, column=1, padx=5,pady=5)

    contrast_label = tk.Label(controls_frame, text="Contrast")
    contrast_label.grid(row=1, column=0, padx=5,pady=5)
    contrast_scale = tk.Scale(controls_frame, from_=0.5, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, length=300, command=update_image)
    contrast_scale.set(1.0)
    contrast_scale.grid(row=1, column=1, padx=5,pady=5)

    def save_image():
        adjusted = get_image() # Adjust the image here and return the adjusted image
        images[index] = adjusted
        adjusted_images.append(adjusted)
        adjust_window.destroy()
        # Proceed to adjust the next image recursively
        adjust_imaging(images, index + 1) # 여기가 아닌 거 같은데?

    save_button = tk.Button(adjust_window, text="Save Image", command=save_image)
    save_button.pack()


def composite_image(): # 영랑네컷
    # add a save button to save the composite image
    def save_composite():
        now = datetime.datetime.now().strftime("%m%d_%H%M")
        save_path = f"composite_image_{now}.png"
        try:
            final_composite.save(save_path)
            print(f"Composite image saved as {save_path}")
        except Exception as e:
            print(f"Error saving composite image: {e}")

    import pdb; pdb.set_trace()
    frame_path = PHOTO_FRAME_DICT[PHOTO_FRAME_KEY]
    if not os.path.exists(frame_path):
        messagebox.showerrer("Frame Error", f"Frame image {frame_path} not found.")
        return
    
    # Load the frame (not a tkinker object lol)
    photo_frame = Image.open(frame_path).convert("RGBA") # PIL image.
    
    # Create a base image with the same size as the photo frame, transparent background
    base_image = Image.new("RGBA", photo_frame.size, (255, 255, 255, 0))
    
    # Define the positions (top-left corners) where images will be pasted
    positions = [(71, 68), (737, 68), (71, 608), (741, 608)]  # Positions for 1st, 2nd, 3rd, 4th images
    
    # Define the target size for each image
    frame_size = (660, 523)  # Width, Height
    
    # Define the aspect ratio of the frame rectangle
    target_aspect = frame_size[0] / frame_size[1]  # 654 / 523 ≈ 1.25

    for i, pos in enumerate(positions):
        if i >= len(adjusted_images):
            print(f"Only {len(adjusted_images)} images provided. Skipping remaining positions.")
            break  # Prevents IndexError if there are fewer images than positions
        
        img = adjusted_images[i]
        
        # Validate image dimensions
        if img.shape[1] < 1 or img.shape[0] < 1:
            print(f"Image {i+1} has invalid dimensions. Skipping.")
            continue
        
        # Convert OpenCV image (BGR) to PIL image (RGBA)
        try:
            cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        except Exception as e:
            print(f"Error converting image {i+1} from BGR to RGBA: {e}")
            continue
        
        pil_image = Image.fromarray(cv2image)
        
        # Get original image size
        img_w, img_h = pil_image.size
        img_aspect = img_w / img_h
        
        # Center crop to maintain aspect ratio
        if img_aspect > target_aspect:
            # Image is wider than target aspect ratio
            new_width = int(target_aspect * img_h)
            left = (img_w - new_width) // 2
            right = left + new_width
            top = 0
            bottom = img_h
        else:
            # Image is taller than target aspect ratio
            new_height = int(img_w / target_aspect)
            top = (img_h - new_height) // 2
            bottom = top + new_height
            left = 0
            right = img_w
        
        # Crop the image
        pil_image_cropped = pil_image.crop((left, top, right, bottom))
        
        # Resize the image to fit the frame rectangle
        pil_image_resized = pil_image_cropped.resize(frame_size, Image.BILINEAR)
        
        # Optional: Add a border or other effects here if desired
        
        # Paste the image onto the composite image at the specified position
        # Use the image itself as the mask to preserve transparency
        base_image.paste(pil_image_resized, pos, pil_image_resized)
    
    final_composite = Image.alpha_composite(base_image, photo_frame)
    
    # Create a new Tkinter window to display the final image
    composite_window = tk.Toplevel(root)
    composite_window.title("Final Image")

    frame = tk.Frame(composite_window) # Make a frame inside display_window!
    frame.pack(padx=10, pady=10)
    
    # Optionally, you can set the window size based on the composite image size -> but it's too big!!
    composite_window.geometry(f"{int(photo_frame.width/3)+100}x{int(photo_frame.height/3)+100}")
    
    # Convert the composite PIL image to a format Tkinter can display
    final_composite_thumbnail = final_composite.copy()
    final_composite_thumbnail.thumbnail((int(final_composite.width/3),int(final_composite.height/3)))
    tk_image = ImageTk.PhotoImage(final_composite_thumbnail)
    
    # Create a label to hold the image
    label = tk.Label(frame, image=tk_image)
    label.image = tk_image  # Keep a reference to prevent garbage collection
    label.pack()
    save_button = tk.Button(frame, text="Save Image", command=save_composite)
    save_button.pack(pady=10)

if __name__ == "__main__":
    # listen_for_cheese()
    root = tk.Tk()
    root.title("Camera App")
    take_pictures_button = tk.Button(root, text="Start", command=listen_for_signal)
    take_pictures_button.pack()
    root.mainloop()
