def returnit(func, obj):
    """
    Pass `obj` to `func` and then return `obj`
    """
    func(obj)
    return obj
