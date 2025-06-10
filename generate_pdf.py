import sys
import textwrap

from pdfrw import PdfWriter
from pdfrw.objects.pdfname import PdfName
from pdfrw.objects.pdfstring import PdfString
from pdfrw.objects.pdfdict import PdfDict
from pdfrw.objects.pdfarray import PdfArray

def create_javascript_action(js_code):
  action = PdfDict()
  action.S = PdfName.JavaScript
  action.JS = js_code
  return action
  
def create_pdf_page(width, height):
  page = PdfDict()
  page.Type = PdfName.Page
  page.MediaBox = PdfArray([0, 0, width, height])

  page.Resources = PdfDict()
  page.Resources.Font = PdfDict()
  page.Resources.Font.F1 = PdfDict()
  page.Resources.Font.F1.Type = PdfName.Font
  page.Resources.Font.F1.Subtype = PdfName.Type1
  page.Resources.Font.F1.BaseFont = PdfName.Courier
  
  return page

def create_form_field(name, x, y, width, height, value="", field_type=PdfName.Tx):
  annotation = PdfDict()
  annotation.Type = PdfName.Annot
  annotation.Subtype = PdfName.Widget
  annotation.FT = field_type
  annotation.Ff = 2
  annotation.Rect = PdfArray([x, y, x + width, y + height])
  annotation.T = PdfString.encode(name)
  annotation.V = PdfString.encode(value)

  annotation.BS = PdfDict()
  annotation.BS.W = 0

  appearance = PdfDict()
  appearance.Type = PdfName.XObject
  appearance.SubType = PdfName.Form
  appearance.FormType = 1
  appearance.BBox = PdfArray([0, 0, width, height])
  appearance.Matrix = PdfArray([1.0, 0.0, 0.0, 1.0, 0.0, 0.0])

  return annotation

def create_text_object(x, y, size, text_content):
  return f"""
  BT
  /F1 {size} Tf
  {x} {y} Td ({text_content}) Tj
  ET
  """

def create_button_field(name, x, y, width, height, display_value):
  button = create_form_field(name, x, y, width, height, field_type=PdfName.Btn)
  button.AA = PdfDict()
  button.Ff = 65536
  button.MK = PdfDict()
  button.MK.BG = PdfArray([0.90])
  button.MK.CA = display_value
  return button

def create_key_control_buttons(key_definitions):
  buttons = []
  for key_def in key_definitions:
    name = key_def["name"] + "_button"
    key_char = key_def["key"]
    button = create_button_field(name, key_def["x"], key_def["y"], key_def["width"], key_def["height"], key_def["name"])
    button.AA = PdfDict()
    button.AA.D = create_javascript_action(f"key_down(\\'{key_char}\\')")
    button.AA.U = create_javascript_action(f"key_up(\\'{key_char}\\')")
    buttons.append(button)
  return buttons

if __name__ == "__main__":
  with open(sys.argv[1]) as f:
    javascript_code = f.read()

  page_width = 360
  page_height = 200
  display_scale = 2

  pdf_writer = PdfWriter()
  pdf_page = create_pdf_page(page_width * display_scale - 8, page_height * display_scale + 220)
  pdf_page.AA = PdfDict()
  pdf_page.AA.O = create_javascript_action("try {"+javascript_code+"} catch (e) {app.alert(e.stack || e)}");

  form_fields = []
  for i in range(0, page_height):
    field = create_form_field(f"field_{i}", 0, i * display_scale + 220, page_width * display_scale - 8, display_scale, "")
    form_fields.append(field)
  for i in range(0, 25):
    field = create_form_field(f"console_{i}", 8, 8 + i * 8, 300, 8, "")
    form_fields.append(field)

  input_field = create_form_field(f"key_input", 450, 64, 150, 64, "Type here for keyboard controls.")
  input_field.AA = PdfDict()
  input_field.AA.K = create_javascript_action("key_pressed(event.change)")
  form_fields.append(input_field)

  form_fields += create_key_control_buttons([
    {"name": "<", "key": "a", "x": 320, "y": 102, "width": 30, "height": 30},
    {"name": "^", "key": "w", "x": 358, "y": 140, "width": 30, "height": 30},
    {"name": "v", "key": "s", "x": 358, "y": 102, "width": 30, "height": 30},
    {"name": ">", "key": "d", "x": 396, "y": 102, "width": 30, "height": 30},
    {"name": "esc", "key": "q", "x": 320, "y": 140, "width": 30, "height": 30},
    {"name": "use", "key": "e", "x": 396, "y": 140, "width": 30, "height": 30},
    {"name": "enter", "key": "z", "x": 320, "y": 64, "width": 30, "height": 30},
    {"name": "fire", "key": " ", "x": 358, "y": 64, "width": 68, "height": 30},
  ])

  pdf_page.Contents = PdfDict()
  pdf_page.Contents.stream = "\n".join([
    create_text_object(320, 190, 24, "DoomPDF"),
    create_text_object(450, 162, 12, "Controls:"),
    create_text_object(450, 148, 8, "WASD, q = esc, z = enter, e = use, space = fire"),
    create_text_object(450, 136, 8, "shift+WASD = sprint, m = map, 1-7 = weapons"),
    create_text_object(320, 34, 8, "Upload custom WAD files at: https://doompdf.pages.dev/"),
    create_text_object(320, 22, 8, "Source code: https://github.com/ading2210/doompdf"),
    create_text_object(320, 10, 8, "Note: This PDF only works in Chromium-based browsers.")
  ])

  pdf_page.Annots = PdfArray(form_fields)
  pdf_writer.addpage(pdf_page)
  pdf_writer.write(sys.argv[2])

