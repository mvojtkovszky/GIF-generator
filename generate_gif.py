from PIL import Image
import io

# === Settings ===
max_output_size = (64, 64)      # Resize input images to fit within this size

# === Effect Functions ===
def rotate_effect(image, step=10, rotation_duration=30):
    frames = []
    for angle in range(0, 360, step):
        rotated = image.rotate(angle, resample=Image.BICUBIC)
        frames.append(rotated)
    durations = [rotation_duration] * len(frames)
    return frames, durations

def still_effect(image, duration=500):
    return [image], [duration]

def bounce_zoom_effect(image, steps=10, duration=30):
    frames = []
    durations = []
    # Scale from 1.0 to 1.5 and back to 1.0
    max_scale = 1.5
    scales = [1 + (max_scale - 1) * (i / (steps - 1)) for i in range(steps)]
    scales += scales[-2::-1]  # bounce back
    for scale in scales:
        new_size = (int(image.width * scale), int(image.height * scale))
        frame = image.resize(new_size, Image.Resampling.LANCZOS)
        # Center on canvas
        canvas = Image.new("RGBA", image.size, (255, 255, 255, 0))
        offset = ((image.width - frame.width) // 2, (image.height - frame.height) // 2)
        canvas.paste(frame, offset, frame)
        frames.append(canvas)
        durations.append(duration)
    return frames, durations

def move_from_left_effect(image, steps=20, duration=30):
    frames = []
    durations = []
    canvas_width, canvas_height = image.size
    start_x = -image.width
    end_x = canvas_width
    for i in range(steps):
        x = int(start_x + (end_x - start_x) * (i / (steps - 1)))
        canvas = Image.new("RGBA", image.size, (255, 255, 255, 0))
        offset = (x, 0)
        canvas.paste(image, offset, image)
        frames.append(canvas)
        durations.append(duration)
    return frames, durations

def pulse_effect(image, steps=5, scale_range=(1.0, 1.3), duration=40):
    frames = []
    durations = []
    min_scale, max_scale = scale_range
    scales_up = [min_scale + (max_scale - min_scale) * (i / (steps - 1)) for i in range(steps)]
    scales_down = scales_up[-2::-1]
    scales = scales_up + scales_down
    for scale in scales:
        new_size = (int(image.width * scale), int(image.height * scale))
        frame = image.resize(new_size, Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", image.size, (255, 255, 255, 0))
        offset = ((image.width - frame.width) // 2, (image.height - frame.height) // 2)
        canvas.paste(frame, offset, frame)
        frames.append(canvas)
        durations.append(duration)
    return frames, durations

def shrink_out_effect(image, steps=10, duration=40):
    frames = []
    durations = []
    scales = [1 - (i / (steps - 1)) for i in range(steps)]
    for scale in scales:
        if scale <= 0:
            scale = 0.01  # avoid zero size
        new_size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
        frame = image.resize(new_size, Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", image.size, (255, 255, 255, 0))
        offset = ((image.width - frame.width) // 2, (image.height - frame.height) // 2)
        canvas.paste(frame, offset, frame)
        frames.append(canvas)
        durations.append(duration)
    return frames, durations

def shrink_in_effect(image, steps=10, duration=40):
    frames = []
    durations = []
    scales = [(i / (steps - 1)) for i in range(steps)]
    for scale in scales:
        if scale <= 0:
            scale = 0.01  # avoid zero size
        new_size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
        frame = image.resize(new_size, Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", image.size, (255, 255, 255, 0))
        offset = ((image.width - frame.width) // 2, (image.height - frame.height) // 2)
        canvas.paste(frame, offset, frame)
        frames.append(canvas)
        durations.append(duration)
    return frames, durations

# === Helper Functions ===
def center_image(img, canvas_size):
    background = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
    offset = ((canvas_size[0] - img.width) // 2, (canvas_size[1] - img.height) // 2)
    background.paste(img, offset, img)
    return background

# === Effects dictionary ===
effects = {
    "rotate": rotate_effect,
    "still": still_effect,
    "zoom_in_bounce": bounce_zoom_effect,
    "pulse": pulse_effect,
    "shrink_out": shrink_out_effect,
    "shrink_in": shrink_in_effect,
    "move_from_left": move_from_left_effect,
}

def generate_gif(sequence):
    """
    sequence: list of tuples (PIL.Image object, effect_name str, duration int or None, repeat int)
    Returns: bytes of the generated GIF
    """
    # Resize images and store in dict to avoid duplicate resizing if same image instance
    images = {}
    for img, _, _, _ in sequence:
        img_id = id(img)
        if img_id not in images:
            # Create a copy to avoid modifying original image
            img_copy = img.copy()
            img_copy.thumbnail(max_output_size, Image.Resampling.LANCZOS)
            images[img_id] = img_copy

    # Determine canvas size (max diagonal)
    max_side = 0
    for img in images.values():
        side = int((img.width**2 + img.height**2) ** 0.5)
        if side > max_side:
            max_side = side
    canvas_size = (max_side, max_side)

    all_frames = []
    all_durations = []
    for img, effect_name, duration, repeat in sequence:
        img_resized = images[id(img)]
        img_centered = center_image(img_resized, canvas_size)
        effect_func = effects.get(effect_name)
        if not effect_func:
            # Skip unknown effect
            continue
        if effect_name == "rotate":
            step = 10
            rot_dur = duration if duration is not None else 30
            frames, durations = effect_func(img_centered, step=step, rotation_duration=rot_dur)
        elif effect_name == "still":
            dur = duration if duration is not None else 500
            frames, durations = effect_func(img_centered, duration=dur)
        elif effect_name == "zoom_in_bounce":
            steps = 10
            dur = duration if duration is not None else 30
            frames, durations = effect_func(img_centered, steps=steps, duration=dur)
        elif effect_name == "pulse":
            steps = 5
            dur = duration if duration is not None else 40
            frames, durations = effect_func(img_centered, steps=steps, duration=dur)
        elif effect_name == "shrink_out":
            steps = 10
            dur = duration if duration is not None else 40
            frames, durations = effect_func(img_centered, steps=steps, duration=dur)
        elif effect_name == "shrink_in":
            steps = 10
            dur = duration if duration is not None else 40
            frames, durations = effect_func(img_centered, steps=steps, duration=dur)
        elif effect_name == "move_from_left":
            steps = 20
            dur = duration if duration is not None else 30
            frames, durations = effect_func(img_centered, steps=steps, duration=dur)
        else:
            frames, durations = effect_func(img_centered)
        frames *= repeat
        durations *= repeat
        all_frames.extend(frames)
        all_durations.extend(durations)

    if not all_frames:
        return None

    # Save GIF to bytes
    output_bytes = io.BytesIO()
    all_frames[0].save(
        output_bytes,
        format="GIF",
        save_all=True,
        append_images=all_frames[1:],
        duration=all_durations,
        loop=0,
        disposal=2  # Clears previous frame before showing next
    )
    output_bytes.seek(0)
    return output_bytes.getvalue()
