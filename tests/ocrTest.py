import paddle
from paddleocr import PaddleOCR
import cv2
import re

def extract_brand(text):
    # 使用正则表达式匹配“授权品牌：”后面的内容，直到遇到“品牌；”
    match = re.search(r"授权品牌：(.*?)品牌", text)
    if match:
        # 提取匹配到的品牌名称
        brand = match.group(1).replace("_", "").strip()
        return brand
    else:
        return None
    
def orcScan(filepath):   
   # 读取图片
    #img_path = r'C:\Users\acederz\Documents\worksoft\pythonProject\auth_system\uploads\20250225164644-0001.tif'#带文本的图片
    img = cv2.imread(filepath)
    #如果识别不准，可以添加均值或高斯模糊来去噪
    img = cv2.GaussianBlur(img, (5, 5), 0)#先模糊，去除噪声
    # 执行文字检测和识别
    result = ocr.ocr(img)
    # 绘制结果
    info = {
        "company" : '',
        "channel" : '',
        "brand" : '',
        "valid_period" : ''
    }
    for line in result:
        #print(line)#如[[[[13.0, 15.0], [261.0, 8.0], [262.0, 51.0], [14.0, 58.0]], ('CMIITTD', 0.8830805420875549)]],文本区域的框的四个顶点坐标，文本内容及置信度
        for word in line:
            #print(word[-1][0])#CMIITTD
            if '被授权人：' in word[-1][0] :
                info["company"] = word[-1][0].replace('》','').replace('_','').replace(' ','').replace('被授权人：','')
            if '授权渠道：' in word[-1][0] :
                info["channel"] = word[-1][0].replace('》','').replace('_','').replace(' ','').replace('授权渠道：','')
            if '授权时间：' in word[-1][0] :
                info["valid_period"] = word[-1][0].replace('》','').replace('_','').replace(' ','').replace('授权时间：','')
            if '授权品牌：' in word[-1][0] :
                info["brand"] = extract_brand(word[-1][0])
            #print(word[-1][1])#0.8830805420875549
    print(info)
    return info


ocr = PaddleOCR(use_angle_cls=True, lang='ch')#第一次运行会自动下载模型，默认下载到工作目录的,ch是中文模型，也能检测英文
    # 读取图片
img_path = r'C:\Users\acederz\Downloads\20250307093639.png'#带文本的图片
#img_path = r'C:\Users\acederz\Downloads\20250225164644-0001.tif'
img = cv2.imread(img_path)
    #如果识别不准，可以添加均值或高斯模糊来去噪
img = cv2.GaussianBlur(img, (5, 5), 0)#先模糊，去除噪声
    # 执行文字检测和识别
result = ocr.ocr(img)

for line in result:
        #print(line)#如[[[[13.0, 15.0], [261.0, 8.0], [262.0, 51.0], [14.0, 58.0]], ('CMIITTD', 0.8830805420875549)]],文本区域的框的四个顶点坐标，文本内容及置信度
        for word in line:
            print(word[-1][0])#CMIITTD

info = {
        "company" : '',
        "channel" : '',
        "brand" : '',
        "valid_period" : ''
    }
for line in result:
        #print(line)#如[[[[13.0, 15.0], [261.0, 8.0], [262.0, 51.0], [14.0, 58.0]], ('CMIITTD', 0.8830805420875549)]],文本区域的框的四个顶点坐标，文本内容及置信度
        for word in line:
            #print(word[-1][0])#CMIITTD
            if '被授权人：' in word[-1][0] :
                info["company"] = word[-1][0].replace('》','').replace('_','').replace(' ','').replace('被授权人：','')
            if '授权渠道：' in word[-1][0] :
                info["channel"] = word[-1][0].replace('》','').replace('_','').replace(' ','').replace('授权渠道：','')
            if '授权时间：' in word[-1][0] :
                info["valid_period"] = word[-1][0].replace('》','').replace('_','').replace(' ','').replace('授权时间：','')
            if '授权品牌：' in word[-1][0] :
                info["brand"] = extract_brand(word[-1][0])
            #print(word[-1][1])#0.8830805420875549
print(info)