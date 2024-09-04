import os
import json

from magic_pdf.pipe.UNIPipe import UNIPipe
from magic_pdf.rw.DiskReaderWriter import DiskReaderWriter

import magic_pdf.model as model_config
model_config.__use_inside_model__ = True

current_script_dir = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    pdf_path = "1706.03762.pdf"
    model_path = 'output/1706.03762.json'
    output_dir = 'output'

    pdf_path = os.path.join(current_script_dir, pdf_path)
    model_path = os.path.join(current_script_dir, model_path)
    output_dir = os.path.join(current_script_dir, output_dir)
    filename = pdf_path.split('.')[0]

    local_image_dir = os.path.join(current_script_dir, f'{output_dir}/images')
    image_dir = str(os.path.basename(local_image_dir))

    image_writer = DiskReaderWriter(local_image_dir)

    pdf_bytes = open(pdf_path, "rb").read()

    pipe = UNIPipe(
        pdf_bytes=pdf_bytes,
        jso_useful_key={
            "_pdf_type": "",
            "model_list": json.loads(open(model_path, "r", encoding="utf-8").read())
        },
        image_writer=image_writer,
        is_debug=True
    )

    pipe.pipe_classify()
    pipe.pipe_parse()
    md_content = pipe.pipe_mk_markdown(image_dir, drop_mode="none")
    content_list = pipe.pipe_mk_uni_format(image_dir)

    md_writer = DiskReaderWriter(output_dir)
    md_writer.write(content=md_content, path=f"{filename}.md")
    md_writer.write(content=json.dumps(pipe.pdf_mid_data, ensure_ascii=False, indent=4), path=f"{filename}_mid.json")
    md_writer.write(content=json.dumps(content_list, ensure_ascii=False, indent=4), path=f"{filename}_content.json")
