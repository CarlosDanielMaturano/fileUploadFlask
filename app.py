from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
import os 
from shutil import rmtree   


app = Flask(__name__) 
app.config["SECRET_KEY"] = "coolkey"
files_path = os.path.realpath("files")
app.config["UPLOAD_FOLDER"] = files_path


icons_for_file_types = {
    "txt":     'text.svg',
    "jpg":      'images.svg',
    "png":     'images.svg',
    "jpeg":    'images.sv',
    "pdf":     'pdf.svg',
    "mp4":     'video.svg'   
}

def get_files(dir):
    path = os.path.join(files_path, dir)
    if os.path.isdir(path):
        _dir = os.listdir(path)
        _dir.sort()
        for file in _dir:
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):                    
                yield {
                        "filename":     file,
                        "file_path":    f'{dir}|{file}',
                        "file_type":    file[file.index('.')+1:]
                    }
                

def get_folders():
     for dir in os.listdir(files_path):
        path = os.path.join(files_path, dir)
        if os.path.isdir(path):
            yield dir


def delete_file(filename):
    os.remove(os.path.join(files_path, filename))


@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        folder_name = request.form["folder_name"]
        try:
            os.mkdir(os.path.join(files_path, folder_name))
        except:
            flash("Folder already exists")


    return render_template("index.html", folders=list(get_folders()))


@app.route('/files/<folder_name>', methods=["GET", "POST"])
def files(folder_name):
    if request.method == "POST":
        if 'file' not in request.files:
            flash("No files")
            return redirect(url_for('index'))

        file = request.files['file']
        
        if not any(file.filename.endswith(file_type) for file_type in icons_for_file_types.keys()):
            flash("Banned file type")
            return redirect(url_for('files', folder_name=folder_name))

        file.save(os.path.join(files_path, f'{folder_name}/{file.filename}'))

    files = list(get_files(folder_name))
    return render_template("files.html", files=files, icons=icons_for_file_types)


@app.route('/files/delete/<file>')
def delete_file(file):
    folder_name = file[0:file.index('|')]
    file = str(file).replace('|', '/')
    os.remove(os.path.join(files_path, file))
   
    return redirect(url_for("files", folder_name=folder_name))

@app.route('/delete/<folder_name>')
def delete_folder(folder_name):
    folder_path  = os.path.join(files_path, folder_name)
    rmtree(folder_path)
   

    return redirect(url_for('index'))


@app.route('/files/download/<file>')
def download_file(file):
    file = str(file).replace('|', '/')
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], path=file, filename=file, as_attachment=True)


@app.route('/files/view/<file>')
def view_raw(file):
    file = str(file).replace('|', '/')
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], path=file, filename=file)


if __name__ == '__main__':
    app.run(debug=True)
