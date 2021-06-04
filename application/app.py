from flask import Flask, flash, redirect, url_for, request
from werkzeug.utils import secure_filename
import os
import service

UPLOAD_FOLDER = './data/data'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xls', 'xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/init')
def init():
    res = {
        'code': 400,
        'msg': 'Failure',
        'data': {}
    }
    try:
        data_info = service.read_csv('./data/data_info.csv')
        name = list(data_info['name'])
        res['data']['name'] = name
        res['code'] = 200
        res['msg'] = 'success'
    except Exception as e:
        res['msg'] = str(e)
    return res


@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload_file'))
            # return 'success'
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


if __name__ == '__main__':
    app.run()

'''
import pandas as pd
data = pd.DataFrame()
data['name'] = ['graphdata(new).xlsx']
data['path'] = [r'./data/data/graphdata(new).xlsx']
data['key'] = ['sample_password']
data.to_csv('data/data_info.csv',index=False)
'''