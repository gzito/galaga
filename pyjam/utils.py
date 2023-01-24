import math
import glm

K_EPSILON = 0.000001

# angles are in degrees, rotation are clockwise
# angles are measured starting at 0 degrees from negative y-axis (up).
# 180 degrees means oriented toward positive y-axis (down)


def sin_deg(angle_deg: float) -> float:
    return math.sin(glm.radians(angle_deg))


def cos_deg(angle_deg: float) -> float:
    return math.cos(glm.radians(angle_deg))


def tan_deg(angle_deg: float) -> float:
    return math.tan(glm.radians(angle_deg))


def atan2_deg(y: float, x: float) -> float:
    """
    Returns the arc tangent of y/x, in degrees. Where x and y are the coordinates of a point (x,y)
    The returned value is between 180 and -180.
    """
    return glm.degrees(math.atan2(y, x))


def acos_deg(x: float) -> float:
    return glm.degrees(math.acos(x))


def asin_deg(x: float) -> float:
    return glm.degrees(math.asin(x))


def wrap_angle_deg_180(angle: float):
    """ Wraps angle expressed in degrees between the range [-180,180] """

    angle -= math.ceil(angle / 360 - 0.5) * 360
    return angle


def wrap_angle_deg_360(angle: float):
    """ Wraps angle expressed in degrees between the range [0,360) """
    return wrap(angle, 0, 359)


def delta_angle_unsigned(angle_from: float, angle_to: float) -> float:
    """
    Returns the smallest positive angle in degrees between 2 angles
    """
    return abs(wrap_angle_deg_180(angle_to - angle_from))


def delta_angle_signed(angle_from: float, angle_to: float) -> float:
    """
    Returns the smallest angle in degrees between 2 angles
    The delta angle can be positive or negative, since it express the smallest angle rotation
    positive (clockwise) or negative (anti-clockwise) needed to move from "angle_from" to "angle_to"
    """
    delta = wrap_angle_deg_360(angle_to) - wrap_angle_deg_360(angle_from)
    return wrap_angle_deg_180(delta)


def wrap(n, nmin, nmax):
    """ Wraps value between the range [nmin,nmax] """

    if nmin <= n <= nmax:
        w = n
    else:  # n < nmin or n > nmax
        w = n % (nmax+1) + nmin
    return w


def wrapf(n, nmin: float, nmax: float):
    """ Wraps value between the range [nmin,nmax] """

    if nmin <= n <= nmax:
        w = n
    else:  # n < nmin or n > nmax
        w = n % nmax + nmin
    return w


def clamp(value, vmin, vmax):
    """ Clamps value between min and max and returns value """
    if value < vmin:
        value = vmin
    elif value > vmax:
        value = vmax
    return value


def clamp01(value: float) -> float:
    """ Clamps value between 0.0 and 1.0 and returns value """
    if value < 0.0:
        value = 0.0
    elif value > 1.0:
        value = 1.0
    return value


def vec2_to_str(v: glm.vec2):
    return f'({v.x:.02f}, {v.y:.02f})'


def vec2_from_angle_deg(angle: float) -> glm.vec2:
    """ Given an angle in degrees starting from y-axis, it returns the unit vector oriented by that angle """

    angle_rad = glm.radians(wrap_angle_deg_180(angle - 90))
    v = glm.vec2(math.cos(angle_rad), math.sin(angle_rad))
    return glm.normalize(v)


def vec2_angle_from_y_deg(v: glm.vec2) -> float:
    """ Returns the angle in degrees between the given vector and the y-axis """

    angle = atan2_deg(v.y, v.x)
    # with y is positive down it is: wrap_angle_deg_180(angle-270)
    # with y positive up it is: wrap_angle_deg_180(90-angle)
    return wrap_angle_deg_180(angle-270)


def vec2_delta_angle_deg_signed(vfrom: glm.vec2, vto: glm.vec2) -> float:
    angle_from = vec2_angle_from_y_deg(vfrom)
    angle_to = vec2_angle_from_y_deg(vto)
    return delta_angle_signed(angle_from, angle_to)


def vec2_delta_angle_deg_unsigned(vfrom: glm.vec2, vto: glm.vec2) -> float:
    """
    Returns the angle in degrees between from and to.

    The angle returned is the unsigned angle between the two vectors.
    Note: The angle returned will always be between 0 and 180 degrees,
    because the method returns the smallest angle between the vectors.
    """

    denom = math.sqrt(glm.length2(vfrom) * glm.length2(vto))
    dot = clamp(glm.dot(vfrom, vto) / denom, -1.0, 1.0)
    return acos_deg(float(dot))


def vec2_move_torwards(current: glm.vec2, target: glm.vec2, max_distance_delta: float) -> glm.vec2:
    """ Moves a point current towards target. """

    to_vector = target - current
    sq_dist = to_vector.x * to_vector.x + to_vector.y * to_vector.y

    if sq_dist == 0 or (max_distance_delta >= 0 and sq_dist <= max_distance_delta * max_distance_delta):
        return target

    dist = math.sqrt(sq_dist)

    return glm.vec2(current.x + to_vector.x / dist * max_distance_delta,
                    current.y + to_vector.y / dist * max_distance_delta)


def vec2_rotate_towards(current: glm.vec2, target: glm.vec2, max_degrees_delta: float):
    """ Rotates a vector current towards target. """

    from_direction = glm.normalize(current)
    to_direction = glm.normalize(target)
    angle_degrees = acos_deg(glm.dot(from_direction, to_direction))
    angle_degrees = glm.min(angle_degrees, max_degrees_delta)
    axis = glm.vec3(0, 0, 1)
    rotation_increment = glm.angleAxis(glm.radians(angle_degrees), axis)
    return glm.vec2(rotation_increment * glm.vec3(from_direction, 0))


def quat_rotate_towards(q_from: glm.quat, q_to: glm.quat, max_degrees_delta: float):
    """ Rotates a quaternion q_from towards q_to """
    angle = quat_get_delta_angle_deg(q_from, q_to)
    if angle == 0.0:
        return q_to
    return glm.slerp(q_from, q_to, glm.min(max_degrees_delta / angle, 1.0))


def quat_get_roll_deg(q: glm.quat) -> float:
    """ Returns the roll angle in degrees of the given quaternion """

    return glm.degrees(glm.roll(q))


def quat_get_delta_angle_deg(a: glm.quat, b: glm.quat):
    """ Returns the absolute roll angle difference in degrees between two quaternions """

    dot = glm.min(glm.abs(glm.dot(a, b)), 1.0)
    return 0.0 if is_equal_using_dot(dot) else acos_deg(dot) * 2.0


def is_equal_using_dot(dot: float):
    # Returns false in the presence of NaN values.

    return dot > 1.0 - K_EPSILON


def swap_endians(value):
    leftmost_byte = (value & eval('0x000000FF')) >> 0
    left_middle_byle = (value & eval('0x0000FF00')) >> 8
    right_middle_byte = (value & eval('0x00FF0000')) >> 16
    rightmost_byte = (value & eval('0xFF000000')) >> 24

    leftmost_byte <<= 24
    left_middle_byle <<= 16
    right_middle_byte <<= 8
    rightmost_byte <<= 0

    return (leftmost_byte | left_middle_byle
            | right_middle_byte | rightmost_byte)

