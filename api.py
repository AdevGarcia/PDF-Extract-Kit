import time

from app_tools.config import setup_logging
from app_tools.pdf import PDFProcessor
from app_tools.layout_analysis import LayoutAnalyzer
from app_tools.formula_analysis import FormulaProcessor
from app_tools.ocr_analysis import OCRProcessor
from app_tools.table_analysis import TableProcessor

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

logger = setup_logging('app')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info('Started!')
start = time.time()
## ======== model init ========##
analyzer = LayoutAnalyzer()
formulas = FormulaProcessor()
ocr_processor = OCRProcessor(show_log=True)
# table_processor = TableProcessor()
logger.info(f'Model init done in {int(time.time() - start)}s!')
## ======== model init ========##

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/process-pdf/")
async def process_pdf(file: UploadFile = File(...), batch_size: int = 128, num_workers: int = 32):
    # Leer el contenido del PDF
    pdf_processor = PDFProcessor()
    all_pdfs = pdf_processor.check_pdf(file.filename)

    doc_layout_result = []

    for idx, single_pdf, img_list in pdf_processor.process_all_pdfs(all_pdfs):

        doc_layout_result = analyzer.detect_layout(img_list)
        doc_layout_result = formulas.detect_recognize_formulas(img_list, doc_layout_result, batch_size, num_workers)
        doc_layout_result = ocr_processor.recognize_ocr(img_list, doc_layout_result)
        # doc_layout_result = table_processor.recognize_tables(img_list, doc_layout_result)

    # result = {
    #     "result": doc_layout_result
    # }

    return JSONResponse(content=doc_layout_result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
