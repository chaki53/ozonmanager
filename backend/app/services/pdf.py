from weasyprint import HTML

def render_pdf(html: str, out_path: str):
    HTML(string=html).write_pdf(out_path)
    return out_path
