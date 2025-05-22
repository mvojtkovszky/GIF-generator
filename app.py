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

        max_width = request.form.get("max_width")
        max_height = request.form.get("max_height")

        try:
            max_width = int(max_width)
        except (TypeError, ValueError):
            max_width = 80

        try:
            max_height = int(max_height)
        except (TypeError, ValueError):
            max_height = 80

        sequence = []
        for file, effect, duration, repeat in zip(images, effects, durations, repetitions):
            img = Image.open(file.stream).convert("RGBA")
            duration = int(duration)
            repeat = int(repeat)
            sequence.append((img, effect, duration, repeat))

        print("Images:", images)
        print("Effects:", effects)
        print("Durations:", durations)
        print("Repetitions:", repetitions)
        print("Max Size:", max_width, max_height)
        print("Sequence:", sequence)

        gif_bytes = generate_gif(sequence, max_output_size=(max_width, max_height))
        if gif_bytes:
            return send_file(io.BytesIO(gif_bytes), mimetype="image/gif", as_attachment=True, download_name="output.gif")
        else:
            return "Error: GIF could not be generated", 400

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
