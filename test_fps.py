import cv2
import time
import sys
import io

# Ép terminal hiển thị tiếng Việt
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def benchmark_fps(target_fps):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # Dùng DSHOW để truy cập trực tiếp hơn
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FPS, target_fps)
    
    num_frames = 30 # Số lượng khung hình để lấy mẫu
    start = time.time()
    
    for i in range(num_frames):
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return 0
            
    end = time.time()
    seconds = end - start
    actual_fps = num_frames / seconds
    
    cap.release()
    return actual_fps

print("--- KIỂM TRA TỐC ĐỘ THỰC TẾ (BENCHMARK) ---")
test_levels = [30, 60, 90, 120]

for target in test_levels:
    real_fps = benchmark_fps(target)
    print(f"Yêu cầu: {target} FPS -> Thực tế đo được: {real_fps:.2f} FPS")

    # Nếu thực tế đo được chỉ quanh quẩn 30 trong khi yêu cầu là 60
    if target > 30 and real_fps < 35:
        print(f"   => Kết luận: Phần cứng của bạn bị khóa (Capped) ở 30 FPS.")
        break