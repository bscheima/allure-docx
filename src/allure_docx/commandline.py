import subprocess
from allure_docx import process
import os
import click
import sys
import shutil
import ast


class PythonLiteralOption(click.Option):
    def type_cast_value(self, ctx, value):
        try:
            return ast.literal_eval(value)
        except:
            raise click.BadParameter(value)


template_dir = None
if getattr(sys, "frozen", False):
    # running in a bundle
    template_dir = sys._MEIPASS
else:
    # running live
    template_dir = os.path.dirname(os.path.realpath(__file__))

cwd = os.getcwd()


@click.command()
@click.argument("alluredir")
@click.argument("output")
@click.option(
    "--template",
    default=None,
    help="Path (absolute or relative) to a custom docx template file with styles",
)
@click.option(
    "--config",
    default="standard",
    help="Configuration for the docx report. Options are: standard, standard_on_fail, no_trace, compact. Alternatively path to custom .ini configuration file (see documentation).",
)
@click.option(
    "--pdf",
    is_flag=True,
    help="Try to generate a pdf file from created docx using soffice or OfficeToPDF (needs MS Word installed)",
)
@click.option("--title", default=None, help="Custom report title")
@click.option("--logo", default=None, help="Path to custom report logo image")
@click.option(
    "--logo-height",
    default=None,
    help="Image height in centimeters. Width is scaled to keep aspect ratio",
)
def main(alluredir, output, template, pdf, title, logo, logo_height, config):
    """alluredir: Path (relative or absolute) to alluredir folder with test results

    output: Path (relative or absolute) with filename for the generated docx file"""
    if not os.path.isabs(alluredir):
        alluredir = os.path.join(cwd, alluredir)
    if not os.path.isabs(output):
        output = os.path.join(cwd, output)
    if template is None:
        template = os.path.join(template_dir, "template.docx")
    else:
        if not os.path.isabs(template):
            template = os.path.join(cwd, template)
    print("Template: {}".format(template))

    if logo_height is not None:
        logo_height = float(logo_height)
    process.run(alluredir, template, output, title, logo, logo_height, config)

    if pdf:
        filepath, ext = os.path.splitext(output)
        output_pdf = filepath + ".pdf"
        officetopdf = shutil.which("OfficeToPDF")
        soffice = shutil.which("soffice")

        if officetopdf is not None:
            print("Found OfficeToPDF, using it. Make sure you have MS Word installed.")
            proc = subprocess.run(
                [officetopdf, "/bookmarks", "/print", output, output_pdf],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            print(proc.stdout.decode())
            sys.exit(proc.returncode)
        elif soffice is not None:
            result_dir = os.path.dirname(output)
            doc_path = output
            subprocess.call(["soffice", "--convert-to", "pdf", "--outdir", result_dir, doc_path])
            return doc_path
        else:
            print("Could not find neither OfficeToPDF nor soffice. Not generating PDF.")
            sys.exit(1)


if __name__ == "__main__":
    main()
