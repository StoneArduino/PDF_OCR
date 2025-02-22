# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path

def setup_environment():
    """设置运行环境"""
    try:
        # 创建必要的目录
        os.makedirs('input', exist_ok=True)
        os.makedirs('output', exist_ok=True)
        return True
    except Exception as e:
        print(f"Error setting up environment: {str(e)}")
        return False

def main():
    try:
        # 设置环境
        if not setup_environment():
            return 1

        # 创建 QApplication
        from PyQt6.QtWidgets import QApplication, QMessageBox
        app = QApplication([])
        
        try:
            # 导入和检查依赖
            from pdf_ocr_processor import check_dependencies, PDFProcessorGUI
            check_dependencies()
            
            # 创建并显示窗口
            window = PDFProcessorGUI()
            window.show()
            return app.exec()
            
        except ImportError as e:
            QMessageBox.critical(
                None,
                "Error",
                f"Failed to load required modules: {str(e)}\n\nPlease reinstall the application.",
                QMessageBox.StandardButton.Ok
            )
            return 1
        except Exception as e:
            QMessageBox.critical(
                None,
                "Error",
                f"Application error: {str(e)}",
                QMessageBox.StandardButton.Ok
            )
            return 1
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 