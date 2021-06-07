from flask import Flask, flash, redirect, url_for, request, render_template, send_from_directory, make_response
from werkzeug.utils import secure_filename
import os
import service
import pandas as pd

UPLOAD_FOLDER = './data/data/'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xls', 'xlsx', 'py'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000000

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
            return redirect(url_for('upload_file'))
        file = request.files.get('file')
        thekey = request.form.get('pass')
        thekey = thekey+'0'*(16-len(thekey))
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            service.encrypt_file1(key=thekey.encode(), in_filename=file, out_filename=filename+'.enc', out_path=UPLOAD_FOLDER)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            with open('data/data_info.csv','a+') as f:
                f.writelines('\r'+filename+'.enc'+','+UPLOAD_FOLDER+filename+'.enc'+','+thekey)
            return redirect(url_for('upload_file'))
            # return 'success'
    return render_template('template1.html')


@app.route('/file_list', methods=['GET', 'POST'])
def list():
    if request.method == 'GET':
        data_info = pd.read_csv('data/data_info.csv')
        file_list = []
        for i in range(len(data_info)):
            file_list.append({'name':data_info['name'][i], 'path': data_info['path'][i]})
        return render_template('template2.html', file_list=file_list)
    elif request.method == 'POST':
        pwd = request.form.get('password')
        fname = request.form.get('filename')
        thekey = pwd+'0'*(16-len(pwd))
        data_path = 'data/data/'
        fname_path = data_path+fname
        out_filename = 'temp/'+os.path.splitext(fname)[0]
        service.decrypt_file(key=thekey.encode(), in_filename=fname_path, out_filename=out_filename)
        response = make_response(send_from_directory('', out_filename, as_attachment=True))
        return response


@app.route('/download/<filename>', methods=['GET'])
def return_file(filename):
    directory = 'data/data/'
    response = make_response(send_from_directory(directory, filename, as_attachment=True))
    return response


if __name__ == '__main__':
    app.run()

