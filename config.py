import ConfigParser

class ConfigurationError(Exception):
    def __init__(self, value):
        self.value = value
            
    def __str__(self):
        return 'ConfigurationError: %s' % self.value
            
class Config(object):
    
    def __init__(self, filename, load=True, ignore_errors=False):
        self.filename = filename
          
        self.parser = ConfigParser.RawConfigParser()
            
        if load:
            self.parser.read(self.filename)
                
            if not ignore_errors:
                if not self.parser.has_section('core'):
                   raise ConfigurationError('Core section missing.')
        
    def save(self):
        cfgfile = open(self.filename, 'w')
        self.parser.write(cfgfile)
        cfgfile.flush()
        cfgfile.close()
            
    def add_section(self, name):
            
        try:
            return self.parser.add_section(name)
        except ConfigParser.DubplicateSectionError:
            return False
            
    def has_option(self, section, name):
        return self.parser.has_option(section, name)
        
    def has_section(self, name):
        return self.parser.has_section(name)
                        
    class ConfigSection(object):
        def __init__(self, name, items, parent):
            object.__setattr__(self, '_name', name)
            object.__setattr__(self, '_parent', parent)
            for item in items:
                value = item[1].strip()
                if not value.lower() == 'none':
                    if value.lower() == 'false':
                        value = False
                    object.__setattr__(self, item[0], value)
        def __getattr__(self, name):
            return None
            
        def __setattr__(self, name, value):
            object.__setattr__(self, name, value)
            if type(value) is list:
                value = ','.join(value)
            self._parent.parser.set(self._name, name, value)
            
        def get_list(self, name):
            value = getattr(self, name)
            if not value:
                return []
            if isinstance(value, basestring):
                value = value.split(',')
                setattr(self, name, value)
                return value
                
    def __getattr__(self, name):
        if name in self.parser.sections():
            items = self.parser.items(name)
            section = self.ConfigSection(name, items, self)
            setattr(self, name, section)
            return section
        elif self.parser.has_option('core', name):
            return self.parser.get('core', name)
        else:
            raise AttributeError("%r object has no attribute %r" % (type(self).__name__, name))
            
  
