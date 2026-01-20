import json
import os


"""
Модуль реализует класс, позволяющий работать со словарем, чьи значения сохраняются в файле.
"""


class jdict:
    """
    Реализация словаря, значения которого хранятся на диске, а ключи в оперативной памяти.
    Значения ограничиваются структурами, поддерживающими сериализацию и десериализацию в формате JSON.
    Типы ключей соответствуют стандартам стандартного словаря Python.
    """

    def __init__(self):
        """
        Создает новый экземпляр класса для работы с файловым словарем формата JSON.
        """
        self.pathtodict = ""
        self.jda = None
        self.jdb = None
        self.dpos = dict()
        self.bytes = 0
        self.isopen = False

    def push(self, key, value):
        """
        Добавляет новую запись в словарь.

        :param key: Ключ записи.
        :type key: any
        :param value: Значение записи.
        :type value: any
        :return: True, если пара была успешно добавлена, иначе False.
        :rtype: bool
        """
        if key in self.dpos:
            return False
        else:
            self.jdb.seek(self.bytes)
            self.dpos[key] = self.jdb.tell()
            self.jdb.write(json.dumps(value) + '\n')
            self.bytes = self.jdb.tell()
            return True

    def get(self, key):
        """
        Возвращает значение по указанному ключу.

        :param key: Ключ искомой записи.
        :type key: any
        :return: Значение, соответствующее данному ключу, либо пустой словарь, если ключ отсутствует.
        :rtype: any
        """
        if key in self.dpos:
            pos = self.dpos[key]
            self.jdb.seek(pos)
            line = self.jdb.readline()
            try:
                return json.loads(line)
            except Exception:
                return dict()
        else:
            return dict()

    def contains(self, key):
        """
        Проверяет наличие ключа в словаре.

        :param key: Ключ для проверки принадлежности.
        :type key: any
        :return: True, если ключ присутствует в словаре, иначе False.
        :rtype: bool
        """
        return key in self.dpos

    def connect(self, pathtodict):
        """
        Подключается к файловому словарю и загружает ключи в оперативную память.

        :param pathtodict: Путь к файловому словарю.
        :type pathtodict: str
        """
        jdap = f"{pathtodict}.jda"
        jdbp = f"{pathtodict}.jdb"
        if not os.path.exists(jdap):
            open(jdap, 'a').close()
        if not os.path.exists(jdbp):
            open(jdbp, 'a').close()
        self.jda = open(jdap, 'a+')
        self.jdb = open(jdbp, 'a+')
        if self.jda.tell() == 0:
            self.dpos = dict()
        else:
            self.jda.seek(0)
            sdict = json.loads(self.jda.readline())
            self.dpos = {int(k): v for k, v in sdict.items()}
        self.bytes = self.jdb.tell()
        self.isopen = True

    def beginRestore(self):
        """
        Начинает процесс восстановления ключей словаря.
        """
        self.jdb.seek(0)

    def next(self):
        """
        Чтение следующего элемента из базы данных словаря.

        :return: Контент и позиция элемента в файле.
        :rtype: tuple(any, int)
        """
        line = self.jdb.readline()
        if line != '' and len(line) > 1:
            return (json.loads(line), self.jdb.tell())
        else:
            return (dict(), 0)

    def rekey(self, key, pos):
        """
        Восстанавливает поврежденные ключи словаря.

        :param key: Новый ключ.
        :type key: int
        :param pos: Новая позиция в файле.
        :type pos: int
        """
        self.dpos[key] = pos

    def close(self):
        """
        Закрывает подключение к словарю и сохраняет изменения на диск.
        """
        if self.isopen:
            self.jda.truncate(0)
            self.jda.write(json.dumps(self.dpos))
            self.jda.close()
            self.jdb.close()

    def flush(self):
        """
        Сохраняет текущее состояние словаря на диск.
        """
        if self.isopen:
            self.jda.truncate(0)
            self.jda.write(json.dumps(self.dpos))
            self.jda.flush()
            self.jdb.flush()

    def clear(self):
        """
        Полностью очищает словарь.
        """
        self.dpos = dict()
        self.bytes = 0
        self.jda.truncate(0)
        self.jdb.truncate(0)
        self.jdb.truncate(0)