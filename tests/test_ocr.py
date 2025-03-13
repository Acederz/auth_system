import sys
import os
# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import unittest
from app.utils.ocr import OCRProcessor
import logging
import time
import timeout_decorator

class TestOCRProcessor(unittest.TestCase):
    def setUp(self):
        """测试前的准备工作"""
        # 设置测试图片路径
        self.test_images_dir = os.path.join(os.path.dirname(__file__), 'test_images')
        if not os.path.exists(self.test_images_dir):
            os.makedirs(self.test_images_dir)
        
        # 配置日志
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        
        # 初始化OCR处理器
        self.ocr_processor = OCRProcessor()
        self.logger.info("OCR处理器初始化完成")

    @timeout_decorator.timeout(30)  # 设置30秒超时
    def test_extract_text_from_image(self):
        """测试从图片中提取文字的功能"""
        # 指定测试图片路径
        test_image_path = os.path.join(self.test_images_dir, 'test_auth.jpg')
        
        # 添加时间记录
        start_time = time.time()
        self.logger.info("开始OCR处理...")
        
        # 测试文字提取
        extracted_text = self.ocr_processor.extract_text_from_image(test_image_path)
        
        # 记录处理时间
        processing_time = time.time() - start_time
        self.logger.info(f"OCR处理完成，耗时: {processing_time:.2f}秒")
        
        # 确认测试图片存在
        self.assertTrue(os.path.exists(test_image_path), 
                       f"测试图片不存在: {test_image_path}")
        
        # 验证提取结果
        self.assertIsNotNone(extracted_text, "文字提取失败，返回None")
        self.assertTrue(len(extracted_text) > 0, "提取的文字为空")
        
        # 验证提取文本的质量
        self.assertTrue('被授权人' in extracted_text, "未找到关键词'被授权人'")
        self.assertTrue('授权渠道' in extracted_text, "未找到关键词'授权渠道'")
        self.assertTrue('授权品牌' in extracted_text, "未找到关键词'授权品牌'")
        self.assertTrue('授权时间' in extracted_text, "未找到关键词'授权时间'")
        
        self.logger.info("提取的文字内容:")
        self.logger.info(extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text)

    @timeout_decorator.timeout(30)  # 添加30秒超时限制
    def test_extract_authorization_info_with_real_text(self):
        """使用真实OCR结果测试信息提取"""
        # 指定测试图片路径
        test_image_path = os.path.join(self.test_images_dir, 'test_auth.jpg')
        
        # 检查文件是否存在
        self.logger.info(f"正在检查测试图片: {test_image_path}")
        if not os.path.exists(test_image_path):
            self.logger.error("测试图片不存在！")
            self.fail("测试图片不存在")
        
        # 记录开始时间
        start_time = time.time()
        self.logger.info("开始OCR文字提取...")
        
        # 先进行OCR识别
        extracted_text = self.ocr_processor.extract_text_from_image(test_image_path)
        
        # 记录OCR耗时
        ocr_time = time.time() - start_time
        self.logger.info(f"OCR文字提取耗时: {ocr_time:.2f}秒")
        
        self.assertIsNotNone(extracted_text, "OCR文字提取失败")
        
        # 测试信息提取
        self.logger.info("开始测试授权信息提取")
        info = self.ocr_processor.extract_authorization_info(extracted_text)
        
        # 记录总耗时
        total_time = time.time() - start_time
        self.logger.info(f"总处理耗时: {total_time:.2f}秒")
        
        # 验证提取的信息
        self.assertIsNotNone(info, "授权信息提取失败")
        self.assertIsInstance(info, dict, "返回结果应为字典类型")
        
        # 验证所有必要字段
        required_fields = ['company', 'brand', 'channel', 'valid_period']
        for field in required_fields:
            self.assertIn(field, info, f"结果中缺少字段: {field}")
            self.assertIsNotNone(info[field], f"字段 {field} 的值为None")
        
        self.logger.info("提取的授权信息:")
        self.logger.info(info)

    def test_extract_authorization_info_with_mock_text(self):
        """使用模拟文本测试信息提取功能"""
        mock_text = """
        授权情况如下：
        被授权人：北京久久恒安商贸有限公司
        授权渠道：国网积分商城
        授权时间：2025年1月22日至2025年3月31日
        授权品牌：妙洁品牌，附件为具体授权产品详见附件1。
        """
        
        info = self.ocr_processor.extract_authorization_info(mock_text)
        
        # 验证提取的信息
        self.assertEqual(info['company'], "北京久久恒安商贸有限公司")
        self.assertEqual(info['brand'], "妙洁")
        self.assertEqual(info['channel'], "国网积分商城")
        self.assertEqual(info['valid_period'], "2025年1月22日至2025年3月31日")

    def test_process_document_complete(self):
        """测试完整的文档处理流程"""
        test_image_path = os.path.join(self.test_images_dir, 'test_auth.jpg')
        
        self.logger.info(f"开始测试完整文档处理流程: {test_image_path}")
        result = self.ocr_processor.process_document(test_image_path)
        
        # 验证处理结果
        self.assertIsNotNone(result, "文档处理失败，返回None")
        self.assertIsInstance(result, dict, "处理结果应该是字典类型")
        
        # 验证结果包含所有必要字段
        required_fields = ['company', 'brand', 'channel', 'valid_period']
        for field in required_fields:
            self.assertIn(field, result, f"结果中缺少字段: {field}")
            self.assertIsNotNone(result[field], f"字段 {field} 的值为None")
        
        self.logger.info("文档处理结果:")
        self.logger.info(result)

    def test_error_handling(self):
        """测试错误处理"""
        # 测试不存在的文件
        result = self.ocr_processor.process_document('nonexistent.jpg')
        self.assertIsNone(result, "对不存在的文件应返回None")
        
        # 测试空文本
        info = self.ocr_processor.extract_authorization_info("")
        self.assertIsNone(info, "对空文本应返回None")
        
        # 测试格式错误的文本
        invalid_text = "这是一段没有任何授权信息的文本"
        info = self.ocr_processor.extract_authorization_info(invalid_text)
        self.assertIsNotNone(info, "应返回包含None值的字典")
        self.assertTrue(all(v is None for v in info.values()), "所有字段值应为None")

    def test_performance(self):
        """测试OCR处理性能"""
        test_image_path = os.path.join(self.test_images_dir, 'test_auth.jpg')
        
        # 测试OCR处理时间
        start_time = time.time()
        result = self.ocr_processor.process_document(test_image_path)
        processing_time = time.time() - start_time
        
        self.assertIsNotNone(result, "处理失败")
        self.assertLess(processing_time, 10, "处理时间超过10秒")
        
        self.logger.info(f"文档处理耗时: {processing_time:.2f}秒")

def run_tests():
    """运行测试的主函数"""
    unittest.main(verbosity=2)

if __name__ == '__main__':
    run_tests() 