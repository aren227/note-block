def time_digits(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds // 60) % 60
    s = seconds % 60
    if h > 0:
        return "{}:{:02d}:{:02d}".format(h, m, s)
    return "{:02d}:{:02d}".format(m, s)


def time_approximated(seconds: int) -> str:
    if seconds >= 3600:
        return "{}시간".format(seconds // 3600)
    if seconds >= 60:
        return "{}분".format(seconds // 60)
    return "{}초".format(seconds)
