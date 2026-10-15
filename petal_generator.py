import numpy as np
from scipy.interpolate import splprep, splev
from scipy import integrate


def petal_radius(theta, r0, c1, c2, n1, n2):
    return r0 * (1 + c1 * np.cos(n1 * theta) + c2 * np.cos(n2 * theta))


def get_max_radius(r0, c1, c2, n1, n2, num_samples=1000):
    theta = np.linspace(0, 2 * np.pi, num_samples)
    return np.max(petal_radius(theta, r0, c1, c2, n1, n2))


def calculate_required_r0(L, target_phi, c1, c2, n1, n2, r0_min=0.01 / 20, r0_max=0.5 / 20,
                          tolerance=1e-6, max_iterations=100):
    def calculate_fill_ratio(r0):
        theta = np.linspace(0, 2 * np.pi, 1000)
        r = petal_radius(theta, r0, c1, c2, n1, n2)
        area = 0.5 * integrate.trapezoid(r ** 2, theta)
        return area / (L * L)

    max_radius_coefficient = 1 + abs(c1) + abs(c2)
    r0_max = min(r0_max, (L / 2) / max_radius_coefficient)

    low_boundary, high_boundary = r0_min, r0_max
    while high_boundary - low_boundary > 1e-6:
        mid = (low_boundary + high_boundary) / 2
        if get_max_radius(mid, c1, c2, n1, n2) <= L / 2:
            low_boundary = mid
        else:
            high_boundary = mid

    r0_max_valid = low_boundary

    max_phi = calculate_fill_ratio(r0_max_valid)
    if max_phi < target_phi - tolerance:
        return r0_max_valid, max_phi, False

    low, high = r0_min, r0_max_valid
    mid = low
    iterations = 0

    while iterations < max_iterations:
        mid = (low + high) / 2
        phi = calculate_fill_ratio(mid)

        if get_max_radius(mid, c1, c2, n1, n2) > L / 2:
            high = mid
            iterations += 1
            continue

        if abs(phi - target_phi) < tolerance:
            return mid, phi, True

        if phi < target_phi:
            low = mid
        else:
            high = mid

        iterations += 1

    final_r0 = mid
    final_phi = calculate_fill_ratio(final_r0)

    return final_r0, final_phi, get_max_radius(final_r0, c1, c2, n1, n2) <= L / 2


def generate_petal_curve(L, r0, c1, c2, n1, n2, num_points=100, apply_smoothing=True):
    theta = np.linspace(0, 2 * np.pi, num_points)
    r = petal_radius(theta, r0, c1, c2, n1, n2)

    x = r * np.cos(theta)
    y = r * np.sin(theta)

    if apply_smoothing and num_points > 3:
        try:
            tck, u = splprep([x, y], s=0, per=True)
            u_new = np.linspace(0, 1, num_points)
            x_smooth, y_smooth = splev(u_new, tck)
            return x_smooth, y_smooth
        except Exception:
            return x, y

    return x, y
