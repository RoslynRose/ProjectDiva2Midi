
import pygame
import mido
from mido import Message

# Define MIDI notes for C major scale from C4 to C5
midi_notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C4, D4, E4, F4, G4, A4, B4, C5

# Initialize pygame for controller input and GUI
pygame.init()
pygame.joystick.init()

# Check for joystick
joystick_connected = pygame.joystick.get_count() > 0
if joystick_connected:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

# Load background image and determine initial window size
max_width, max_height = 960, 540
background = pygame.image.load('miku.png')
original_width, original_height = background.get_size()
aspect_ratio = original_width / original_height

# Calculate initial window size
if original_width > max_width or original_height > max_height:
    if original_width / max_width < original_height / max_height:
        initial_width = int(original_width * (max_height / original_height))
        initial_height = max_height
    else:
        initial_width = max_width
        initial_height = int(original_height * (max_width / original_width))
else:
    initial_width, initial_height = original_width, original_height

screen = pygame.display.set_mode((initial_width, initial_height), pygame.RESIZABLE)
pygame.display.set_caption('PS3 Controller to MIDI')

# Initialize mido for MIDI output
outport = mido.open_output()  # Select appropriate MIDI output

# Store button and key states
button_states = [False] * 8  # False for not pressed, True for pressed
key_mappings = {
    pygame.K_w: 0,
    pygame.K_a: 1,
    pygame.K_s: 2,
    pygame.K_d: 3,
    pygame.K_i: 4,
    pygame.K_j: 5,
    pygame.K_k: 6,
    pygame.K_l: 7
}

# Define square size and margin
square_size = 30
margin = 20

# Function to resize the window while maintaining aspect ratio
def resize_window(new_width, new_height):
    new_aspect = new_width / new_height
    if new_aspect > aspect_ratio:
        new_width = int(new_height * aspect_ratio)
    else:
        new_height = int(new_width / aspect_ratio)
    screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
    return new_width, new_height

current_width, current_height = initial_width, initial_height

try:
    running = True
    while running:
        screen.fill((0, 0, 0))  # Fill background with black
        scaled_background = pygame.transform.scale(background, (current_width, current_height))
        screen.blit(scaled_background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                current_width, current_height = resize_window(event.w, event.h)

            elif joystick_connected and event.type in [pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]:
                button_index = event.button
                button_states[button_index] = event.type == pygame.JOYBUTTONDOWN
                note = midi_notes[button_index]
                midi_action = 'note_on' if event.type == pygame.JOYBUTTONDOWN else 'note_off'
                outport.send(Message(midi_action, note=note))

            elif event.type in [pygame.KEYDOWN, pygame.KEYUP] and event.key in key_mappings:
                button_index = key_mappings[event.key]
                button_states[button_index] = event.type == pygame.KEYDOWN
                note = midi_notes[button_index]
                midi_action = 'note_on' if event.type == pygame.KEYDOWN else 'note_off'
                outport.send(Message(midi_action, note=note))

        # Display square indicators for notes
        squares_x = current_width - square_size - margin  # Place squares on the right side
        for i, state in enumerate(button_states):
            color = (0, 255, 0) if state else (255, 0, 0)
            square_y = current_height - (i + 1) * (square_size + margin)
            pygame.draw.rect(screen, color, (squares_x, square_y, square_size, square_size))

        # Display message if no joystick is connected
        if not joystick_connected:
            font = pygame.font.Font(None, 36)
            text = font.render('No controller connected', True, (255, 255, 255))
            screen.blit(text, (50, 50))

        pygame.display.flip()

except KeyboardInterrupt:
    pass

finally:
    # Clean up on exit
    pygame.quit()
    outport.close()
