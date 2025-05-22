from flask import Flask, request, render_template, send_file
from PIL import Image
from generate_gif import generate_gif
import io

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        images = request.files.getlist("images")
        effects = request.form.getlist("effect")
        durations = request.form.getlist("duration")
        repetitions = request.form.getlist("repetitions")

        sequence = []
        for file, effect, duration, repeat in zip(images, effects, durations, repetitions):
            img = Image.open(file.stream).convert("RGBA")
            duration = int(duration)
            sequence.append((img, effect, duration, repeat))

        gif_bytes = generate_gif(sequence)
        if gif_bytes:
            return send_file(io.BytesIO(gif_bytes), mimetype="image/gif", as_attachment=True, download_name="output.gif")
        else:
            return "Error: GIF could not be generated", 400

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
