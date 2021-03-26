from flask import request, redirect, render_template
from flask import Flask

import os
import PyPDF2
import requests
from dotenv import load_dotenv

from resources.upload import UploadFile

app = Flask(__name__, template_folder='templates')


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    page_dict = {
        'status': 'Fail',
        'page': 'index'
    }
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        # if there is no file
        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            page_dict['page'] = 'processed'
            page_content = read_file(file)
            aws_processed = post_to_aws(page_content)
            if aws_processed:
                page_dict['status'] = 'Success'
                return render_template('index.html', **page_dict)

            return render_template('index.html', **page_dict)

    return render_template('index.html', **page_dict)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ('pdf',)


def read_file(file):
    read_pdf = PyPDF2.PdfFileReader(file)
    page = read_pdf.getPage(0)
    page_content = page.extractText()

    return page_content


def post_to_aws(text):
    return True
    aws_url = os.environ.get('AWS_URL')
    result = requests.post(aws_url, data=text)

    if result.status_code in (200, 201):
        return True

    return False


if __name__ == '__main__':
    load_dotenv()
    app_host = os.environ.get('APP_HOST')
    app_port = os.environ.get('APP_PORT')

    app.add_url_rule('/upload', view_func=UploadFile.as_view('post'))

    app.run(host=app_host, port=app_port)
