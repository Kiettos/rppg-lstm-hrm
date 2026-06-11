import os
import time
import threading
import cv2
import torch
import pandas as pd
import numpy as np
from collections import deque
from fastapi import FastAPI, BackgroundTasks, UploadFile, File
from ultralytics import YOLO

# Import class mô hình rPPG của bạn (Đảm bảo file model_rppg.py nằm cùng thư mục)
from model_rppg import rPPGNet

# Khởi tạo FastAPI Server
app = FastAPI(title="Edge Health Monitoring Server (Staff)")

def load_rppg_model(checkpoint_path="rppg_weights.pth"):
    """Hàm load custom rPPG Model lên GPU/CPU"""
    # Tự động nhận diện GPU (RTX 5050)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = rPPGNet()
    
    if os.path.exists(checkpoint_path):
        state_dict = torch.load(checkpoint_path, map_location=device)
        model.load_state_dict(state_dict)
        print(f"[INFO] Đã load rPPG model thành công trên {device}")
    else:
        print(f"[WARN] Không tìm thấy {checkpoint_path}. Vui lòng kiểm tra lại đường dẫn!")
        
    model.to(device)
    model.eval() # Khóa chế độ suy luận
    return model

@app.on_event("startup")
def startup_event():
    """Khởi chạy tài nguyên khi bật Server (Bước 1)"""
    print("[INFO] Đang khởi động Application Server...")
    
    # Load 2 Models vào RAM/VRAM
    app.state.yolo = YOLO("yolov11_model.pt") 
    app.state.rppg = load_rppg_model("rppg_weights.pth")
    
    # Khởi tạo RAM Buffer và Khóa an toàn
    app.state.buffer = deque(maxlen=300)
    app.state.lock = threading.Lock()
    
    # Tạo thư mục lưu trữ CSV nếu chưa có
    os.makedirs("data_export", exist_ok=True)
    print("[INFO] Server đã sẵn sàng nhận luồng Camera.")

def save_and_clear_buffer(data_snapshot):
    """Background Task: Ghi file CSV mà không làm gián đoạn luồng Video (Bước 5)"""
    df = pd.DataFrame(data_snapshot)
    filename = f"data_export/rppg_data_{int(time.time())}.csv"
    df.to_csv(filename, index=False)
    print(f"[BACKGROUND] Đã lưu {len(df)} frames vào {filename}")

def get_expression(results):
    """Hàm trích xuất nhãn biểu cảm từ kết quả YOLO"""
    try:
        # Lấy ID của class có confidence cao nhất
        cls_id = int(results[0].boxes.cls[0].item())
        return results[0].names[cls_id]
    except:
        return "Neutral"

@app.post("/process_frame")
async def process_frame(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """API Endpoint nhận frame từ Camera, xử lý YOLO & rPPG (Bước 2, 3, 4)"""
    
    # Đọc ảnh từ request (thay thế cho Bước 2 upscale/decode)
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        return {"error": "Không thể đọc frame ảnh"}

    # Mặc định khởi tạo các giá trị
    expression = "None"
    rppg_value = 0.0

    # Bước 3: Inference YOLO
    # Tắt verbose để console không bị spam khi chạy realtime
    results = app.state.yolo(frame, verbose=False) 
    
    if results[0].boxes is not None and len(results[0].boxes) > 0:
        # Lấy tọa độ bounding box khuôn mặt đầu tiên
        bbox = results[0].boxes.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = map(int, bbox)
        
        # Kiểm tra an toàn: Đảm bảo tọa độ không vượt quá kích thước ảnh
        h, w = frame.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        face_crop = frame[y1:y2, x1:x2]
        
        if face_crop.size > 0:
            expression = get_expression(results)

            # --- RPPG INFERENCE ---
            # Lưu ý: Thêm logic tiền xử lý (resize, normalize) tại đây tùy theo model của bạn
            with torch.no_grad():
                # Giả định hàm forward của bạn nhận numpy array hoặc Tensor
                # tensor_face = preprocess(face_crop).to(device)
                # rppg_value = app.state.rppg(tensor_face).item()
                
                # Tạm thời gán random để bạn test API nếu model chưa tích hợp xong
                rppg_value = np.random.uniform(60.0, 90.0) 

            # Bước 4 & 5: Ghi vào RAM Buffer và Window Evaluation
            with app.state.lock:
                app.state.buffer.append({
                    'timestamp': time.time(),
                    'expression': expression,
                    'rppg_signal': rppg_value
                })

                # Nếu đủ 300 records
                if len(app.state.buffer) >= 300:
                    # Chép dữ liệu ra một list mới để đẩy vào luồng phụ
                    data_to_save = list(app.state.buffer)
                    # Kích hoạt Background Task
                    background_tasks.add_task(save_and_clear_buffer, data_to_save)
                    # Xóa bộ nhớ đệm ngay lập tức
                    app.state.buffer.clear()

    return {
        "status": "success", 
        "expression": expression, 
        "rppg": round(rppg_value, 2),
        "buffer_size": len(app.state.buffer)
    }