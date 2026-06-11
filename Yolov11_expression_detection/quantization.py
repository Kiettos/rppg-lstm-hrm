import onnx
from onnxruntime.quantization.matmul_4bits_quantizer import MatMul4BitsQuantizer

def convert_onnx_to_int4(input_onnx_path, output_onnx_path):
    print(f"[INFO] Đang load model gốc: {input_onnx_path}")
    model = onnx.load(input_onnx_path)

    print("[INFO] Đang thực hiện lượng tử hóa INT4 (Weight-only)...")
    # Cấu hình bộ lượng tử hóa INT4
    quantizer = MatMul4BitsQuantizer(
        model=model,
        block_size=128,      # Nhóm 128 giá trị để tính scale/zero_point (chuẩn chung)
        is_symmetric=True,   # Lượng tử hóa đối xứng (giữ nguyên gốc 0)
        accuracy_level=1     # Mức độ tối ưu hóa cấu trúc
    )
    
    quantizer.process()
    
    # Lưu model mới
    quantizer.model.save(output_onnx_path)
    print(f"[SUCCESS] Đã lưu model INT4 tại: {output_onnx_path}")

# Hướng dẫn sử dụng
# Lưu ý: Bạn phải convert model PyTorch (.pt/.pth) sang ONNX (FP32) trước.
input_fp32 = "rppg_model_fp32.onnx" 
output_int4 = "rppg_model_int4.onnx"

# Bỏ comment dòng dưới để chạy
# convert_onnx_to_int4(input_fp32, output_int4)