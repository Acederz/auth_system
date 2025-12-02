"""
PDF 文档生成工具
根据 Generated 模型数据和模板文件生成PDF授权书
"""
import os
import sys
import subprocess
from datetime import datetime
from flask import current_app

# 分别导入各个模块，以便更准确地报告错误
Document = None
convert = None
pythoncom = None
_import_errors = []

try:
    from docx import Document
except Exception as e:
    # 捕获所有异常，不仅仅是 ImportError
    _import_errors.append(f'python-docx 导入失败: {type(e).__name__}: {str(e)}')

try:
    from docx2pdf import convert
except Exception as e:
    # 捕获所有异常，不仅仅是 ImportError
    _import_errors.append(f'docx2pdf 导入失败: {type(e).__name__}: {str(e)}')

try:
    import pythoncom
except Exception:
    # pythoncom 只在 Windows 上可用，这是正常的
    pass


class PDFGenerator:
    """PDF 文档生成器"""
    
    def __init__(self, template_dir=None):
        """
        初始化生成器
        
        Args:
            template_dir: 模板文件存放目录，如果为 None 则使用配置中的路径
        """
        # 使用配置中的路径
        if template_dir is None:
            try:
                self.template_dir = current_app.config.get('UPLOAD_FOLDER_TEMPLATE', 'app/static/templates')
            except RuntimeError:
                self.template_dir = 'app/static/templates'
        else:
            self.template_dir = template_dir
        
        # 字段映射：模型字段名 -> Word 文档中的占位符
        self.field_mapping = {
            'template_used': '《使用模板》',
            'store_type': '《店铺类型》',
            'authorized_entity': '《授权主体》',
            'platform': '《授权平台》',
            'brand': '《授权品牌》',
            'trademark_no': '《品牌商标号》',
            'store_name': '《店铺名称》',
            'period': '《授权期间》',
            'auth_number': '《授权字号》',
            'stamping_entity': '《授权方主体》',
            'stamping_date': '《用印时间》'
        }
    
    def generate_from_model(self, generated_model, output_dir=None):
        """
        从 Generated 模型生成 PDF 文档
        
        Args:
            generated_model: Generated 模型实例
            output_dir: 输出目录，如果为 None 则使用配置中的路径
            
        Returns:
            tuple: (success: bool, file_path: str or error_message: str)
        """
        if Document is None:
            error_msg = '系统缺少 python-docx 依赖，请先安装：pip install python-docx'
            if _import_errors:
                # 只显示 python-docx 相关的错误
                docx_errors = [e for e in _import_errors if 'python-docx' in e]
                if docx_errors:
                    error_msg += f'\n详细错误：{docx_errors[0]}'
                else:
                    error_msg += f'\n详细错误：{"; ".join(_import_errors)}'
            error_msg += '\n提示：如果已安装但仍报错，请检查：1) Python 环境是否正确；2) 虚拟环境是否激活；3) 依赖是否安装在当前 Python 环境中'
            return False, error_msg
        
        # 使用配置中的输出路径
        if output_dir is None:
            try:
                output_dir = current_app.config.get('UPLOAD_FOLDER_SHOUQUAN', 'app/static/generated_docs')
            except RuntimeError:
                output_dir = 'app/static/generated_docs'
        
        # 获取模板文件名
        template_name = generated_model.template_used
        if not template_name:
            return False, '未指定使用模板'
        
        # 移除可能已经包含的扩展名
        template_name_base = template_name
        for ext in ['.docx', '.doc', '.DOCX', '.DOC']:
            if template_name_base.endswith(ext):
                template_name_base = template_name_base[:-len(ext)]
                break
        
        # 构建模板文件路径
        template_path = None
        for ext in ['.docx', '.doc']:
            path = os.path.join(self.template_dir, f"{template_name_base}{ext}")
            # 标准化路径（处理混合斜杠问题）
            path = os.path.normpath(path)
            if os.path.exists(path):
                template_path = path
                break
        
        if not template_path:
            return False, f'未找到模板文件：{template_name_base}.docx'
        
        temp_word_path = None
        try:
            # 打开模板文档
            doc = Document(template_path)
            
            # 准备替换数据
            replace_data = self._prepare_replace_data(generated_model)
            
            # 替换文档中的占位符
            self._replace_in_document(doc, replace_data)
            
            # 生成临时Word文件路径（包含时间戳避免冲突）
            temp_word_path = self._generate_temp_word_path(generated_model, output_dir)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(temp_word_path), exist_ok=True)
            
            # 保存临时Word文档
            doc.save(temp_word_path)
            
            # 生成最终PDF文件路径（不包含时间戳）
            pdf_filename = self._generate_pdf_filename(generated_model)
            pdf_path = os.path.join(output_dir, pdf_filename)
            
            # 转换为PDF - 根据操作系统选择转换方法
            if sys.platform == 'win32' and convert is not None:
                # Windows: 使用 docx2pdf (需要 Microsoft Word)
                if pythoncom is not None:
                    pythoncom.CoInitialize()
                try:
                    convert(temp_word_path, pdf_path)
                except Exception as e:
                    return False, f'PDF转换失败（Windows）: {str(e)}。请确保已安装 Microsoft Word。'
                finally:
                    if pythoncom is not None:
                        pythoncom.CoUninitialize()
            else:
                # Linux/Mac: 优先使用 LibreOffice 命令行工具
                success = self._convert_with_libreoffice(temp_word_path, pdf_path)
                if not success:
                    # 如果 LibreOffice 不可用，尝试使用 docx2pdf（如果可用，某些 Linux 环境可能支持）
                    if convert is not None:
                        try:
                            convert(temp_word_path, pdf_path)
                        except Exception as e:
                            return False, f'PDF转换失败。Linux系统请安装LibreOffice: sudo apt-get install libreoffice 或 sudo yum install libreoffice。错误详情: {str(e)}'
                    else:
                        return False, 'PDF转换失败。Linux系统请安装LibreOffice: sudo apt-get install libreoffice 或 sudo yum install libreoffice。如果已安装，请确保 libreoffice 命令在系统 PATH 中。'
            
            # 删除临时Word文件
            if os.path.exists(temp_word_path):
                os.remove(temp_word_path)
            
            return True, pdf_path
            
        except Exception as e:
            # 确保清理临时文件
            if temp_word_path and os.path.exists(temp_word_path):
                try:
                    os.remove(temp_word_path)
                except:
                    pass
            return False, f'生成PDF失败: {str(e)}'
    
    def _prepare_replace_data(self, generated_model):
        """准备替换数据"""
        replace_data = {}
        
        for field_name, placeholder in self.field_mapping.items():
            value = getattr(generated_model, field_name, '')
            replace_data[placeholder] = value if value else placeholder
        
        return replace_data
    
    def _replace_in_document(self, doc, replace_data):
        """替换文档中的所有占位符"""
        # 替换段落中的文本
        for paragraph in doc.paragraphs:
            self._replace_in_paragraph(paragraph, replace_data)
        
        # 替换表格中的文本
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        self._replace_in_paragraph(paragraph, replace_data)
        
        # 替换页眉页脚中的文本
        for section in doc.sections:
            # 页眉
            header = section.header
            for paragraph in header.paragraphs:
                self._replace_in_paragraph(paragraph, replace_data)
            # 替换页眉中的文本框
            self._replace_in_shapes(header, replace_data)
            
            # 页脚
            footer = section.footer
            for paragraph in footer.paragraphs:
                self._replace_in_paragraph(paragraph, replace_data)
            # 替换页脚中的文本框
            self._replace_in_shapes(footer, replace_data)
        
        # 替换正文中的文本框和形状
        self._replace_in_shapes(doc, replace_data)
    
    def _replace_in_shapes(self, parent, replace_data):
        """
        替换文本框和形状中的文本
        
        Args:
            parent: Document 或 Header/Footer 对象
            replace_data: 替换数据字典
        """
        try:
            # 获取 XML 元素
            if hasattr(parent, 'element'):
                element = parent.element
            elif hasattr(parent, '_element'):
                element = parent._element
            else:
                return
            
            # 查找所有文本框（w:txbxContent）
            from docx.oxml.ns import qn
            
            # 查找所有文本框内容
            txbx_contents = element.findall('.//' + qn('w:txbxContent'))
            
            for txbx_content in txbx_contents:
                # 在文本框内查找所有段落
                paragraphs = txbx_content.findall('.//' + qn('w:p'))
                
                for p_element in paragraphs:
                    # 获取段落中的所有文本
                    text_elements = p_element.findall('.//' + qn('w:t'))
                    
                    if not text_elements:
                        continue
                    
                    # 收集完整文本
                    full_text = ''.join([t.text or '' for t in text_elements])
                    
                    # 检查是否需要替换
                    need_replace = any(placeholder in full_text for placeholder in replace_data.keys())
                    
                    if need_replace:
                        # 执行替换
                        new_text = full_text
                        for placeholder, value in replace_data.items():
                            new_text = new_text.replace(placeholder, str(value))
                        
                        # 更新第一个文本元素，清空其他
                        if text_elements:
                            text_elements[0].text = new_text
                            # 清空其他文本元素
                            for t in text_elements[1:]:
                                t.text = ''
        
        except Exception as e:
            # 如果处理文本框出错，记录但不中断整个替换过程
            print(f"警告：处理文本框时出错: {str(e)}")
    
    def _replace_in_paragraph(self, paragraph, replace_data):
        """替换段落中的占位符"""
        full_text = paragraph.text
        need_replace = any(placeholder in full_text for placeholder in replace_data.keys())
        
        if need_replace:
            new_text = full_text
            for placeholder, value in replace_data.items():
                new_text = new_text.replace(placeholder, str(value))
            
            if new_text != full_text:
                original_runs = list(paragraph.runs)
                for run in paragraph.runs:
                    run.text = ''
                
                if original_runs:
                    run = original_runs[0]
                    run.text = new_text
                else:
                    paragraph.add_run(new_text)
    
    def _generate_temp_word_path(self, generated_model, output_dir):
        """生成临时Word文件路径（包含时间戳避免并发冲突）"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')  # 包含微秒，更精确
        
        parts = []
        if generated_model.store_type:
            parts.append(generated_model.store_type)
        if generated_model.store_name:
            parts.append(generated_model.store_name)
        parts.append(timestamp)  # 临时文件包含时间戳
        
        filename = '_'.join(parts)
        filename = self._sanitize_filename(filename)
        filename = f"{filename}.docx"
        
        return os.path.join(output_dir, filename)
    
    def _generate_pdf_filename(self, generated_model):
        """生成最终PDF文件名（不包含时间戳）"""
        parts = []
        if generated_model.store_type:
            parts.append(generated_model.store_type)
        if generated_model.store_name:
            parts.append(generated_model.store_name)
        
        filename = '_'.join(parts)
        filename = self._sanitize_filename(filename)
        return f"{filename}.pdf"
    
    def _sanitize_filename(self, filename):
        """清理文件名中的非法字符"""
        illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        
        for char in illegal_chars:
            filename = filename.replace(char, '_')
        
        return filename
    
    def _convert_with_libreoffice(self, docx_path, pdf_path):
        """
        使用 LibreOffice 命令行工具将 Word 文档转换为 PDF（Linux/Mac）
        
        Args:
            docx_path: Word 文档路径
            pdf_path: 输出 PDF 路径
            
        Returns:
            bool: 转换是否成功
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(pdf_path)
            os.makedirs(output_dir, exist_ok=True)
            
            # 尝试不同的 LibreOffice 命令
            libreoffice_cmds = [
                ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', output_dir, docx_path],
                ['soffice', '--headless', '--convert-to', 'pdf', '--outdir', output_dir, docx_path],
            ]
            
            for cmd in libreoffice_cmds:
                try:
                    result = subprocess.run(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=60,
                        check=False
                    )
                    
                    if result.returncode == 0:
                        # LibreOffice 生成的 PDF 文件名可能与预期不同
                        # 查找生成的 PDF 文件
                        base_name = os.path.splitext(os.path.basename(docx_path))[0]
                        generated_pdf = os.path.join(output_dir, f'{base_name}.pdf')
                        
                        if os.path.exists(generated_pdf):
                            # 如果文件名不同，重命名
                            if generated_pdf != pdf_path:
                                if os.path.exists(pdf_path):
                                    os.remove(pdf_path)
                                os.rename(generated_pdf, pdf_path)
                            return True
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            return False
        except Exception as e:
            print(f"LibreOffice 转换错误: {str(e)}")
            return False


# 便捷函数
def generate_pdf_document(generated_model, output_dir=None):
    """
    便捷函数：生成单个 PDF 文档
    
    Args:
        generated_model: Generated 模型实例
        output_dir: 输出目录，如果为 None 则使用配置中的路径
        
    Returns:
        tuple: (success: bool, file_path: str or error_message: str)
    """
    generator = PDFGenerator()
    return generator.generate_from_model(generated_model, output_dir)

