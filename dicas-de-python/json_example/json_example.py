import json
from io import StringIO
from pprint import pprint


def json_to_string_with_dumps(my_dict):
    '''
    Serializa (encode) objeto para string no formato JSON.
    '''
    return json.dumps(my_dict, indent=4)


def json_to_string_with_dump_stringio(my_dict):
    '''
    Serializa (encode) objeto para string no formato JSON usando StringIO.
    '''
    io = StringIO()
    json.dump(my_dict, io, indent=4)
    return io.getvalue()


def json_to_file_with_dump_open_file(filename, my_dict):
    '''
    Serializa (encode) objeto para arquivo no formato JSON usando open.
    '''
    with open(filename, 'w') as f:
        json.dump(my_dict, f, indent=4)


def string_to_json_with_loads(text):
    '''
    Deserializa (decode) string no formato JSON para objeto.
    '''
    return json.loads(text)


def string_to_json_with_load_stringio(text):
    '''
    Deserializa (decode) string no formato JSON para objeto usando StringIO.
    '''
    io = StringIO(text)
    return json.load(io)


def file_to_json_with_load_open_file(filename):
    '''
    Deserializa (decode) string no formato JSON para arquivo usando open.
    '''
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


if __name__ == '__main__':
    # Serialize (encode)

    my_dict = {
        "name": "Elliot",
        "age": 25
    }
    print(json_to_string_with_dumps(my_dict))
    print(type(json_to_string_with_dumps(my_dict)))

    my_dict = {
        "name": "Elliot",
        "full_name": {"first_name": "Elliot", "last_name": "Alderson"},
        "items": [1, 2.5, "a"],
        "pi": 3.14,
        "active": True,
        "nulo": None
    }
    print(json_to_string_with_dump_stringio(my_dict))
    print(type(json_to_string_with_dump_stringio(my_dict)))

    filename = '/tmp/file.txt'
    my_dict = {
        "name": "Elliot",
        "full_name": {"first_name": "Elliot", "last_name": "Alderson"},
        "items": [1, 2.5, "a"],
        "pi": 3.14,
        "active": True,
        "nulo": None
    }
    json_to_file_with_dump_open_file(filename, my_dict)

    # Deserialize (decode)

    text = """
    {
        "name": "Darlene",
        "age": 27
    }
    """
    pprint(string_to_json_with_load_stringio(text))
    print(type(string_to_json_with_load_stringio(text)))

    pprint(string_to_json_with_loads(text))
    print(type(string_to_json_with_loads(text)))

    pprint(file_to_json_with_load_open_file(filename))
