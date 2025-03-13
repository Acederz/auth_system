from paddleocr import PaddleOCR

def test_paddleocr():
    """测试 PaddleOCR 功能"""
    ocr = PaddleOCR(
    lang='en',
    det_model_dir='/Users/xuebing/.paddleocr/whl/det/en/en_PP-OCRv3_det_infer',
    rec_model_dir='/Users/xuebing/.paddleocr/whl/rec/en/en_PP-OCRv4_rec_infer'
    )  # 只需运行一次以加载模型到内存
    img_path = '/Users/xuebing/Desktop/shouquan/auth_system/tests/test_images/test_auth.jpg'  # 替换为您的图片路径
    result = ocr.ocr(img_path, det=False, cls=False)  # 不进行检测和分类

    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            print(line)

if __name__ == "__main__":
    test_paddleocr()


