import pygame
import numpy as np
from pydub import AudioSegment
from pydub.utils import mediainfo

pygame.init()

# Load the audio file
audio_path = "bad_omens_like_a_villain.mp3"
audio_info = mediainfo(audio_path)
audio = AudioSegment.from_file(audio_path, format=audio_info['format'])
fps = audio.frame_rate

# Create the Pygame window
window_width = 800
window_height = 600
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Music Visualizer")

# Define colors
bg_color = (0, 0, 0)
line_color = (255, 255, 255)
ball_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

# Define ball properties
ball_radius = 50
ball_color_index = 0
ball_color = ball_colors[ball_color_index]
ball_speed = 0.1
ball_direction = 1
ball_pos = np.array([window_width / 2, window_height / 2])
ball_velocity = np.array([ball_speed, ball_speed]) * ball_direction

# Define audio properties
audio_length = audio.duration_seconds
chunk_size = 1024
chunks_per_second = fps // chunk_size

# Define waveform properties
waveform_width = 2
waveform_height = 300
waveform_margin_top = 50
waveform_margin_bottom = 50
waveform_x = 0
waveform_y = (window_height - waveform_height - waveform_margin_bottom)

# Create the waveform array
waveform_length = int(audio_length * chunks_per_second)
waveform_array = np.zeros((waveform_length, chunk_size))
for i, chunk in enumerate(audio[:audio_length * 1000:chunk_size]):
    waveform_array[i] = np.frombuffer(chunk._data, dtype=np.int16)

# Scale the waveform to fit the window
waveform_scale = (waveform_height / 2) / np.abs(waveform_array).max()
waveform_array *= waveform_scale
waveform_array += waveform_y + waveform_height / 2

# Main loop
running = True
clock = pygame.time.Clock()

# Define time and amplitude properties
audio_time = 0
amplitude = 0

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Calculate current audio time
    audio_time = pygame.mixer.music.get_pos() / 1000.0

    # Calculate current amplitude
    if audio_time >= audio_length:
        amplitude = 0
    else:
        chunk_index = int(audio_time * chunks_per_second)
        amplitude = np.abs(waveform_array[chunk_index]).mean() / (waveform_height / 2)

    # Update the ball position
    ball_speed = amplitude * 10 + 0.1
    ball_direction = np.sign(ball_velocity[0]) * np.sign(amplitude - 0.5)
    ball_velocity = np.array([ball_speed, ball_speed]) * ball_direction
    ball_pos += ball_velocity

    # Bounce the ball off the walls
    if ball_pos[0] < ball_radius or ball_pos[0] > window_width - ball_radius:
        ball_direction *= -1
        ball_color_index = (ball_color_index + 1) % len(ball_colors)
        ball_color = ball_colors[ball_color_index]
    if ball_pos[1] < ball_radius or ball_pos[1] > window_height - ball_radius:
        ball_direction *= -1
        ball_color_index = (ball_color_index + 1) % len(ball_colors)
        ball_color = ball_colors[ball_color_index]
# Draw the background
window.fill(bg_color)

# Draw the waveform
for i in range(waveform_length - 1):
    x1 = i * waveform_width
    y1 = waveform_array[i]
    x2 = (i + 1) * waveform_width
    y2 = waveform_array[i + 1]
    pygame.draw.line(window, line_color, (x1, y1), (x2, y2), waveform_width)

# Draw the ball
pygame.draw.circle(window, ball_color, ball_pos.astype(int), ball_radius)

# Update the display
pygame.display.update()

# Limit the frame rate
clock.tick(60)

pygame.quit()


