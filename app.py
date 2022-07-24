from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
import os 


app = Flask(__name__) 
app.config["SECRET_KEY"] = "coolkey"
files_path = os.path.realpath("files")
app.config["UPLOAD_FOLDER"] = files_path
permitted_files = [".txt", ".jpg", ".png", ".jpeg", ".pdf", ".mp4"]


def get_files():
    for dir in os.listdir(files_path):
        path = os.path.join(files_path, dir)
        if os.path.isdir(path):
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                if os.path.isfile(file_path):                    
                    yield {
                            "filename":   file,
                            "file_path":  f'{dir}|{file}'
                        }


def delete_file(filename):
    os.remove(os.path.join(files_path, filename))


def organize_files():
    for file in os.listdir(files_path):
        path = os.path.join(files_path, file)
        if os.path.isfile(path):
            default_file_type = None
            for file_type in permitted_files:
                if file.endswith(file_type):
                    default_file_type = file_type.removeprefix('.')
                    break 

            if default_file_type:
                os.replace(path, os.path.join(files_path, f'{default_file_type}/{file}'))
    

@app.route('/', methods=["GET", "POST"])
def index():
    organize_files()
    if request.method == "POST":
        if 'file' not in request.files:
            flash("No files")
            return redirect(url_for('index'))

        file = request.files['file']
        
        if not any(file.filename.endswith(file_type) for file_type in permitted_files):
            flash("Banned file type")
            print("SEM MACACO")
            return redirect(url_for('index'))

        file.save(os.path.join(files_path, file.filename))
        organize_files()

    return render_template("index.html", files=list(get_files()))


@app.route('/delete/<file>')
def delete_file(file):
    file = str(file).replace('|', '/')
    print(file)
    os.remove(os.path.join(files_path, file))
   
    return redirect(url_for("index"))


@app.route('/download/<file>')
def download_file(file):
    file = str(file).replace('|', '/')
    print(file)
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], path=file, filename=file, as_attachment=True)


@app.route('/view/<file>')
def view_raw(file):
    file = str(file).replace('|', '/')
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], path=file, filename=file)


if __name__ == '__main__':
    app.run(debug=True)
