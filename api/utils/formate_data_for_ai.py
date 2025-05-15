import io
import os
import logging
import pandas as pd
import camelot
import tabula
import pdfplumber
from pdf2image import convert_from_bytes, convert_from_path
import pytesseract
import numpy as np
import cv2

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFTableExtractor:
    """Extract tables from PDFs (both text-based tables and image-based tables)"""
    
    def __init__(self, file):
        """Initialize the PDF table extractor with a PDF file or file-like object"""
        if isinstance(file, bytes):
            # If the file is in bytes, we can handle it directly
            self.file = io.BytesIO(file)
        elif isinstance(file, io.IOBase):
            # If the file is a file-like object (e.g., uploaded file), use it directly
            self.file = file
        elif isinstance(file, str) and os.path.exists(file):
            # If a valid file path is provided
            self.file = file
        else:
            raise ValueError("Invalid file provided. Please provide a file or file-like object.")
        
        self.extracted_data = []
        self.tables_count = 0

    def extract_all_tables(self):
        """Extract all tables from the PDF using multiple methods"""
        logger.info(f"Starting extraction of tables from the provided file")
        
        # Try different extraction methods in order of preference
        self._extract_with_camelot()  # Best for text-based tables
        
        # If no tables were found with Camelot, try other methods
        if self.tables_count == 0:
            self._extract_with_tabula()
        
        # If still no tables, or additional tables might be in images, extract from images
        self._extract_from_images()
        
        # Use pdfplumber as last resort for simple tables
        if self.tables_count == 0:
            self._extract_with_pdfplumber()
        
        logger.info(f"Extracted {self.tables_count} tables in total")
        return self.extracted_data
    
    def _extract_with_camelot(self):
        """Extract tables using Camelot library (good for text-based tables)"""
        try:
            logger.info("Attempting table extraction with Camelot")
            # Try with lattice method first (for tables with borders)
            tables_lattice = camelot.read_pdf(self.file, pages='all', flavor='lattice')
            
            # Then try with stream method (for tables without clear borders)
            tables_stream = camelot.read_pdf(self.file, pages='all', flavor='stream')
            
            camelot_tables = list(tables_lattice) + list(tables_stream)
            
            # Filter out low-accuracy tables
            camelot_tables = [table for table in camelot_tables if table.accuracy > 80]
            
            for i, table in enumerate(camelot_tables):
                df = table.df
                # Clean data
                df = self._clean_dataframe(df)
                
                if not df.empty:
                    table_data = {
                        "table_id": f"camelot_table_{i+1}",
                        "page_number": table.page,
                        "extraction_method": "camelot",
                        "accuracy_score": table.accuracy,
                        "data": df.to_dict(orient='records'),
                        "headers": df.columns.tolist(),
                        "shape": df.shape
                    }
                    self.extracted_data.append(table_data)
                    self.tables_count += 1
            
            logger.info(f"Camelot extracted {len(camelot_tables)} tables")
        except Exception as e:
            logger.warning(f"Camelot extraction failed: {str(e)}")
    
    def _extract_with_tabula(self):
        """Extract tables using Tabula library"""
        try:
            logger.info("Attempting table extraction with Tabula")
            tabula_tables = tabula.read_pdf(self.file, pages='all', multiple_tables=True)
            
            for i, df in enumerate(tabula_tables):
                # Clean data
                df = self._clean_dataframe(df)
                
                if not df.empty:
                    table_data = {
                        "table_id": f"tabula_table_{i+1}",
                        "extraction_method": "tabula",
                        "data": df.to_dict(orient='records'),
                        "headers": df.columns.tolist(),
                        "shape": df.shape
                    }
                    self.extracted_data.append(table_data)
                    self.tables_count += 1
            
            logger.info(f"Tabula extracted {len(tabula_tables)} tables")
        except Exception as e:
            logger.warning(f"Tabula extraction failed: {str(e)}")
    
    def _extract_with_pdfplumber(self):
        """Extract tables using pdfplumber library"""
        try:
            logger.info("Attempting table extraction with pdfplumber")
            table_count = 0
            
            with pdfplumber.open(self.file) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    
                    for i, table_data in enumerate(tables):
                        # Convert to DataFrame
                        if table_data and len(table_data) > 0:
                            headers = table_data[0]
                            data = table_data[1:]
                            
                            # Check if headers are valid
                            if all(h is None or h == '' for h in headers):
                                # Generate column names if headers are empty
                                headers = [f"Column_{i}" for i in range(len(table_data[0]))]
                            
                            df = pd.DataFrame(data, columns=headers)
                            df = self._clean_dataframe(df)
                            
                            if not df.empty:
                                table_data = {
                                    "table_id": f"pdfplumber_table_p{page_num+1}_{i+1}",
                                    "page_number": page_num + 1,
                                    "extraction_method": "pdfplumber",
                                    "data": df.to_dict(orient='records'),
                                    "headers": df.columns.tolist(),
                                    "shape": df.shape
                                }
                                self.extracted_data.append(table_data)
                                table_count += 1
                                self.tables_count += 1
            
            logger.info(f"PDFPlumber extracted {table_count} tables")
        except Exception as e:
            logger.warning(f"PDFPlumber extraction failed: {str(e)}")
    
    def _extract_from_images(self):
        """Extract tables from PDF pages by converting to images and using OCR"""
        try:
            logger.info("Attempting table extraction from PDF images")
            # Convert PDF to images
            pdf_data = self.file.read()
            images = convert_from_bytes(pdf_data)
            
            for page_num, image in enumerate(images):
                # Process each page as an image
                image_np = np.array(image)
                
                # Detect table boundaries
                tables_coordinates = self._detect_table_boundaries(image_np)
                
                for i, coords in enumerate(tables_coordinates):
                    # Extract the table region
                    x, y, w, h = coords
                    table_image = image_np[y:y+h, x:x+w]
                    
                    # Extract text from the table image using OCR
                    df = self._extract_table_with_ocr(table_image)
                    
                    if df is not None and not df.empty:
                        table_data = {
                            "table_id": f"image_table_p{page_num+1}_{i+1}",
                            "page_number": page_num + 1,
                            "extraction_method": "image_ocr",
                            "data": df.to_dict(orient='records'),
                            "headers": df.columns.tolist(),
                            "shape": df.shape,
                            "coordinates": {"x": x, "y": y, "width": w, "height": h}
                        }
                        self.extracted_data.append(table_data)
                        self.tables_count += 1
            
            logger.info(f"Image-based extraction completed")
        except Exception as e:
            logger.warning(f"Image-based extraction failed: {str(e)}")
    
    def _detect_table_boundaries(self, image):
        """Detect table boundaries in an image using OpenCV"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 2)
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
        horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        table_mask = cv2.add(horizontal_lines, vertical_lines)
        contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_size = 5000
        table_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_size]
        table_boundaries = [cv2.boundingRect(cnt) for cnt in table_contours]
        return table_boundaries
    
    def _extract_table_with_ocr(self, table_image):
        """Extract table data from an image using OCR"""
        text = pytesseract.image_to_string(table_image, config='--psm 6')
        lines = text.splitlines()
        table_data = []
        
        for line in lines:
            columns = line.split(r'\s{2,}', line.strip())  # Split by multiple spaces
            table_data.append(columns)
        
        df = pd.DataFrame(table_data)
        return df if not df.empty else None
    
    def _clean_dataframe(self, df):
        """Clean up extracted dataframe (e.g., remove empty rows or columns and mark empty cells)"""
        
        # Drop rows and columns that are completely empty
        df = df.dropna(how="all", axis=0)  # Drop fully empty rows
        df = df.dropna(how="all", axis=1)  # Drop fully empty columns

        # Strip whitespace from string cells
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

        # Replace empty strings or whitespace-only strings with "EMPTY CELL"
        df.replace(r'^\s*$', 'EMPTY CELL', regex=True, inplace=True)

        # Replace actual NaN values with "EMPTY CELL"
        df.fillna('EMPTY CELL', inplace=True)

        return df

