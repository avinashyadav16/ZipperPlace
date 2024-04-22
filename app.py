import os
import glob
import shutil
import subprocess
from flask import Flask, render_template, request, send_file

app = Flask(__name__)
app.config["FILE_UPLOADS"] = r"C:\Users\avina\OneDrive - Shiv Nadar Foundation\SRM - AP\DOCUMENT\GitHub\ZipperPlace\uploads"


def clear_directory(directory):
    filelist = glob.glob(directory + '*')
    for f in filelist:
        if os.path.isfile(f):
            os.remove(f)


@app.route("/")
def home():
    clear_directory('uploads/')
    clear_directory('downloads/')
    return render_template("home.html")


@app.route("/compress", methods=["GET", "POST"])
def compress():
    if request.method == "GET":
        return render_template("compress.html", check=0)

    up_file = request.files["file"]
    if not up_file.filename:
        return render_template("compress.html", check=-1)

    filename = up_file.filename
    up_file_path = os.path.join(app.config["FILE_UPLOADS"], filename)
    up_file.save(up_file_path)

    subprocess.run(['huffcompress.exe', 'uploads/{}'.format(filename)])

    filename = filename.split('.')[0]
    ftype = "-compressed.bin"

    shutil.move('uploads/{}{}'.format(filename, ftype), 'downloads/')

    return render_template("compress.html", check=1)


@app.route("/decompress", methods=["GET", "POST"])
def decompress():
    if request.method == "GET":
        return render_template("decompress.html", check=0)

    up_file = request.files["file"]
    if not up_file.filename:
        return render_template("decompress.html", check=-1)

    filename = up_file.filename
    up_file_path = os.path.join(app.config["FILE_UPLOADS"], filename)
    up_file.save(up_file_path)

    subprocess.run(['huffdecompress.exe', 'uploads/{}'.format(filename)])

    # Check for decompressed file in uploads directory
    decompressed_files = [f for f in os.listdir(
        'uploads/') if f.startswith(filename)]

    if decompressed_files:
        decompressed_filename = decompressed_files[0]
        ftype = decompressed_filename.split(
            '.')[1] if '.' in decompressed_filename else ""
    else:
        print(f"Decompressed file not found for {filename}.")
        ftype = ""

    source_file_path = os.path.join(
        'uploads', decompressed_filename) if decompressed_files else None
    destination_file_path = 'downloads/'

    if source_file_path:
        try:
            shutil.move(source_file_path, os.path.join(
                destination_file_path, decompressed_filename))
            print(f"File moved successfully to {
                  destination_file_path}{decompressed_filename}")
        except FileNotFoundError as e:
            print(f"Error moving file: {e}")
    else:
        print("File not found for moving.")

    return render_template("decompress.html", check=1)


@app.route("/download")
def download_file():
    filename = request.args.get('filename')
    ftype = request.args.get('ftype')

    if filename is None or ftype is None:
        return "File not found", 404

    # path = os.path.join("downloads", filename + ftype)
    path = os.path.join(app.config["FILE_UPLOADS"],
                        "downloads", filename + ftype)

    print("Attempting to download file from path:", path)  # Debugging line
    print("Current working directory:", os.getcwd())  # Debugging line

    if not os.path.exists(path):
        return "File not found", 404

    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
