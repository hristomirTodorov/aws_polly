from abc import ABC

from flask import request, redirect, render_template
from flask.views import View


class UploadFile(View, ABC):
    methods = ['GET', 'POST']

    @classmethod
    def post(cls):
        print('kor')
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
