from docx import Document
from docx2pdf import convert
import re

def interpolate_data(match_obj):
    match = match_obj.group(1)
    print(match)
    return match

src_file = "/Volumes/Work/resume/pure_frontend/Resume-Michael-Chilelli.docx"
dest_file = "/Volumes/Work/resume/pure_frontend/~temp.docx"

document = Document(src_file)
for (index, paragraph) in enumerate(document.paragraphs):
    for run in paragraph.runs:
        if re.match("{(.*?)}", run.text):
            run.text = re.sub("{(.*?)}", interpolate_data, run.text)


document.save(dest_file)
convert(dest_file)