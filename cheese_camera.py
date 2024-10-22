import cv2
import os
import datetime
import time

import tkinter as tk
from tkinter import messagebox
import threading
from PIL import Image, ImageTk

import speech_recognition as sr

def print_picture(fname):
    os.system(f"lpr {fname}") 
    # lpr: 파일을 프린트 (이후 사진기와 연결 필요) -> lpr -P [프린터 이름] [파일 이름]

def take_picture(fname):
    fname = f"{fname}.png"
    # 카메라 설정
    cap = cv2.VideoCapture(0) # default camera
    ret, picture = cap.read() # ret이 True : 사진이 찍힘 
    if ret:
        # 파일 저장하기
        cv2.imwrite(f"{fname}", picture)
        print(f"Photo taken and saved as {fname}")
        print_picture(fname)
    else:
        print(f"Failed to capture image to {fname}")
    cap.release()
    # Print the current date and time

def listen_for_cheese():
    # 'cheese'를 인식하는 함수
    # 에러 좀 많이 남.. 최대한 간단한 스펠링을 인식하게 만들어서 어떻게든 구동되게 함.
    r = sr.Recognizer() # 객체 설정
    mic = sr.Microphone() # 마이크 설정 : 일단은 컴에 있는 마이크로 설정
    with mic as source:
        print("Adjusting for ambient noise...")
        r.adjust_for_ambient_noise(source) 

    while True:
        with mic as source:
            print("Listening for 'cheese'...")
            audio = r.listen(source)
        try:
            print("Recognizing audio...")
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            if "ch" in text.lower():  # lower() : 소문자로 바꾸기
                print("Cheese detected!")
                now = datetime.datetime.now()
                take_picture(fname=f"{now.strftime('%m-%d-%H-%M')}")
                break
            time.sleep(0.1)
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

def take_pictures_thread():    
    # Now take 4 pictures
    cap = cv2.VideoCapture(0)
    pictures = []
    for i in range(4):
        ret, frame = cap.read()
        if ret:
            pictures.append(frame)
            time.sleep(0.5)
    cap.release()
    # Display the pictures and allow user to select one
    root.after(0, display_pictures, pictures)

def take_pictures():
    threading.Thread(target = take_pictures_thread).start()


def display_pictures(pictures): # pictures is a list of cv2 images
    display_window = tk.Toplevel(root)
    display_window.title("Select a Best Picture")
    images = []
    for idx, pic in enumerate(pictures): 
        cv2image = cv2.cvtColor(pic, cv2.COLOR_BGR2RGBA) # BGR: OpenCV -(전환)-> RGBA: PIL.
        # RGBA : Red, Green, Blue, Alpha(투명도) 
        img = Image.fromarray(cv2image)
        #cv2image를 PIL image로 변환 : numpy array to PIL image
        img.thumbnail((200, 200))
        imgtk = ImageTk.PhotoImage(image=img)
        images.append(imgtk) 
        # Keep a reference to prevent garbage collection
        # Create a button with the image
        btn = tk.Button(display_window, image=imgtk,command = lambda idx = idx: select_picture(idx, pictures, display_window))
        btn.grid(row=0, column=idx) # images are buttons, and they are placed in a single row.
    # Keep a references to prevent garbage collection: save to display_window.images !!!
    display_window.images = images

def select_picture(idx, pictures, display_window):
    selected_pic = pictures[idx]
    display_window.destroy() # Now you can close the picture selection window
    # Allow user to adjust imaging
    adjust_imaging(selected_pic)

def adjust_imaging(image):
    adjust_window = tk.Toplevel(root)
    adjust_window.title("Adjust Imaging")
    adjust_window.geometry("600x600")

    image_frame = tk.Frame(adjust_window)
    image_frame.pack(pady=10)

    controls_frame = tk.Frame(adjust_window)
    controls_frame.pack(pady=10)

    save_frame = tk.Frame(adjust_window)
    save_frame.pack(pady=10)

    def get_image():
        brightness = brightness_scale.get()
        contrast = contrast_scale.get()
        adjusted = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness) # this image is opencv image
        return adjusted
    
    def update_image(val=None):
        adjusted = get_image()
        cv2image = cv2.cvtColor(adjusted, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        img.thumbnail((500,400))
        imgtk = ImageTk.PhotoImage(image = img)
        img_label.configure(image = imgtk)
        img_label.image = imgtk # Keep a reference

    cv2image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image) # numpy array to PIL image
    img.thumbnail((500, 400)) # Resize the image inplace
    imgtk = ImageTk.PhotoImage(image=img) # open image with ImageTk.PhotoImage
    img_label = tk.Label(image_frame, image=imgtk) # NOT adjust_window (full window), but image_frame
    img_label.image = imgtk # Keep a reference
    img_label.pack() # Place the image in the window # 안 보여주면 이젠 scale이라도 보이나

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
        # Save the adjusted image
        filename = 'adjusted.png'
        cv2.imwrite(filename, adjusted)
        messagebox.showinfo("Success", f"Image saved as {filename}")

    save_button = tk.Button(adjust_window, text="Save Image", command=save_image)
    save_button.pack()

# if __name__ == "__main__":
#     listen_for_cheese()
#     root = tk.Tk()
#     root.title("Camera App")
#     take_pictures_button = tk.Button(root, text="Take Pictures", command=take_pictures)
#     take_pictures_button.pack()
#     root.mainloop()
if __name__ == "__main__":
    take_picture(fname="test")