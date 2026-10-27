class Converter:
    @staticmethod
    def do(x: float) -> int:
        if x >= 100.7:
            return 1000

        elif 0 < x < 100.7:
            return int(x)

        elif x == 0.0:
            raise ValueError("Число не должно быть равно нулю")

        elif -30.4 <= x < 0:
            return int(x) - 5

        elif x <= -30.5:
            return -2000