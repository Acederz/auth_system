from paddleocr import PaddleOCR
import os
import re
import logging
import numpy as np
from PIL import Image
import signal
from functools import wraps
import psutil
import gc

# 配置日志
def setup_logger():
    """配置日志记录器"""
    try:
        # 使用绝对路径创建日志目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        log_dir = os.path.join(project_root, 'logs')
        
        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)
        
        # 日志文件路径
        log_file = os.path.join(log_dir, 'ocr.log')
        
        # 配置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 文件处理器
        file_handler = logging.FileHandler(
            log_file, 
            encoding='utf-8',
            mode='a'  # 追加模式
        )
        file_handler.setFormatter(formatter)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # 创建logger
        logger = logging.getLogger('OCRProcessor')
        logger.setLevel(logging.DEBUG)
        
        # 清除现有的处理器
        logger.handlers = []
        
        # 添加处理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # 测试日志
        logger.info("日志系统初始化成功")
        logger.info(f"日志文件路径: {log_file}")
        
        return logger
        
    except Exception as e:
        # 如果日志设置失败，使用基本配置
        print(f"日志设置失败: {str(e)}")
        basic_logger = logging.getLogger('OCRProcessor')
        basic_logger.setLevel(logging.DEBUG)
        basic_logger.addHandler(logging.StreamHandler())
        return basic_logger

# 初始化日志
logger = setup_logger()

def timeout(seconds):
    """超时装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def handler(signum, frame):
                raise TimeoutError(f"函数执行超时 ({seconds}秒)")
            
            # 设置信号处理器
            original_handler = signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            
            try:
                result = func(*args, **kwargs)
            finally:
                # 恢复原始信号处理器
                signal.alarm(0)
                signal.signal(signal.SIGALRM, original_handler)
            return result
        return wrapper
    return decorator

class OCRProcessor:
    def __init__(self):
        logger.info("开始初始化 OCRProcessor...")
        try:
            logger.info("正在初始化 PaddleOCR...")
            
            # 检查系统资源
            memory = psutil.virtual_memory()
            logger.info(f"系统内存使用情况: {memory.percent}%")
            
            # 检查模型目录
            home_dir = os.path.expanduser('~')
            paddle_dir = os.path.join(home_dir, '.paddleocr', 'whl')
            
            model_paths = {
                'det': os.path.join(paddle_dir, 'det/ch/ch_PP-OCRv4_det_infer'),
                'rec': os.path.join(paddle_dir, 'rec/ch/ch_PP-OCRv4_rec_infer'),
                'cls': os.path.join(paddle_dir, 'cls/ch_ppocr_mobile_v2.0_cls_infer')
            }
            
            # 验证模型目录
            for name, path in model_paths.items():
                if not os.path.exists(path):
                    raise FileNotFoundError(f"{name} 模型目录不存在: {path}")
                logger.info(f"找到 {name} 模型: {path}")
            
            # 初始化 OCR，使用更简单的配置
            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang="ch",
                use_gpu=False,
                show_log=True,
                det_model_dir=model_paths['det'],
                rec_model_dir=model_paths['rec'],
                cls_model_dir=model_paths['cls'],
                # 性能优化
                enable_mkldnn=False,     # 禁用 MKLDNN
                cpu_threads=2,           # 适度的线程数
                rec_batch_num=1,         # 最小批处理
                max_text_length=64,      # 减少最大文本长度
                det_db_thresh=0.3,        # 检测阈值
                det_db_box_thresh=0.5,    # 框检测阈值
                det_limit_side_len=960,   # 限制图片大小
                rec_img_shape='3, 32, 320',  # 较小的识别尺寸
                use_space_char=False      # 禁用空格字符
            )
            logger.info("PaddleOCR初始化完成")
            
        except Exception as e:
            logger.error(f"PaddleOCR初始化失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    @timeout(60)
    def extract_text_from_image(self, image_path):
        """从图片中提取文字"""
        try:
            logger.info(f"开始处理图片: {image_path}")
            
            # 验证图片文件是否存在
            if not os.path.exists(image_path):
                logger.error(f"图片文件不存在: {image_path}")
                return None
            
            # 直接使用PaddleOCR处理图片
            logger.info("开始OCR识别...")
            try:
                result = self.ocr.ocr(image_path, cls=True)
                logger.info("OCR识别完成")
            except Exception as e:
                logger.error(f"OCR处理出错: {str(e)}")
                return None
            
            if not result or not result[0]:
                logger.warning("未能从图片中提取到文字")
                return None
            
            # 处理识别结果
            text_lines = []
            for line in result[0]:
                text = line[1][0]
                confidence = line[1][1]
                logger.debug(f"识别文本: {text}, 置信度: {confidence:.2f}")
                if confidence > 0.6:  # 置信度阈值
                    text_lines.append(text)
            
            if not text_lines:
                logger.warning("没有找到置信度足够高的文本")
                return None
            
            # 合并并处理文本
            text = '\n'.join(text_lines)
            text = text.replace(' ', '').strip()
            text = re.sub(r'\n+', '\n', text)
            
            logger.info(f"成功提取文字，共 {len(text)} 个字符")
            logger.debug(f"提取的文本: {text[:200]}...")
            return text
            
        except TimeoutError:
            logger.error("OCR处理超时")
            return None
        except Exception as e:
            logger.error(f"OCR处理错误: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def extract_authorization_info(self, text):
        """从OCR文本中提取授权信息"""
        if not text:
            logger.error("错误：输入文本为空")
            return None

        info = {
            'company': None,
            'brand': None,
            'channel': None,
            'valid_period': None
        }

        try:
            company_pattern = r'被授权人[：:]\s*([^\n]+)'
            channel_pattern = r'授权渠道[：:]\s*([^\n]+)'
            brand_pattern = r'授权品牌[：:]\s*([^品\n]+)品牌'
            date_pattern = r'授权时间[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)[至到](\d{4}年\d{1,2}月\d{1,2}日)'

            company_match = re.search(company_pattern, text)
            if company_match:
                info['company'] = company_match.group(1).strip()
                logger.debug(f"找到公司名称: {info['company']}")

            channel_match = re.search(channel_pattern, text)
            if channel_match:
                info['channel'] = channel_match.group(1).strip()
                logger.debug(f"找到渠道: {info['channel']}")

            brand_match = re.search(brand_pattern, text)
            if brand_match:
                info['brand'] = brand_match.group(1).strip()
                logger.debug(f"找到品牌: {info['brand']}")

            date_match = re.search(date_pattern, text)
            if date_match:
                start_date = date_match.group(1)
                end_date = date_match.group(2)
                info['valid_period'] = f"{start_date}至{end_date}"
                logger.debug(f"找到有效期: {info['valid_period']}")

            missing_fields = [k for k, v in info.items() if v is None]
            if missing_fields:
                logger.warning(f"以下字段未能提取: {', '.join(missing_fields)}")
                logger.debug(f"原始文本: {text}")

            return info

        except Exception as e:
            logger.error(f"提取授权信息时出错: {str(e)}")
            logger.error(f"原始文本: {text}")
            return None

    def process_document(self, file_path):
        """处理文档并提取信息"""
        text = self.extract_text_from_image(file_path)
        if text:
            return self.extract_authorization_info(text)
        return None 