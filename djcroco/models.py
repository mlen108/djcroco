try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([], ["^djcroco\.fields\.CrocoField"])
