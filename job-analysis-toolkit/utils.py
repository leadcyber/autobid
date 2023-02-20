def parseInt(sin):
  import re
  m = re.search(r'^(\d+)[.,]?\d*?', str(sin))
  return int(m.groups()[-1]) if m and not callable(sin) else None