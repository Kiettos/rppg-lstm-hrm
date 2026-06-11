import cv2

def upscale_bicubic_cv2(image_path, output_path, scale_factor=2.0):
    # Đọc ảnh đầu vào
    img = cv2.imread(image_path)
    
    if img is None:
        print("Không thể đọc được ảnh. Vui lòng kiểm tra lại đường dẫn.")
        return

    # Lấy kích thước gốc (chiều cao, chiều rộng)
    height, width = img.shape[:2]

    # Tính toán kích thước mới
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)

    # Thực hiện upscale với thuật toán Bicubic
    upscaled_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

    # Lưu ảnh kết quả
    cv2.imwrite(output_path, upscaled_img)
    print(f"Đã upscale ảnh thành công và lưu tại: {output_path}")

# Sử dụng hàm
input_image = "input.jpg"   # Thay bằng tên ảnh của bạn
output_image = "output_bicubic.jpg"
upscale_bicubic_cv2(input_image, output_image, scale_factor=2.0) # Phóng to gấp 2 lần