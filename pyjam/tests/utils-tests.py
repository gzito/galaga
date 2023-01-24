import math
import glm

from pyjam import utils


def quat_test_1():
    v = glm.vec3(1, 0, 0)
    print(f'v = {v}')

    a_rad = glm.radians(45)

    # quat as angle axis
    qa = glm.angleAxis(a_rad, glm.vec3(0, 0, 1))
    va = qa * v
    print(f'va = {va}')

    # quat initialization
    qa = glm.quat(math.cos(a_rad / 2), 0, 0, math.sin(a_rad / 2))
    va = qa * v
    print(f'va = {va}')
    # print(f'angle(qa): {glm.degrees(glm.angle(qa))}')

    # euler angles to quat
    qa = glm.quat(glm.radians(glm.vec3(0, 0, 45)))
    va = qa * v
    print(f'va = {va}')

    # 2d point rotation
    va = glm.vec2(v.x * math.cos(a_rad) - v.y * math.sin(a_rad), v.x * math.sin(a_rad) + v.y * math.cos(a_rad))
    print(f'va = {va}')

    # glm rotate z
    va = glm.rotateZ(v, a_rad)
    print(f'va = {va}')


def quat_test_2():
    a = glm.vec3(1, -1, 0)
    b = glm.vec3(-1, -1, 0)
    # q1 is the rotation between a to b
    q1 = glm.quat(a, b)
    # q2 is the rotation between b to a
    q2 = glm.quat(b, a)
    print(f'a = {a}')
    print(f'b = {b}')
    print(f'q1 = {q1}')
    print(f'q2 = {q2}')
    print(f'glm.angle(q1) = {glm.angle(q1)} ({glm.degrees(glm.angle(q1))})')
    print(f'glm.axis(q1) = {glm.axis(q1)}')
    print(f'glm.angle(q2) = {glm.angle(q2)} ({glm.degrees(glm.angle(q2))})')
    print(f'glm.axis(q2) = {glm.axis(q2)}')

    aa = utils.vec2_angle_from_y_deg(glm.vec2(a))
    print(f'aa = {aa}')
    ab = utils.vec2_angle_from_y_deg(glm.vec2(b))
    print(f'ab = {ab}')
    qa = glm.angleAxis(glm.radians(aa), glm.vec3(0, 0, 1))
    qb = glm.angleAxis(glm.radians(ab), glm.vec3(0, 0, 1))
    aqab = utils.quat_get_delta_angle_deg(qa, qb)
    print(f'glm.angle(q) = {glm.radians(aqab)} ({aqab})')


def quat_test_3():
    # quat from euler angles
    q1 = glm.quat(glm.radians(glm.vec3(0, 0, 45)))
    q2 = glm.quat(glm.radians(glm.vec3(0, 0, 135)))
    print(glm.degrees(glm.angle(q1)), glm.degrees(glm.angle(q2)))

    qt = glm.quat(q1)
    while glm.degrees(glm.angle(q2)) - glm.degrees(glm.angle(qt)) > 0.0001:
        qt = glm.slerp(qt, q2, glm.radians(5))
        print(glm.degrees(glm.angle(qt)))


def test_vec_from_angle_single(angle):
    print(f'vec2 from angle {angle}: {utils.vec2_to_str(utils.vec2_from_angle_deg(angle))}')


def test_vec_from_angle():
    print('--- test_vec_from_angle')
    test_vec_from_angle_single(0)
    test_vec_from_angle_single(45)
    test_vec_from_angle_single(90)
    test_vec_from_angle_single(135)
    test_vec_from_angle_single(180)
    test_vec_from_angle_single(225)
    test_vec_from_angle_single(270)
    test_vec_from_angle_single(315)
    test_vec_from_angle_single(-45)
    test_vec_from_angle_single(-90)
    test_vec_from_angle_single(-180)


def test_angle_from_vec_single(v: glm.vec2):
    print(f'Angle from vec2({utils.vec2_to_str(v)}): ', utils.vec2_angle_from_y_deg(v))


def test_angle_from_vec():
    print('--- test_angle_from_vec')
    test_angle_from_vec_single(glm.vec2(0, -1))
    test_angle_from_vec_single(glm.vec2(1, -1))
    test_angle_from_vec_single(glm.vec2(1, 0))
    test_angle_from_vec_single(glm.vec2(1, 1))
    test_angle_from_vec_single(glm.vec2(0, 1))
    test_angle_from_vec_single(glm.vec2(-1, 1))
    test_angle_from_vec_single(glm.vec2(-1, 0))
    test_angle_from_vec_single(glm.vec2(-1, -1))


def test_delta_angle_signed_single(a, b):
    print(f'Delta angle signed({a},{b}): ', utils.delta_angle_signed(a, b))


def test_delta_angle_signed():
    print('--- test_delta_angle_signed')
    test_delta_angle_signed_single(0, 90)
    test_delta_angle_signed_single(90, 0)
    test_delta_angle_signed_single(0, -135)
    test_delta_angle_signed_single(-90, 0)
    test_delta_angle_signed_single(-135, 135)
    test_delta_angle_signed_single(135, -135)
    test_delta_angle_signed_single(720, -90)
    test_delta_angle_signed_single(720, 179)


def test_delta_angle_unsigned_single(a, b):
    print(f'Delta angle unsigned({a},{b}): ', utils.delta_angle_unsigned(a, b))


def test_delta_angle_unsigned():
    print('--- test_delta_angle_unsigned')
    test_delta_angle_unsigned_single(0, 90)
    test_delta_angle_unsigned_single(90, 0)
    test_delta_angle_unsigned_single(0, -135)
    test_delta_angle_unsigned_single(-90, 0)
    test_delta_angle_unsigned_single(-135, 135)
    test_delta_angle_unsigned_single(135, -135)
    test_delta_angle_unsigned_single(720, -90)
    test_delta_angle_unsigned_single(720, 179)


def test_vec2_delta_angle_signed_single(vfrom: glm.vec2, vto: glm.vec2):
    print(f'vec2_delta_angle_deg_signed(({vfrom.x:.02},{vfrom.y:.02}), ({vto.x:.02},{vto.y:.02})): ', utils.vec2_delta_angle_deg_signed(vfrom, vto))


def test_vec2_delta_angle_unsigned_single(vfrom: glm.vec2, vto: glm.vec2):
    print(f'vec2_delta_angle_deg_unsigned(({vfrom.x:.02},{vfrom.y:.02}), ({vto.x:.02},{vto.y:.02})): ', utils.vec2_delta_angle_deg_unsigned(vfrom, vto))


def test_vec2_delta_angle_signed():
    print('--- test_vec2_delta_angle_signed')

    vfrom = utils.vec2_from_angle_deg(135)
    vto = utils.vec2_from_angle_deg(-135)
    test_vec2_delta_angle_signed_single(vfrom, vto)
    test_vec2_delta_angle_signed_single(vto, vfrom)


def test_vec2_delta_angle_unsigned():
    print('--- test_vec2_delta_angle_unsigned')
    vfrom = utils.vec2_from_angle_deg(135)
    vto = utils.vec2_from_angle_deg(-135)
    test_vec2_delta_angle_unsigned_single(vfrom, vto)
    test_vec2_delta_angle_unsigned_single(vto, vfrom)


def vec_test_rotate_towards():
    v1 = glm.vec2(-1, -1)
    v2 = glm.vec2(0, -1)

    v = glm.vec2(v1)
    while True:
        v = utils.vec2_rotate_towards(v, v2, 5)
        print(v)


def test_wrap():
    print('--- test_wrap')
    x = 2
    print(f'x = {x}')
    x = utils.wrap(x + 1, 0, 3)
    print(f'x = wrap(x+1,0,3) = {x}\n')

    x = 3
    print(f'x = {x}')
    x = utils.wrap(x + 1, 0, 3)
    print(f'x = wrap(x+1,0,3) = {x}\n')

    x = 6
    print(f'x = {x}')
    x = utils.wrap(x + 1, 0, 3)
    print(f'x = wrap(x+1,0,3) = {x}\n')

    x = 1
    print(f'x = {x}')
    x = utils.wrap(x - 2, 0, 3)
    print(f'x = wrap(x-2,0,3) = {x}\n')

    x = -1
    print(f'x = {x}')
    x = utils.wrap(x, 0, 359)
    print(f'x = wrap(x, 0, 360) = {x}\n')

    x = 100.0
    print(f'x = {x}')
    x = utils.wrap(x+0.2, 0, 100)
    print(f'x = wrap(x+0.2, 0, 100) = {x}\n')


def test_wrap_angle_deg_360_single(a):
    print(f'wrap_angle_deg_360({a}): ', utils.wrap_angle_deg_360(a))


def test_wrap_angle_deg_360():
    print('--- test_wrap_angle_deg_360')
    test_wrap_angle_deg_360_single(0)
    test_wrap_angle_deg_360_single(90)
    test_wrap_angle_deg_360_single(-90)


if __name__ == '__main__':
    # quat_test_1()
    # quat_test_2()
    # quat_test_3()
    #test_wrap()
    test_vec_from_angle()
    #test_angle_from_vec()
    #test_wrap_angle_deg_360()
    #test_delta_angle_signed()
    #test_delta_angle_unsigned()
    #test_vec2_delta_angle_signed()
    #test_vec2_delta_angle_unsigned()
    # vec_test_rotate_towards()
