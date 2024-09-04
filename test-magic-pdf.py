from pathlib import Path
import json

from magic_pdf.pipe.UNIPipe import UNIPipe
from magic_pdf.rw.DiskReaderWriter import DiskReaderWriter

import magic_pdf.model as model_config
model_config.__use_inside_model__ = True

def post_process(pdf: str, output: str = 'output'):

    current_script_dir = Path(__file__).parent

    pdf_path = Path(pdf)
    filename = str(pdf_path.stem)
    pdf_path = current_script_dir / pdf_path
    output_dir = current_script_dir / output
    model_path = output_dir / f"{filename}.json"
    image_dir = output_dir / 'images'

    pdf_bytes = open(pdf_path, "rb").read()

    image_writer = DiskReaderWriter(image_dir)
    md_writer = DiskReaderWriter(output_dir)

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
    md_content = pipe.pipe_mk_markdown(img_parent_path='images', drop_mode="none")
    content_list = pipe.pipe_mk_uni_format(img_parent_path='images')

    md_writer.write(content=md_content, path=f"{filename}.md")
    md_writer.write(content=json.dumps(pipe.pdf_mid_data, ensure_ascii=False, indent=4), path=f"{filename}_mid.json")
    md_writer.write(content=json.dumps(content_list, ensure_ascii=False, indent=4), path=f"{filename}_content.json")


if __name__ == '__main__':

    post_process(pdf="1706.03762.pdf", output='output')
