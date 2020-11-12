class Counter:
    def __init__(self):
        self.val = 0

    def __int__(self):
        return self.val

    def __str__(self):
        return str(self.val)
    
    def increment(self):
        self.val += 1

    def reset(self):
        self.val = 0
