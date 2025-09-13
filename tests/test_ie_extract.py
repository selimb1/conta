import sys
sys.path.insert(0, 'services/api')

from app.utils.ie_extract import extract_fields
import pytest

@pytest.mark.parametrize('letter', ['A', 'B', 'C', 'M'])
def test_detect_invoice_letter(letter):
    tokens = ['Factura', letter, '0001-00000001']
    campos = extract_fields({'tokens': tokens})
    assert campos['tipo'] == letter
