

# Animated GIF Creator (Web App)

This project provides a simple web interface for creating animated GIFs from multiple images using customizable visual effects like rotation, zoom, bounce, and motion.

Each image can have its own effect, duration (in milliseconds per frame), and number of repetitions (how many times the effect is repeated). The result is generated as a downloadable looping GIF.

## Setup Instructions (macOS/Homebrew)

1. Install Python and Flask:

If Python is not installed via Homebrew:

```
brew install python
```

Then install the required Python packages:

```
pip3 install flask pillow
```

2. Run the app:

In the project folder (where `app.py` is located), run:

```
python3 app.py
```

Then open this address in your browser:

```
http://127.0.0.1:5000
```

## Usage

- Click “Add Another” to add multiple image/effect rows.
- Each row requires:
  - An image file (PNG preferred)
  - An animation effect
  - A duration in milliseconds (per frame)
  - A number of repetitions (how many times to repeat the effect)
- Click “Generate GIF” to create and download the result.
