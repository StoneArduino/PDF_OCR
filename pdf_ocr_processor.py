# -*- coding: utf-8 -*-
import sys
import subprocess
import os
from pathlib import Path

# 导入 PyQt6 组件
from PyQt6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, 
                            QWidget, QFileDialog, QLabel, QProgressBar, QMessageBox, QStyle, QApplication)
from PyQt6.QtCore import Qt

# 导入 ocrmypdf
try:
    import ocrmypdf
except ImportError:
    print("未找到 ocrmypdf 模块")
    sys.exit(1)

def check_tesseract():
    """检查 Tesseract 安装状态"""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, 
                              text=True, 
                              encoding='utf-8',
                              check=True)
        print("Tesseract 已安装:", result.stdout.split('\n')[0])
        
        # 检查中文语言包
        result = subprocess.run(['tesseract', '--list-langs'],
                              capture_output=True,
                              text=True,
                              encoding='utf-8',
                              check=True)
        if 'chi_sim' not in result.stdout:
            print("未找到中文语言包")
            return False
        return True
    except Exception as e:
        print(f"检查 Tesseract 时出错: {e}")
        return False

def check_ghostscript():
    """检查 Ghostscript 安装状态"""
    try:
        # 首先尝试直接运行 gs 命令
        try:
            result = subprocess.run(['gs', '--version'], 
                                capture_output=True, 
                                text=True, 
                                check=True)
            print("Ghostscript 已安装:", result.stdout.strip())
            return True
        except FileNotFoundError:
            # 如果直接运行失败，尝试查找具体路径
            gs_path = None
            possible_paths = [
                r'C:\Program Files\gs\gs*\bin\gswin64c.exe',  # 64位版本
                r'C:\Program Files (x86)\gs\gs*\bin\gswin32c.exe',  # 32位版本
            ]

            # 展开通配符路径
            import glob
            for pattern in possible_paths:
                matches = glob.glob(pattern)
                if matches:
                    gs_path = matches[-1]  # 使用最新版本
                    break

            if gs_path:
                # 将 Ghostscript 目录添加到 PATH
                gs_dir = os.path.dirname(gs_path)
                if gs_dir not in os.environ['PATH']:
                    os.environ['PATH'] = gs_dir + os.pathsep + os.environ['PATH']
                
                result = subprocess.run([gs_path, '--version'], 
                                    capture_output=True, 
                                    text=True, 
                                    check=True)
                print("Ghostscript 已安装:", result.stdout.strip())
                return True

            print("未找到 Ghostscript，请安装 Ghostscript：")
            print("1. 访问 https://ghostscript.com/releases/gsdnld.html")
            print("2. 下载并安装最新版本")
            print("3. 确保将 Ghostscript 添加到系统环境变量 PATH 中")
            return False

    except Exception as e:
        print(f"检查 Ghostscript 时出错: {e}")
        print("请确保正确安装 Ghostscript 并添加到系统环境变量 PATH 中")
        return False

def check_dependencies():
    """检查必要的依赖"""
    try:
        import ocrmypdf
        import PyQt6
        import pdf2image
        import PIL
    except ImportError as e:
        print(f"缺少必要的依赖: {e}")
        sys.exit(1)

    if not check_tesseract() or not check_ghostscript():
        sys.exit(1)

    return True

class PDFProcessor:
    def __init__(self, input_dir="input", output_dir="output"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self._create_directories()

    def _create_directories(self):
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def process_single_pdf(self, input_file, output_file=None, progress_callback=None):
        try:
            if output_file is None:
                input_path = Path(input_file)
                output_file = str(Path(self.output_dir) / f"ocr_{input_path.name}")

            def progress_hook(info):
                if progress_callback:
                    if 'page' in info:
                        current = info.get('page', 0)
                        total = info.get('total_pages', 100)
                        stage = info.get('description', '')
                        progress = int((current / total) * 100)
                        progress_callback(progress, f"{stage}: {current}/{total}")

            ocrmypdf.ocr(
                input_file=input_file,
                output_file=output_file,
                language='chi_sim+eng+deu',
                skip_text=True,
                force_ocr=False,
                optimize=1,
                deskew=True,
                progress_bar=progress_hook
            )
            return True
        except Exception as e:
            print(f"处理文件出错 {input_file}: {str(e)}")
            return False

    def process_directory(self, language='chi_sim+eng+deu'):
        """
        处理输入目录中的所有PDF文件
        :param language: OCR语言，默认中文简体+英文
        """
        input_path = Path(self.input_dir)
        pdf_files = list(input_path.glob("*.pdf"))
        
        if not pdf_files:
            print("未找到PDF文件")
            return

        for pdf_file in pdf_files:
            output_file = str(Path(self.output_dir) / f"ocr_{pdf_file.name}")
            self.process_single_pdf(str(pdf_file), output_file, language)

class PDFProcessorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.processor = PDFProcessor()
        self.init_ui()

    def init_ui(self):
        """Initialize GUI interface"""
        # Set window properties
        self.setWindowTitle('Schindler PDF OCR')
        self.setGeometry(300, 300, 600, 400)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
            }
        """)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Add title
        title_label = QLabel('Schindler PDF OCR Tool')
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #1565C0;
            margin: 20px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Add description
        info_label = QLabel('Select PDF files for OCR text recognition')
        info_label.setStyleSheet('color: #666666;')
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        # Create button container
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(15)

        # Add select single file button
        self.select_file_btn = QPushButton('Select Single PDF File')
        self.select_file_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.select_file_btn.clicked.connect(self.select_file)
        button_layout.addWidget(self.select_file_btn)

        # Add select directory button
        self.select_dir_btn = QPushButton('Select PDF Directory')
        self.select_dir_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        self.select_dir_btn.clicked.connect(self.select_directory)
        button_layout.addWidget(self.select_dir_btn)

        layout.addWidget(button_container)

        # 添加进度条和状态标签到主布局的中间位置
        progress_container = QWidget()
        progress_layout = QVBoxLayout(progress_container)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2196F3;
                border-radius: 5px;
                text-align: center;
                height: 25px;
                font-size: 12px;
                background-color: #E3F2FD;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
        """)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)  # 显示进度文本
        self.progress_bar.setFormat("%p%")  # 显示百分比
        self.progress_bar.hide()  # 默认隐藏
        progress_layout.addWidget(self.progress_bar)

        # 状态标签
        self.status_label = QLabel('')
        self.status_label.setStyleSheet("""
            color: #666666;
            font-size: 12px;
            min-height: 20px;
            margin-top: 5px;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.status_label)

        # 将进度容器添加到主布局
        layout.addWidget(progress_container)

        # Add copyright info
        copyright_label = QLabel('© 2025 Schindler Escalator PDF OCR Tool')
        copyright_label.setStyleSheet("""
            color: #999999;
            font-size: 12px;
        """)
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copyright_label)

    def select_file(self):
        """Select single PDF file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select PDF File",
            "",
            "PDF Files (*.pdf)"
        )
        if file_path:
            self.process_single_file(file_path)

    def select_directory(self):
        """Select directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Directory with PDF Files",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if dir_path:
            self.process_directory(dir_path)

    def open_output_folder(self, file_path=None):
        """Open output folder and select file if specified"""
        try:
            if file_path and os.path.exists(file_path):
                os.system(f'explorer /select,"{file_path}"')
            else:
                os.startfile(self.processor.output_dir)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Warning",
                f"Cannot open output folder: {str(e)}",
                QMessageBox.StandardButton.Ok
            )

    def process_single_file(self, file_path):
        """Process single PDF file"""
        try:
            # 显示进度条和初始状态
            self.progress_bar.show()
            self.progress_bar.setValue(0)
            self.status_label.setText(f"Processing: {os.path.basename(file_path)}")
            
            def update_progress(progress, status):
                # 确保在主线程中更新UI
                self.progress_bar.setValue(progress)
                self.status_label.setText(status)
                # 强制更新UI
                QApplication.processEvents()
            
            output_file = str(Path(self.processor.output_dir) / f"ocr_{Path(file_path).name}")
            success = self.processor.process_single_pdf(
                file_path, 
                output_file,
                progress_callback=update_progress
            )
            
            # 处理完成后的操作
            self.progress_bar.hide()
            if success:
                result = QMessageBox.information(
                    self,
                    "Success",
                    f"File processing completed!\nSaved to: {output_file}\n\nOpen output folder?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                if result == QMessageBox.StandardButton.Yes:
                    self.open_output_folder(output_file)
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Error processing file",
                    QMessageBox.StandardButton.Ok
                )
            
            self.status_label.setText("")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error processing file: {str(e)}",
                QMessageBox.StandardButton.Ok
            )
            self.progress_bar.hide()
            self.status_label.setText("")

    def process_directory(self, dir_path):
        """Process all PDF files in directory"""
        try:
            pdf_files = list(Path(dir_path).glob("*.pdf"))
            if not pdf_files:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "No PDF files found in selected directory!",
                    QMessageBox.StandardButton.Ok
                )
                return

            self.progress_bar.show()
            self.progress_bar.setValue(0)
            total_files = len(pdf_files)
            processed = 0
            last_output_file = None

            for pdf_file in pdf_files:
                self.status_label.setText(f"Processing {processed + 1}/{total_files}: {pdf_file.name}")
                output_file = str(Path(self.processor.output_dir) / f"ocr_{pdf_file.name}")
                
                def update_progress(progress, status):
                    # 计算总体进度
                    total_progress = int((processed * 100 + progress) / total_files)
                    self.progress_bar.setValue(total_progress)
                    self.status_label.setText(f"File {processed + 1}/{total_files}: {status}")
                    QApplication.processEvents()

                if self.processor.process_single_pdf(str(pdf_file), output_file, progress_callback=update_progress):
                    last_output_file = output_file
                processed += 1

            self.progress_bar.hide()
            result = QMessageBox.information(
                self,
                "Success",
                f"Successfully processed {processed} files!\n\nOpen output folder?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if result == QMessageBox.StandardButton.Yes:
                self.open_output_folder(last_output_file if last_output_file else None)
            
            self.status_label.setText("")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error processing directory: {str(e)}",
                QMessageBox.StandardButton.Ok
            )
            self.progress_bar.hide()
            self.status_label.setText("")