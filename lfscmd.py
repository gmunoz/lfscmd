def chapter_paths(sub_dir):
    from pathlib import Path

    top = Path(sub_dir)

    if not top.is_dir():
        return []

    chapters = []
    for sub_path in top.iterdir():
        if sub_path.name.startswith("chapter"):
            chapters.append(sub_path)

    return chapters

def ent_paths(sub_dir):
    from pathlib import Path
    top = Path(sub_dir)
    if not top.is_dir():
        return []

    entity_paths = []
    for sub_path in top.iterdir():
        if sub_path.name.endswith(".ent"):
            entity_paths.append(sub_path)

    return entity_paths

def __parse_entity(parts):
    """
    Given an array of XML entity string parts, parse out the key and value.
    """
    if len(parts) >= 3 and parts[0] == '<!ENTITY':
        pass
    else:
        return None

    i = 1
    while i < len(parts):
        while i < len(parts) and parts[i] == '':
            i += 1
        if i >= len(parts):
            print(f"error: Parsing {parts}: Unable to parse key (left hand side) of an XML entity string")
            return None
        key = parts[i]
        i += 1
        if key == '%' and i < len(parts):
            if not len(parts[i]) > 0:
                print(f"error: Parsing key with prefixed % doesn't have a matching string name at position {i}")
                return None
            # concat the % and following string as the key
            key += parts[i]
            i += 1
        print(f"debug: key is {key} at position {i}")
        while i < len(parts) and parts[i] == '':
            i += 1
        if i >= len(parts):
            print(f"error: Parsing {parts}: Unable to parse value (right hand side) of an XML entity string")
            return None
        if not parts[i].startswith('"'):
            print(f"error: Parsing {parts}: Value doesn't start with a leading '\"' at position {i}")
            return None
        value = parts[i][1:]
        i += 1
        term = value.find('">')
        if not term == -1:
            value = value[:term] + '">'
        print(f"value so far is {value} and i of {i}")
        while i < len(parts) and not value.endswith('">'):
            value += parts[i]
            term = value.find('">')
            if not term == -1:
                value = value[:term] + '">'
            i += 1

        if value.endswith('">'):
            value = value[:-2]
        else:
            print(f"error: Parsing {parts}: Unable to parse multi-value string with expected string termination '\">' at position {i}")
            return None

        return (key, value)

def resolve_ent(ent_path):
    """
    Read the path and place key value pairs of XML entities into a dictionary.
    Simplification: To avoid XML parsing, parse as <!ENTITY <key> "<value>"
    Algorithm:
      Split every line by ' ' (literal space).
      If the first element is '<!ENTITY', then parse as an entity, otherwise skip.
        A valid entity is:
        <!ENTITY followed by one or more spaces,
        Followed by a non-zero string,
        Followed by one or more spaces,
        Followed by a string that starts with '"&',
        Followed by one or more characters,
        If the first string ends with '">', then we have a full value,
        otherwise parse subsequent values until an end is matched.
    """
    ents = {}
    with open(ent_path, 'r') as ent_f:
        for line in ent_f.readlines():
            parts = line.rstrip().split(' ')
            maybe_entity = __parse_entity(parts)
            if maybe_entity is not None:
                ents[maybe_entity[0]] = maybe_entity[1]

    return ents

def merge_entity_maps(ary):
    result = {}
    for m in ary:
        for key in m:
            if key in result:
                print(f"error: Merging maps together resulted in duplicate key for {key}")
                return None
            result[key] = m[key]

    return result

def __eval_key(key, ent_map, debug=True):
    if key not in ent_map:
        return None

    value = ent_map[key]
    i = 0
    elements = []
    while i < len(value):
        if value[i] == '&':
            orig_i = i
            i += 1
            elem = ''
            while i < len(value) and value[i] != ';':
                elem += value[i]
                i += 1
            if i < len(value) and value[i] == ';':
                i += 1
                elements.append(elem)
                if debug:
                    print(f"debug: found parameter named {elem} starting at position {orig_i} and ending at {i - 1} in '{value}'")
            else:
                print(f"warning: Located '&' at position {orig_i} but unable to find ';' terminator... ignoring any parsed value {elem}")
        else:
            i += 1

    for e in elements:
        sub_str = __eval_key(e, ent_map)
        if debug:
            print(f"When parsing '{ent_map[key]}', found parameter '{e}' to be replaced with '{sub_str}'")
        ent_map[key] = ent_map[key].replace(f"&{e};", sub_str)
        if debug:
            print(f"debug: new value is '{ent_map[key]}'")

    return ent_map[key]

def eval_entity(ent_map):
    # Do DFS based search for every key in the map.
    # A DFS will iterate over every &...; string value and
    # call the DFS function that returns a string with all
    # sub-values substituted.
    for key in ent_map:
        __eval_key(key, ent_map)

def start():
    print("Hello")
    chapters = chapter_paths("lfs.git")
    e_paths = ent_paths("lfs.git")
    all_ent_vars = []
    for e_path in e_paths:
        ents = resolve_ent(e_path)
        all_ent_vars.append(ents)

    entities = merge_entity_maps(all_ent_vars)
    if 'generic-versiond' not in entities:
        # NOTE: This can be an LFS version identifier, but default to the
        # "latest" development version if it doesn't exist. Make this a parameter.
        entities['generic-versiond'] = 'development'

    import pprint
    pprint.pprint(entities)
    #ent = __parse_entity(['<!ENTITY', 'errata', '', '', '', '', '', '', '', '', '', '"&lfs-root;lfs/errata/&version;/">'])
    #print(ent)
    eval_entity(entities)
    pprint.pprint(entities)

if __name__ == "__main__":
    start()
