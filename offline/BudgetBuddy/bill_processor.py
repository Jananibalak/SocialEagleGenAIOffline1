import os
import re
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import platform

# PDF processing
from PyPDF2 import PdfReader

# Image processing
from PIL import Image
import pytesseract

# Configure Tesseract path for Windows
if platform.system() == 'Windows':
    # Try common installation paths
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Users\Admin\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
    ]
    
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break


class BillProcessor:
    """Process bills from PDFs and images with OCR"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.png', '.jpg', '.jpeg']
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from PDF or image file"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_ext in ['.png', '.jpg', '.jpeg']:
            return self._extract_from_image(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _extract_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""
    
    def _extract_from_image(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            print(f"Error extracting image text: {e}")
            return ""
    
    def extract_bill_info(self, text: str, filename: str) -> Dict[str, Any]:
        """Extract structured information from bill text"""
        bill_info = {
            'filename': filename,
            'merchant': self._extract_merchant(text),
            'amount': self._extract_amount(text),
            'date': self._extract_date(text),
            'category': self._categorize_bill(text),
            'items': self._extract_items(text),
            'raw_text': text
        }
        return bill_info
    
    def _extract_merchant(self, text: str) -> str:
        """Extract merchant name from bill"""
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 3 and not line.replace('.', '').replace(',', '').isdigit():
                if not any(word in line.lower() for word in ['receipt', 'invoice', 'bill', 'page', 'date']):
                    return line
        return "Unknown Merchant"
    
    def _extract_amount(self, text: str) -> float:
        """Extract total amount from bill"""
        patterns = [
            r'(?:total|amount due|balance|grand total)[:\s]*\$?\s*(\d+[,\d]*\.?\d*)',
            r'\$\s*(\d+[,\d]*\.\d{2})',
            r'(\d+[,\d]*\.\d{2})\s*(?:total|due)',
        ]
        
        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount = float(match.replace(',', ''))
                    amounts.append(amount)
                except ValueError:
                    continue
        
        return max(amounts) if amounts else 0.0
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from bill"""
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return datetime.now().strftime("%Y-%m-%d")
    
    def _categorize_bill(self, text: str) -> str:
        """Categorize bill based on content"""
        text_lower = text.lower()
        
        categories = {
            'Groceries': ['grocery', 'supermarket', 'walmart', 'target', 'kroger', 'whole foods', 'trader joe'],
            'Utilities': ['electric', 'utility', 'water', 'gas', 'power', 'energy'],
            'Internet/Phone': ['internet', 'phone', 'mobile', 'verizon', 'at&t', 't-mobile', 'comcast', 'spectrum'],
            'Dining': ['restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'dining', 'food'],
            'Transportation': ['gas', 'fuel', 'uber', 'lyft', 'parking', 'metro', 'transit'],
            'Healthcare': ['pharmacy', 'medical', 'doctor', 'hospital', 'clinic', 'cvs', 'walgreens'],
            'Entertainment': ['movie', 'theater', 'netflix', 'spotify', 'gaming', 'concert'],
            'Shopping': ['amazon', 'store', 'retail', 'clothing', 'apparel'],
            'Insurance': ['insurance', 'premium', 'policy'],
            'Rent/Mortgage': ['rent', 'mortgage', 'lease', 'housing'],
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return 'Other'
    
    def _extract_items(self, text: str) -> list:
        """Extract line items from bill"""
        items = []
        lines = text.split('\n')
        
        for line in lines:
            match = re.search(r'(.+?)\s+\$?\s*(\d+\.\d{2})', line)
            if match:
                item_name = match.group(1).strip()
                item_price = match.group(2)
                if len(item_name) > 2 and len(item_name) < 50:
                    items.append({
                        'name': item_name,
                        'price': float(item_price)
                    })
        
        return items[:10]
