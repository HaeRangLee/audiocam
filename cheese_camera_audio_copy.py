import cv2
import os
import datetime
import time
import threading
from playsound import playsound
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import speech_recognition as sr

NUM_PICTURE = 6
CAMERA_INDEX = 1
file_path_정답 = "C:/Users/hylee/Downloads/answer.mp3"
file_path_카메라 = "C:/Users/hylee/Downloads/camera.mp3"

PHOTO_FRAME_DICT = {
    "치즈": "templates/ydp4cuts_brown.png",
    "김치": "templates/ydp4cuts.png",
}

PHOTO_FRAME_KEY = ""

def listen_for_signal():
    global PHOTO_FRAME_KEY
    r = sr.Recognizer()
    mic = sr.Microphone()
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
            if "치즈" in text or "김치" in text:
                print("Signal detected!")
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
    global PHOTO_FRAME_KEY
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        messagebox.showerror("Error", "Failed to open camera")
        return

    pictures = []
    countdown_time = 60
    interval = 10

    # Create a window for the preview
    preview_window = tk.Toplevel(root)
    preview_window.title("Camera Preview")
    preview_label = tk.Label(preview_window)
    preview_label.pack()

    timer_label = tk.Label(preview_window, text=f"Time left: {countdown_time} seconds")
    timer_label.pack()

    def update_preview():
        nonlocal countdown_time
        ret, frame = cap.read()
        if ret:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            img.thumbnail((400, 300))  # Resize for display
            imgtk = ImageTk.PhotoImage(image=img)
            preview_label.imgtk = imgtk
            preview_label.configure(image=imgtk)
            
            if countdown_time > 0:
                countdown_time -= 1
                timer_label.config(text=f"Time left: {countdown_time} seconds")
            else:
                cap.release()
                preview_window.destroy()
                root.after(0, display_pictures, pictures)
                return
            
            if countdown_time % interval == 0:
                playsound(file_path_카메라)
                pictures.append(frame)
                print(f"Picture taken at {60 - countdown_time} seconds.")
        
        preview_window.after(1000, update_preview)

    update_preview()

def display_pictures(pictures):
    if not pictures:
        messagebox.showerror("Error", "No pictures to display")
        return
    display_window = tk.Toplevel(root)
    display_window.title(f"Select Best {NUM_PICTURE} Pictures")

    frame = tk.Frame(display_window)
    frame.pack(padx=10, pady=10)

    images = []
    selected_indices = []

    def on_select(idx):
        if idx not in selected_indices and len(selected_indices) < NUM_PICTURE:
            selected_indices.append(idx)
        elif idx in selected_indices:
            selected_indices.remove(idx)

    btns = []
    for idx, pic in enumerate(pictures):
        cv2image = cv2.cvtColor(pic, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        img.thumbnail((200, 200))
        imgtk = ImageTk.PhotoImage(image=img)
        images.append(imgtk)
        btn = tk.Button(frame, image=imgtk, command=lambda idx=idx: on_select(idx))
        btn.grid(row=0, column=idx)
        btns.append(btn)

    def confirm_selection():
        if len(selected_indices) > 0:
            selected_pics = [pictures[i] for i in selected_indices]
            display_window.destroy()
            adjust_imaging(selected_pics, 0)

    confirm_button = tk.Button(display_window, text="Confirm Selection", command=confirm_selection)
    confirm_button.pack(pady=10)

    display_window.images = images

def adjust_imaging(images, index):
    if index >= len(images):
        composite_image()
        return
    
    image = images[index]
    adjust_window = tk.Toplevel(root)
    adjust_window.title(f"Adjust Image {index + 1}")

    image_frame = tk.Frame(adjust_window)
    image_frame.pack(pady=10)

    def get_image():
        return image

    def update_image(val=None):
        adjusted = get_image()
        cv2image = cv2.cvtColor(adjusted, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        img_label.configure(image=imgtk)
        img_label.image = imgtk

    cv2image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    img_label = tk.Label(image_frame, image=imgtk)
    img_label.image = imgtk
    img_label.pack()

    save_button = tk.Button(adjust_window, text="Save Image", command=lambda: save_image(index))
    save_button.pack()

    def save_image(idx):
        adjusted = get_image()
        images[idx] = adjusted
        adjust_window.destroy()
        adjust_imaging(images, index + 1)

def composite_image():
    frame_path = PHOTO_FRAME_DICT[PHOTO_FRAME_KEY]
    if not os.path.exists(frame_path):
        messagebox.showerror("Frame Error", f"Frame image {frame_path} not found.")
        return
    
    photo_frame = Image.open(frame_path).convert("RGBA")
    base_image = Image.new("RGBA", photo_frame.size, (255, 255, 255, 0))
    
    positions = [(71, 68), (737, 68), (71, 608), (741, 608)]
    frame_size = (660, 523)

    for i, pos in enumerate(positions):
        if i >= len(adjusted):
            break
        
        img = adjusted[i]
        cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        pil_image = Image.fromarray(cv2image)
        pil_image_resized = pil_image.resize(frame_size, Image.BILINEAR)
        base_image.paste(pil_image_resized, pos, pil_image_resized)

    final_composite = Image.alpha_composite(base_image, photo_frame)

    composite_window = tk.Toplevel(root)
    composite_window.title("Final Image")
    frame = tk.Frame(composite_window)
    frame.pack(padx=10, pady=10)
    
    tk_image = ImageTk.PhotoImage(final_composite)
    label = tk.Label(frame, image=tk_image)
    label.image = tk_image
    label.pack()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Camera App")
    take_pictures_button = tk.Button(root, text="Start", command=listen_for_signal)
    take_pictures_button.pack()
    root.mainloop()