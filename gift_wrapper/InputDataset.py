class InputDataset:
    def __init__(self, vertical, horizon, high, line_w=None, interval_w=None, offset=None, s2b_angle=None, b_angle=None):
        self._vertical = vertical
        self._horizon = horizon
        self._high = high
        self._line_w = line_w
        self._interval_w = interval_w
        self._offset = offset
        self._s2b_angle = s2b_angle
        self._b_angle = b_angle

    def get(self):
        return [self._vertical, self._horizon, self._high, self._line_w, self._interval_w, self._offset, self._s2b_angle, self._b_angle]
