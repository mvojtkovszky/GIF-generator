from PIL import Image
import io

# === Settings ===

# === Effect Functions ===
def rotate_effect_left(image, duration):
    steps = 24
    frames = []
    for i in range(steps):
        angle = int(360 * i / steps)
        rotated = image.rotate(angle, resample=Image.BICUBIC)
        frames.append(rotated)
    durations = [duration] * len(frames)
    return frames, durations

def rotate_effect_right(image, duration):
    steps = 24
    frames = []
    for i in range(steps):
        angle = int(360 - (360 * i / steps))
        rotated = image.rotate(angle, resample=Image.BICUBIC)
        frames.append(rotated)
    durations = [duration] * len(frames)
    return frames, durations

def still_effect(image, duration):
    return [image], [duration]

def bounce_zoom_effect(image, duration):
    steps = 30  # 30 steps × 30ms ≈ 900ms for bounce/move
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

def move_from_left_effect(image, duration):
    steps = 30  # 30 steps × 30ms ≈ 900ms for bounce/move
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

def move_from_right_effect(image, duration):
    steps = 30  # 30 steps × 30ms ≈ 900ms for bounce/move
    frames = []
    durations = []
    canvas_width, canvas_height = image.size
    start_x = canvas_width
    end_x = -image.width
    for i in range(steps):
        x = int(start_x + (end_x - start_x) * (i / (steps - 1)))
        canvas = Image.new("RGBA", image.size, (255, 255, 255, 0))
        offset = (x, 0)
        canvas.paste(image, offset, image)
        frames.append(canvas)
        durations.append(duration)
    return frames, durations

def pulse_effect(image, duration, scale_range=(1.0, 1.3)):
    steps = 10
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

def shrink_out_effect(image, duration):
    steps = 20  # 20 steps × 30ms ≈ 600ms for shrink
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

def shrink_in_effect(image, duration):
    steps = 20  # 20 steps × 30ms ≈ 600ms for shrink
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
    "rotate_left": rotate_effect_left,
    "rotate_right": rotate_effect_right,
    "still": still_effect,
    "zoom_in_bounce": bounce_zoom_effect,
    "pulse": pulse_effect,
    "shrink_out": shrink_out_effect,
    "shrink_in": shrink_in_effect,
    "move_from_left": move_from_left_effect,
    "move_from_right": move_from_right_effect,
}

def generate_gif(sequence, max_output_size=(80, 80)):
    """
    sequence: list of tuples (PIL.Image object, effect_name str, duration int, repeat int)
    repeat: number of times to repeat the effect (must be at least 1)
    Returns: bytes of the generated GIF
    """
    print("Generating GIF with sequence:", sequence)
    print("Max output size:", max_output_size)
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
    # Override canvas size with max_output_size to ensure final GIF dimensions do not exceed user-defined width and height
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
        # repeat has to be at least 1
        if not isinstance(repeat, int) or repeat < 1:
            repeat = 1
        frames, durations = effect_func(img_centered, duration=duration)
        if repeat > 1:
            frames *= repeat
            durations *= repeat
        all_frames.extend(frames)
        all_durations.extend(durations)

    if not all_frames:
        print("No frames generated. All_frames is empty.")
        return None

    print(f"Saving GIF with {len(all_frames)} frames.")
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
