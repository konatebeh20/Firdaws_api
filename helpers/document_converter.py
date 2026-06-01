import os
import subprocess
from logger.logger_config import get_logger

logger = get_logger()

# Chemin vers LibreOffice (adapter si nécessaire)
LIBREOFFICE_PATHS = [
    r'C:\Program Files\LibreOffice\program\soffice.exe',
    r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
    'soffice',  # Linux/Mac
]

def get_libreoffice():
    for path in LIBREOFFICE_PATHS:
        if os.path.exists(path) or path == 'soffice':
            return path
    return None

CONVERTIBLE = {'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'odt', 'ods', 'odp'}

def convert_to_pdf(input_path: str, output_dir: str) -> str | None:
    """
    Convertit un fichier Office en PDF via LibreOffice.
    Retourne le chemin du PDF généré, ou None si échec.
    """
    ext = input_path.rsplit('.', 1)[-1].lower()
    if ext not in CONVERTIBLE:
        return None

    soffice = get_libreoffice()
    if not soffice:
        logger.error("LibreOffice introuvable — conversion impossible")
        return None

    try:
        result = subprocess.run(
            [soffice, '--headless', '--convert-to', 'pdf', '--outdir', output_dir, input_path],
            timeout=60,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.error(f"Erreur LibreOffice: {result.stderr}")
            return None

        # Le PDF généré a le même nom de base avec extension .pdf
        basename = os.path.splitext(os.path.basename(input_path))[0]
        pdf_path = os.path.join(output_dir, basename + '.pdf')

        if os.path.exists(pdf_path):
            logger.info(f"Conversion réussie: {pdf_path}")
            return pdf_path

        return None

    except subprocess.TimeoutExpired:
        logger.error("Timeout lors de la conversion LibreOffice")
        return None
    except Exception as e:
        logger.error(f"Erreur conversion: {str(e)}")
        return None