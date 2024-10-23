import cv2
import os
import datetime
import time
import numpy as np


import tkinter as tk
from tkinter import messagebox
import threading
from PIL import Image, ImageTk

import speech_recognition as sr

CAMERA_INDEX = 1

NUM_PICTURE = 6

NUM_SAVE = 4

def print_picture(fname):
    # os.system(f"lpr {fname}") # 맥 버전
    os.system(f'mspaint /pt {fname}')
    # lpr: 파일을 프린트 (이후 사진기와 연결 필요) -> lpr -P [프린터 이름] [파일 이름]

def take_picture(fname):
    fname = f"{fname}.png"
    # 카메라 설정
    cap = cv2.VideoCapture(CAMERA_INDEX) # default camera
    ret, picture = cap.read() # ret이 True : 사진이 찍힘 
    if ret:
        # 파일 저장하기
        cv2.imwrite(f"{fname}", picture)
        print(f"Photo taken and saved as {fname}")
        #print_picture(fname)
        cv2.imshow(f'{fname}', picture)
    else:
        print(f"Failed to capture image to {fname}")
    cap.release()
    # Print the current date and time

def listen_for_signal():
    # 'cheese'를 인식하는 함수
    # 에러 좀 많이 남.. 최대한 간단한 스펠링을 인식하게 만들어서 어떻게든 구동되게 함.
    r = sr.Recognizer() # 객체 설정
    mic = sr.Microphone() # 마이크 설정 : 일단은 컴에 있는 마이크로 설정
    with mic as source:
        print("Adjusting for ambient noise...")
        r.adjust_for_ambient_noise(source) 

    while True:
        with mic as source:
            print("Listening for signal...")
            audio = r.listen(source)
        try:
            print("Recognizing audio...")
            text = r.recognize_google(audio, language='ko-KR')
            print(f"You said: {text}")
            if "치즈" in text or "김치" in text:  # lower() : 소문자로 바꾸기
                print("signal detected!")
                #take_pictures_thread(pictures) # 임의로 수정함
                # now = datetime.datetime.now()
                # take_picture(fname=f"{now.strftime('%m-%d-%H-%M')}")
                return True

        except sr.UnknownValueError:
            print("Could not understand audio")
            return False
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return False



def take_pictures_thread():    
    # Now take 4 pictures
    cap = cv2.VideoCapture(0)
    pictures = []
    for i in range(NUM_PICTURE):
        ret, frame = cap.read()
        if ret:
            pictures.append(frame)
            time.sleep(0.5)
            return pictures

    cap.release()
    # Display the pictures and allow user to select one
    #root.after(0, display_pictures, pictures)

def take_pictures():
    threading.Thread(target = take_pictures_thread).start()

def display_pictures(pictures): # pictures is a list of cv2 images
    if not pictures:
        messagebox.showerror("Error", "No pictures to display")
        return
    display_window = tk.Toplevel(root) # 함수를 실행하기 전에 root를 생성해야함

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
#DF
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
    frame_path = 'templates/ydp4cuts_brown.png'
    if not os.path.exists(frame_path):
        messagebox.showerrer("Frame Error", f"Frame image {frame_path} not found.")
        return
    
    # Load the frame (not a tkinker object lol)
    photo_frame = Image.open(frame_path).convert("RGBA")

    composite_window = tk.Toplevel(root)
    composite_window.title("Final Image")
    frame = tk.Frame(composite_window)
    frame.pack(pady=10)

    # 왼쪽 위를 (x=0,y=0)으로 두고, 각 틀의 맨 왼쪽 위를 (x,y)로 두자.
    positions = [(75,70),(740,70),(75,610),(740,610)] #각각 1,2,3,4번째 사진의 위치.

    for i, pos in enumerate(positions):
        if i > len(adjusted_images):
            break
        img = adjusted_images[i]

        # Convert OpenCV image (BGR) to PIL image (RGBA)
        cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        print(cv2image.shape)
        pil_image = Image.fromarray(cv2image)
        
        # 660 x 540 으로 만들고 싶다. 그러면 1920 x 1080 에서, 1320 인데 중심 기준으로 자르기.
        cropped_image = pil_image.crop()
        pil_image.thumbnail((1000,550)) # 1080 x 1920 임. 그러면 먼저 Adjust size as needed -> 이러다가 왜곡될 텐데. 가로 더 작은 걸로 crop 하기 & 학생들한테 자기 자신 보여주기 # 저러면 550 세로에 맞게 줄어든다.

        x, y = pos
        img_w, img_h = pil_image.size
        top_left = (x - img_w // 2, y - img_h // 2)

        image_padded = Image.new("RGBA", (photo_frame.width, photo_frame.height))
        image_padded.paste(pil_image, top_left)


        # Paste the image onto the frame
        photo_frame = Image.alpha_composite(pil_image, photo_frame) # 레이어 위치는?? 밑으로 갔으면 좋겠는데.
    
    imgtk = ImageTk.PhotoImage(image=photo_frame)
    img_label = tk.Label(frame, image=imgtk)
    img_label.image = imgtk
    img_label.pack()

    # Save the final composite image
    now = datetime.datetime.now()
    nowstr = now.strftime("%m%d_%H%M")
    final_filename = f'final_composite{nowstr}.png'
    photo_frame.save(final_filename)
    messagebox.showinfo("Composite saved",f"Final image saved as {final_filename}")
    # print_picture(final_filename) # 마지막에 프린트~


# 아래 것들은 원래 코드에 있던 애
# def display_pictures(pictures): # pictures is a list of cv2 images
#     display_window = tk.Toplevel(root)
#     display_window.title("Select a Best Picture")
#     images = []
#     for idx, pic in enumerate(pictures): 
#         cv2image = cv2.cvtColor(pic, cv2.COLOR_BGR2RGBA) # BGR: OpenCV -(전환)-> RGBA: PIL.
#         # RGBA : Red, Green, Blue, Alpha(투명도) 
#         img = Image.fromarray(cv2image)
#         #cv2image를 PIL image로 변환 : numpy array to PIL image
#         img.thumbnail((200, 200))
#         imgtk = ImageTk.PhotoImage(image=img)
#         images.append(imgtk) 
#         # Keep a reference to prevent garbage collection
#         # Create a button with the image
#         btn = tk.Button(display_window, image=imgtk,command = lambda idx = idx: select_picture(idx, pictures, display_window))
#         btn.grid(row=0, column=idx) # images are buttons, and they are placed in a single row.
#     # Keep a references to prevent garbage collection: save to display_window.images !!!
#     display_window.images = images

# def select_picture(idx, pictures, display_window):
#     selected_pic = pictures[idx]
#     display_window.destroy() # Now you can close the picture selection window
#     # Allow user to adjust imaging
#     adjust_imaging(selected_pic)

# # def adjust_imaging(image):
# #     adjust_window = tk.Toplevel(root)
# #     adjust_window.title("Adjust Imaging")
# #     adjust_window.geometry("600x600")

# #     image_frame = tk.Frame(adjust_window)
# #     image_frame.pack(pady=10)

# #     controls_frame = tk.Frame(adjust_window)
# #     controls_frame.pack(pady=10)

# #     save_frame = tk.Frame(adjust_window)
# #     save_frame.pack(pady=10)

# #     def get_image():
# #         brightness = brightness_scale.get()
# #         contrast = contrast_scale.get()
# #         adjusted = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness) # this image is opencv image
# #         return adjusted
    
# #     def update_image(val=None):
# #         adjusted = get_image()
# #         cv2image = cv2.cvtColor(adjusted, cv2.COLOR_BGR2RGBA)
#         img = Image.fromarray(cv2image)
#         img.thumbnail((500,400))
#         imgtk = ImageTk.PhotoImage(image = img)
#         img_label.configure(image = imgtk)
#         img_label.image = imgtk # Keep a reference

#     cv2image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
#     img = Image.fromarray(cv2image) # numpy array to PIL image
#     img.thumbnail((500, 400)) # Resize the image inplace
#     imgtk = ImageTk.PhotoImage(image=img) # open image with ImageTk.PhotoImage
#     img_label = tk.Label(image_frame, image=imgtk) # NOT adjust_window (full window), but image_frame
#     img_label.image = imgtk # Keep a reference
#     img_label.pack() # Place the image in the window # 안 보여주면 이젠 scale이라도 보이나

#     brightness_label = tk.Label(controls_frame, text="Brightness")
#     brightness_label.grid(row=0, column=0, padx=5,pady=5)
#     brightness_scale = tk.Scale(controls_frame, from_=-100, to=100, orient=tk.HORIZONTAL, length=300, command=update_image)
#     brightness_scale.set(0)
#     brightness_scale.grid(row=0, column=1, padx=5,pady=5)

#     contrast_label = tk.Label(controls_frame, text="Contrast")
#     contrast_label.grid(row=1, column=0, padx=5,pady=5)
#     contrast_scale = tk.Scale(controls_frame, from_=0.5, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, length=300, command=update_image)
#     contrast_scale.set(1.0)
#     contrast_scale.grid(row=1, column=1, padx=5,pady=5)

#     def save_image():
#         adjusted = get_image() # Adjust the image here and return the adjusted image
#         # Save the adjusted image
#         filename = 'adjusted.png'
#         cv2.imwrite(filename, adjusted)
#         messagebox.showinfo("Success", f"Image saved as {filename}")

#     save_button = tk.Button(adjust_window, text="Save Image", command=save_image)
#     save_button.pack()

if __name__ == "__main__":
    if listen_for_signal() : 
        root = tk.Tk()
        root.title("Camera App")
        take_pictures_button = tk.Button(root, text="Take Pictures", command=take_pictures)
        take_pictures_button.pack()
        root.mainloop() 
        
    


#     root = tk.Tk()
#     root.title("Camera App")
#     take_pictures_button = tk.Button(root, text="Take Pictures", command=take_pictures)
#     take_pictures_button.pack()
# #     root.mainloop()
# if __name__ == "__main__":
#     now = datetime.datetime.now()
#     take_picture(fname=f"{now.strftime('%m-%d-%H-%M')}")