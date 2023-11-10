class HashTable:
    def __init__(self, size=10):
        self.size = size
        self.table = [None] * size

    def _hash(self, key):
        return sum(ord(char) for char in key) % self.size

    def _load_factor(self):
        return sum(1 for i in range(len(self.table)) if self.table[i] is not None) / self.size

    def add(self, value):
        self.resize()
        key = self._hash(value)
        if self.table[key] is None:
            self.table[key] = []
        if value not in self.table[key]:
            self.table[key].append(value)

    def contains(self, value):
        key = self._hash(value)
        if self.table[key] is not None:
            if value in self.table[key]:
                return True
        return False

    def get_position(self, value):
        key = self._hash(value)
        if self.table[key] is not None:
            return key
        return None

    def delete(self, value):
        key = self._hash(value)
        if self.table[key] is not None:
            for i in range(len(self.table[key])):
                if self.table[key][i] == value:
                    self.table[key].pop(i)
                    return True
        return False

    def resize(self):
        if self._load_factor() > 0.7:
            self.size *= 2
            new_table = [None] * self.size
            for i in range(len(self.table)):
                if self.table[i] is not None:
                    for j in range(len(self.table[i])):
                        key = self._hash(self.table[i][j])
                        if new_table[key] is None:
                            new_table[key] = []
                        new_table[key].append(self.table[i][j])
            self.table = new_table

    def __str__(self):
        return str(self.table)


