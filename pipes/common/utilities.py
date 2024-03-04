from shortuuid import ShortUUID


def generate_shortuuid():
    """Generate short identifier for public exposure"""
    _shortuuid = ShortUUID()
    return _shortuuid.random(length=8)
