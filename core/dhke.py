from core.field import Field

class DHKE:
    def __init__(self, p: int, g: int, q: int | None = None):
        self.p = p
        self.g = g
        self.q = q
        self.field = Field(p)

    def generate_public(self, secret: int) -> int:
        return self.field.exp(self.g, secret)

    def validate_public(self, y: int) -> bool:
        if not self.field.is_valid_element(y):
            return False

        if self.q is not None:
            return self.field.exp(y, self.q) == 1

        return True
