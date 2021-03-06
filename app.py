from flask import request, redirect, render_template
from flask import Flask
import PyPDF2
import requests
import boto3

app = Flask(__name__)


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


def write_file(filename, file_data):
    with open(filename, 'w') as file:
        file.write(file_data)


def read_file(file):
    read_pdf = PyPDF2.PdfFileReader(file)
    number_of_pages = read_pdf.getNumPages()
    file_len = 1000
    counter = 1

    page_content = ''
    for page in range(number_of_pages):
        raw_page_content = read_pdf.getPage(page)
        page_content += raw_page_content.extractText()

    file_data_list = [page_content[i:i + file_len] for i in range(0, len(page_content), file_len)]
    for file_data in file_data_list:
        filename = f'{counter}.txt'
        write_file(filename, file_data)
        counter += 1

    return page_content


def post_to_aws(text):
    return True
    # todo

    client = boto3.client('polly')
    aws_url = 'https://a.w.s'
    result = requests.post(aws_url, data=text)

    if result.status_code in (200, 201):
        return True

    return False


if __name__ == "__main__":
    app.run()
