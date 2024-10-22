'''import cv2

def take_picture():
    # 1. Canon EOS 웹캠으로 인식된 카메라 장치 열기
    cap = cv2.VideoCapture(1)  # 0은 첫 번째 웹캠 장치를 나타냄, 필요에 따라 인덱스를 변경
    
    if not cap.isOpened():
        print("Cannot open camera")
        return
    
    # 2. 카메라로부터 프레임 읽기
    ret, frame = cap.read()
    
    if ret:
        # 3. 캡처한 이미지 파일로 저장
        filename = "eos_captured_image.png"
        cv2.imwrite(filename, frame)
        print(f"Photo saved as {filename}")
        
        # 화면에 캡처한 이미지 보여주기
        cv2.imshow("Captured Image", frame)
        cv2.waitKey(0)  # 키 입력 대기
        cv2.destroyAllWindows()  # 창 닫기
    else:
        print("Failed to capture image")
    
    # 4. 카메라 장치 해제
    cap.release()

# 실행
take_picture()'''
import cv2
import tkinter as tk
from PIL import Image, ImageTk

# 1. Tkinter 창 설정
root = tk.Tk()
root.title("웹캠 실시간 영상")

# 2. Tkinter Label에 비디오 프레임을 표시하기 위한 설정
label = tk.Label(root)
label.pack()

# 3. 비디오 캡처 객체 생성 (웹캠 사용)
cap = cv2.VideoCapture(0)

def show_frame():
    # 4. 웹캠에서 프레임 읽기
    ret, frame = cap.read()
    if ret:
        # 5. 프레임 색상 변환 (OpenCV는 BGR을 사용하므로, RGB로 변환해야 함)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 6. 프레임을 PIL 이미지로 변환
        img = Image.fromarray(frame)
        
        # 7. 이미지 크기를 Tkinter에서 사용할 수 있도록 변환
        imgtk = ImageTk.PhotoImage(image=img)
        
        # 8. Label에 이미지를 업데이트
        label.imgtk = imgtk  # 참조를 유지하기 위해 할당
        label.configure(image=imgtk)
        
        # 9. 10ms 후에 다음 프레임을 업데이트
        label.after(10, show_frame)

# 10. show_frame 함수 호출하여 프레임을 업데이트
show_frame()

# 11. Tkinter 메인 루프 실행
root.mainloop()

# 12. 웹캠 리소스 해제
cap.release()