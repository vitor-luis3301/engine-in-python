import sys
import glfw
import OpenGL.GL as gl
from pathlib import Path
from pyrr import Vector3, Matrix44
from ctypes import c_float, sizeof, c_void_p, c_uint

CURDIR = Path(__file__).parent.absolute()

from shader import Shader
from camera import Camera, CameraMovement

# -- settings
SRC_WIDTH = 800
SRC_HEIGHT = 600

# -- camera
camera = Camera(Vector3([0.0, 0.0, 5.0]))
last_x = SRC_WIDTH / 2
last_y = SRC_HEIGHT / 2
first_mouse = True

# -- timing
delta_time = 0.0
last_frame = 0.0

light_pos = Vector3([1.2, 1.0, 2.0])

def main():
    global delta_time, last_frame

    if not glfw.init():
        raise ValueError("Failed to initialize glfw")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)

    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(SRC_WIDTH, SRC_HEIGHT, "learnOpenGL", None, None)
    if not window:
        glfw.terminate()
        raise ValueError("Failed to create window")

    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    gl.glEnable(gl.GL_DEPTH_TEST)

    shader = Shader(CURDIR / 'shaders/vertex.vs', CURDIR / 'shaders/fragment.fs')

    data = [
        # positions         colors      normal
        -0.5, -0.5, -0.5, 1.0, 0.0, 0.0,
         0.5, -0.5, -0.5, 0.0, 1.0, 0.0,
         0.5,  0.5, -0.5, 0.0, 0.0, 1.0,
         0.5,  0.5, -0.5, 0.0, 0.0, 1.0,  # Front
        -0.5,  0.5, -0.5, 0.0, 1.0, 0.0,
        -0.5, -0.5, -0.5, 1.0, 0.0, 0.0,

        -0.5, -0.5,  0.5, 1.0, 0.0, 0.0,
         0.5, -0.5,  0.5, 0.0, 1.0, 0.0,
         0.5,  0.5,  0.5, 0.0, 0.0, 1.0,
         0.5,  0.5,  0.5, 0.0, 0.0, 1.0,
        -0.5,  0.5,  0.5, 0.0, 1.0, 0.0,
        -0.5, -0.5,  0.5, 1.0, 0.0, 0.0,

        -0.5,  0.5,  0.5, 1.0, 0.0, 0.0,
        -0.5,  0.5, -0.5, 0.0, 1.0, 0.0,
        -0.5, -0.5, -0.5, 0.0, 0.0, 1.0,
        -0.5, -0.5, -0.5, 0.0, 0.0, 1.0,
        -0.5, -0.5,  0.5, 0.0, 1.0, 0.0,
        -0.5,  0.5,  0.5, 1.0, 0.0, 0.0,

         0.5,  0.5,  0.5, 0.0, 0.0, 1.0,
         0.5,  0.5, -0.5, 0.0, 1.0, 0.0,
         0.5, -0.5, -0.5, 1.0, 0.0, 0.0,
         0.5, -0.5, -0.5, 1.0, 0.0, 0.0,
         0.5, -0.5,  0.5, 0.0, 1.0, 0.0,
         0.5,  0.5,  0.5, 0.0, 0.0, 1.0,

        -0.5, -0.5, -0.5, 1.0, 0.0, 0.0,
         0.5, -0.5, -0.5, 0.0, 1.0, 0.0,
         0.5, -0.5,  0.5, 0.0, 0.0, 1.0,
         0.5, -0.5,  0.5, 0.0, 0.0, 1.0,
        -0.5, -0.5,  0.5, 0.0, 1.0, 0.0,
        -0.5, -0.5, -0.5, 1.0, 0.0, 0.0,

        -0.5,  0.5, -0.5, 1.0, 0.0, 0.0,
         0.5,  0.5, -0.5, 0.0, 1.0, 0.0,
         0.5,  0.5,  0.5, 0.0, 0.0, 1.0,
         0.5,  0.5,  0.5, 0.0, 0.0, 1.0,
        -0.5,  0.5,  0.5, 0.0, 1.0, 0.0,
        -0.5,  0.5, -0.5, 1.0, 0.0, 0.0,
    ]
    data = (c_float * len(data))(*data)

    vao = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(vao)

    vbo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, sizeof(data), data, gl.GL_STATIC_DRAW)

    # -- vertices
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * sizeof(c_float), c_void_p(0))
    gl.glEnableVertexAttribArray(0)

    # -- color
    gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * sizeof(c_float), c_void_p(3 * sizeof(c_float)))
    gl.glEnableVertexAttribArray(1)


    while not glfw.window_should_close(window):
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame

        process_input(window)

        gl.glClearColor(.2, .3, .3, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        shader.use()
        projection = Matrix44.perspective_projection(camera.zoom, SRC_WIDTH / SRC_HEIGHT, 0.1, 100.0)
        view = camera.get_view_matrix()
        shader.set_mat4("projection", projection)
        shader.set_mat4("view", view)

        model = Matrix44.identity()
        shader.set_mat4("model", model)

        gl.glBindVertexArray(vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)

        glfw.poll_events()
        glfw.swap_buffers(window)

    gl.glDeleteVertexArrays(1, id(vao))
    gl.glDeleteBuffers(1, id(vbo))
    glfw.terminate()


def on_resize(window, w, h):
    gl.glViewport(0, 0, w, h)


def process_input(window):
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        camera.process_keyboard(CameraMovement.FORWARD, delta_time)
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        camera.process_keyboard(CameraMovement.BACKWARD, delta_time)

    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera.process_keyboard(CameraMovement.LEFT, delta_time)
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera.process_keyboard(CameraMovement.RIGHT, delta_time)


def framebuffer_size_callback(window, width, height):
    gl.glViewport(0, 0, width, height)


def mouse_callback(window, xpos, ypos):
    global first_mouse, last_x, last_y

    if first_mouse:
        last_x, last_y = xpos, ypos
        first_mouse = False

    xoffset = xpos - last_x
    yoffset = last_y - ypos  # XXX Note Reversed (y-coordinates go from bottom to top)
    last_x = xpos
    last_y = ypos

    camera.process_mouse_movement(xoffset, yoffset)


def scroll_callback(window, xoffset, yoffset):
    camera.process_mouse_scroll(yoffset)


if __name__ == '__main__':
    main()


if __name__ == '__main__':
    main()
