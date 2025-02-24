# -*- mode: python ; coding: utf-8 -*-
import os
import site
import ocrmypdf

# 获取 ocrmypdf 模块的实际路径
ocrmypdf_path = os.path.dirname(ocrmypdf.__file__)

# 文件信息
file_version = '0.0.1'
product_name = 'PDF OCR'
copyright_info = 'xuyu1'

# 创建版本信息文件
version_info = '''
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(0, 0, 1, 0),
    prodvers=(0, 0, 1, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'FileVersion', u'0.0.1'),
           StringStruct(u'ProductName', u'PDF OCR'),
           StringStruct(u'ProductVersion', u'0.0.1'),
           StringStruct(u'CompanyName', u'Schindler'),
           StringStruct(u'Copyright', u'xuyu1'),
           StringStruct(u'FileDescription', u'PDF OCR Tool')])
      ])
  ]
)
'''

# 将版本信息写入临时文件
with open('version_info.txt', 'w') as f:
    f.write(version_info)

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('input', 'input'),         
        ('output', 'output'),
        # 添加 ocrmypdf 数据文件，使用实际路径
        (ocrmypdf_path, 'ocrmypdf'),
    ],
    hiddenimports=[
        # PyQt6 相关
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        'PyQt6.QtPrintSupport',
        
        # OCR 相关
        'pdf_ocr_processor',
        'ocrmypdf',
        'ocrmypdf._sync',
        'ocrmypdf._pipeline',
        'ocrmypdf.helpers',
        'ocrmypdf.api',
        'ocrmypdf.cli',
        'ocrmypdf.exceptions',
        'ocrmypdf.executor',
        'ocrmypdf.hocr',
        'ocrmypdf.leptonica',
        'ocrmypdf.optimize',
        'ocrmypdf.pdfa',
        'ocrmypdf.pdfinfo',
        'ocrmypdf.quality',
        'ocrmypdf.subprocess',
        'ocrmypdf.workaround',
        'reportlab',
        'reportlab.pdfbase',
        'reportlab.pdfgen',
        'img2pdf',
        'pdf2image',
        'PIL',
        'PIL._imaging',
        'PIL.Image',
        
        # PDF 处理相关
        'pdfminer',
        'pdfminer.high_level',
        'pikepdf',
        'pikepdf._core',
        'pikepdf.models',
        'pikepdf.objects',
        
        # 其他依赖
        'subprocess',
        'pathlib',
        'glob',
        'webbrowser',
        'tempfile',
        'urllib.request',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PDF_OCR',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 设为True以便查看错误信息
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',  # 添加版本信息
)

# 清理临时文件
os.remove('version_info.txt') 