from configparser import ConfigParser


def config(filename='database.ini', section='postgresql') -> dict:
    """ Loads config file for establishing database connection """
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for p in params:
            db[p[0]] = p[1]
    else:
        raise Exception('Section %1 not found in file %2' % section, filename)

    return db
