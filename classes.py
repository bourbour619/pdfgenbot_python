import glob
import os
from abc import ABC, abstractmethod
from os import environ, path
from time import sleep

import docx2pdf
import img2pdf
#import pdf2docx
import pdf2image
from PyPDF2 import PdfFileReader, PdfFileWriter


class Activity :
    id = ''
    root = ''
    step = 0
    known = ['pdf', 'doc', 'docx', 'jpeg', 'jpg', 'png']
    type = ''
    current = ''
    queue = []
    def __init__(self) -> None:
        pass

    def init(self, id):
        self.id = id
        self.root = path.join(path.join(path.dirname(__file__),'files'), self.id)
        self.step = 1
        if self.first() :
            self.env()
        else:
            os.system(f'rm -f {self.root}/*')

    def first(self) -> bool:
        return not path.isdir(self.root)

    def env(self) -> None:
        os.mkdir(self.root)

    def log(self) -> list:
        final = os.listdir().sort()
        if final != self.queue.sort():
            self.queue = final
        return self.queue

    def add(self, name) -> str:
        t = path.join(self.root, name)
        self.queue.append(name)
        self.current = self.queue[len(self.queue) - 1]
        return t
    
    def remove(self, name=None) -> None:
        target = path.join(self.root, self.current)
        if name:
            target = path.join(self.root, name)
        if path.isfile(target):
                os.remove(target)
            

    def flush(self) -> None:
        os.system(f'rm -rf {self.root}')
        self.id = ''
        self.root = ''


class ConvertStrategy(ABC):

    @abstractmethod
    def convert(self, path: str, no: int) -> str:
        pass


class WordToPdf(ConvertStrategy):

    def convert(self,path, no = 1) -> str:        
        pdfPath = path.split('.')[0] + '.pdf'
        docx2pdf.convert(path, pdfPath)
        return pdfPath


class PdfToWord(ConvertStrategy):

    def convert(self,path, no = 1) -> str:
        docxPath = path.split('.')[0] + '.docx'
        pdf2docx.parse(path, docxPath)
        return docxPath

class ImageToPdf(ConvertStrategy):

    def convert(self, path, no = 1) -> str:
        pdfPath = path.split('.')[0] + '.pdf'
        if no == 1:
            with open(pdfPath, 'wb', encoding='utf-8') as p :
                p.write(img2pdf.convert(path))
        else:
            ext = path.split('.')[1]
            globPath = os.path.dirname(path)
            allPaths = glob.glob(f'{globPath}/*.{ext}')
            with open(pdfPath, 'wb', encoding='utf-8') as p :
                p.write(img2pdf.convert(allPaths))
        return pdfPath

class PdfToImage(ConvertStrategy):
    
    def covnert(self, path, no = 1):
        imagePath = os.path.dirname(path)
        images = pdf2image.convert_from_path(path)
        for i in range(len(images)):
            images[i].save(f'{imagePath}/{str(i)}.jpg', 'JPEG')


def merge_pdfs_func(paths) -> str:
    outPath = f'{os.path.dirname(paths[0])}/merged.pdf'
    pdf_writer = PdfFileWriter()

    for path in paths:
        pdf_reader = PdfFileReader(path)
        for page in range(pdf_reader.getNumPages()):
            pdf_writer.addPage(pdf_reader.getPage(page))

    with open(outPath, 'wb', encoding='utf-8') as out:
        pdf_writer.write(out)

    return outPath
