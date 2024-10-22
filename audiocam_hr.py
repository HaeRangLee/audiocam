import cv2
import os
import datetime
import time

import tkinter as tk
from tkinter import messagebox
import threading
from PIL import Image, ImageTk

import speech_recognition as sr

import cv2


def take_picture(fname):
    fname = f"{fname}.png"
    # 카메라 설정
    cap = cv2.VideoCapture(0) # default camera
    ret, picture = cap.read() # ret이 True : 사진이 찍힘 
    if ret:
        # 파일 저장하기
        cv2.imwrite(f"{fname}", picture)
        print(f"Photo taken and saved as {fname}")
      #  cv2.imshow(f"{fname}", picture)
    else:
        print(f"Failed to capture image to {fname}")
    cap.release()

def print_picture(fname):
    os.system(f"lpr {fname}")

def cheese_detect() : 
    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print("Say cheese!")
        audio = r.listen(source)
    try : 
        text = r.recognize_google(audio)
        if "ch" in text.lower():
            print("Cheese detected!")
            return True
        else :
            print("Failed to detect cheese..")
            return False
    except sr.UnknownValueError:
        print("Could not understand audio")
        return False
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return False
    # 여기서 cheese_detect()는 cheese가 인식될 시 True를 반환하고, 아닐 시 False를 반환하는 함수임

    
def take_pictures_six():

    def display_what_is_taken():
        root = tk.Tk()
        root.title("영랑네컷 촬영중~!")

        video_frame = tk.Frame(root)  # 동영상을 띠울 창
        video_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        control_frame = tk.Frame(root) # 타이머를 띠울 창
        control_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        # 동영상을 띠울 라벨
        video_label = tk.Label(video_frame)
        video_label.pack()

        # 타이머를 띠울 라벨
        timer_label = tk.Label(control_frame, text="120", font=("Helvetica", 24))
        timer_label.pack(pady=20)


        



        cap = cv2.VideoCapture(0)

        ret, frame = cap.read()
        if ret : 
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            label.imgtk = imgtk
            label.configure(image=imgtk)

            label.after(10, display_what_is_taken)
        
    def display_what_is_taken_thread():
        threading.Thread(target=display_what_is_taken).start()
    
    pictures = []
    cap = cv2.VideoCapture(0)
    for i in range(6):
        ret, frame = cap.read()
        if ret:
            pictures.append(frame)
            print(f"Taking picture {i}")
            time.sleep(5)
    cap.release()



        

            # now = datetime.datetime.now()
            # take_picture(fname=f"{now.strftime('%m-%d-%H-%M')}")
            # print_picture(f"{now.strftime('%m-%d-%H-%M')}.png")

# 시작 : listen_for_cheese()
# 1번, 사진 6장을 찍어 pictures 리스트에 저장
# --> 지금 구현하다가 말았음(졸려..) : 사진을 찍을 때 GUI에 사진을 찍는 모습과 타이머 및 현재 몇장을 찍었는지 표시
# --> 동시에 진행하는 거라 threading을 써야될 거 같은 느낌이지만 정확히 모르겠음. -> 내일 누님께 질문하기
# 2번, select_pictures 함수를 호출하여 pictures 중에 4장을 선택
# 3번, 선택된 4장의 사진을 프레임에 넣어 하나의 이미지 파일 출력
# -> 넣을 때 이미지를 포샵하고, 크기 조절 및 좌표 맞춰야함
# 4번, 출력된 이미지 파일을 프린터로 출력
# 촬영하기 전 사용자한테 이메일을 넣을 칸을 주면 자신 촬영 다 했을 때 아에 이메일로 보내주는 기능도 추가할 수 있을 듯
# 필터는.... 포기... 일단 구현만
# 음... 이거 구현하면서 느낀 건데... 이거 구현하려면 GUI에 대한 이해도가 높아야 할 거 같음... 그래서 GUI에 대해 공부해야할 거 같음 솔직히 GPT가 뭐라 말하는지 모르겠다.

# --> 진짜 ㅜ머가됐든 내일은 완성해야된다.
# 학교 가져가서 할까. 일찍 일어나서 노트북을 빌려보자!
