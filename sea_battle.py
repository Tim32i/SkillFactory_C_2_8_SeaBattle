import random as rnd
import time


# ----------------------------
# Общая функциональность, используемая в нескольких классах


def pos_around_ship(ship):  # поиск клеток вокруг корабля
    # предполагается, что корабль уже 'нормализован' -
    # клетки слева направо или сверху вниз
    pos_lst = []  # список клеток, которые надо пометить
    if len(ship.pos_list) == 1:  # если корабль из 1 клетки, обходим вокруг четыре клетки
        lst_offset_begin = [(0, -1), (-1, 0), (0, 1), (1, 0)]  # список смещений координат относительно тек точки
    else:  # корабль из нескольких клеток
        if ship.pos_list[0].x == ship.pos_list[1].x:  # корабль горизонтальный
            lst_offset_begin = [(1, 0), (0, -1), (-1, 0)]  # смещения для начальной точки
            lst_offset_middle = [(-1, 0), (1, 0)]  # смещения для срединной точки
            lst_offset_end = [(-1, 0), (0, 1), (1, 0)]  # смещения для конечной точки
        else:  # корабль вертикальный
            lst_offset_begin = [(0, -1), (-1, 0), (0, 1)]  # смещения для начальной точки
            lst_offset_middle = [(0, -1), (0, 1)]  # смещения для срединной точки
            lst_offset_end = [(0, -1), (1, 0), (0, 1)]  # смещения для конечной точки
    for i in range(len(ship.pos_list)):  # проход по точкам корабля
        if i == 0:  # начальная точка
            lst_offset = lst_offset_begin
        elif i == len(ship.pos_list) - 1:  # конечная точка
            lst_offset = lst_offset_end
        else:  # срединная точка
            lst_offset = lst_offset_middle
        for elem in lst_offset:  # проход по соседним точкам
            p = Pos(ship.pos_list[i].x + elem[0], ship.pos_list[i].y + elem[1])  # получаем точку
            if 0 < p.x < 7 and 0 < p.y < 7:  # проверка на реальную точку
                pos_lst.append(p)  # добавить точку в список
    return pos_lst


def rem_num_cells(pos_lst, num_lst):  # удаление точек из списка номеров по координатам точек
    for p in pos_lst:
        num = num_cell(p.x, p.y)  # номер точки по координатам
        try:  # отловим исключение, если точка уже удалена
            num_lst.remove(num)  # удаляем точку из списка по номеру точки
        except ValueError:  # если ее уже нет
            pass  # ничего не делаем


def num_cell(x, y):  # номер клетки по координатам
    return (x - 1) * 6 + y

# --------------------------------------------------


class CellError(Exception):                                # Собственное исключение на повторный ход
    pass


class Pos:
    """Координаты точки на поле"""

    def __init__(self, x, y) -> None:
        self.__x = x
        self.__y = y

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, x):
        self.__x = x

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, y):
        self.__y = y

    def __eq__(self, other):
        return self.__x == other.__x and self.__y == other.__y


class Ship:
    """Класс корабля, хранит список точек корабля, сортирует точки слева направо или сверху вниз"""

    def __init__(self, pos_list):
        self.__pos_list = pos_list  # список точек, из которых состоит корабль
        self.norm_ship()  # переупорядочить клетки - слева направо или сверху вниз

    @property
    def pos_list(self):
        return self.__pos_list

    def norm_ship(self):  # 'нормализация' клеток корабля - слева направо или сверху вниз
        if len(self.__pos_list) == 1:  # для корабля из 1 клетки ничего не делаем
            return None
        if self.__pos_list[0].x == self.__pos_list[1].x:  # горизонтальный корабль
            if self.__pos_list[0].y > self.__pos_list[1].y:  # точки в обратном порядке
                self.__pos_list = self.__pos_list[::-1]  # инвертируем список точек
        else:  # вертикальный корабль
            if self.__pos_list[0].x > self.__pos_list[1].x:  # точки в обратном порядке
                self.__pos_list = self.__pos_list[::-1]  # инвертируем список точек


class Ships:
    """Класс эскадры кораблей"""

    def __init__(self) -> None:
        self.__ships_lst = []                                         # список кораблей (пока пустой)
        self.__free_cells_lst = list(range(1, 37))                     # список своб для выбора ячеек по номерам
        self.create_ships()

    @property
    def ships_lst(self):
        return self.__ships_lst

    def create_ships(self):  # метод создания списка кораблей
        """Параметр create_ship - функция создания корабля - или для компьютера, или для игрока"""
        count_ships = 1  # количество кораблей
        for i in range(3, 0, -1):  # i - 3, 2, 1 - размер корабля
            for j in range(count_ships):  # создание count_ships одинаковых кораблей
                while (new_ship := self.create_ship(i)) is None:  # создание корабля (игрока или компа)
                    pass  # пока не будет создан новый корабль
                self.__ships_lst.append(new_ship)  # новый корабль в список кораблей
            count_ships *= 2  # каждый раз удваиваем кол-во кораблей получится 1 3клеточный,
            # 2 2клеточных, и 4 1клеточных

    def create_ship(self, size_ship):
        first_num = rnd.choice(self.__free_cells_lst)  # случайный выбор номера из списка своб клеток
        px = (first_num - 1) // 6 + 1  # координата x из номера клетки
        py = (first_num - 1) % 6 + 1  # координата y из номера клетки
        first_cell = Pos(px, py)  # создание точки из случайного номера
        lst_ships_cand = []  # список кораблей кандидатов
        if size_ship == 1:  # если корабль из одной клетки, корабль создан
            lst_ships_cand.append(Ship([first_cell]))  # корабль-кандидат из одной клетки
        else:  # корабль 2 или 3 клеточный
            lst_vector = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # список направлений, вверх, вправо, вниз, влево
            for v in lst_vector:  # проходим по направлениям - 4 варианта расположения корабля
                lst_cand = []  # список клеток-кандидатов
                for i in range(1, size_ship):  # проверка точек по длине корабля - 1 (1 или 2)
                    px = first_cell.x + i * v[0]  # координата x клетки-кандидата
                    py = first_cell.y + i * v[1]  # координата y клетки-кандидата
                    if num_cell(px, py) in self.__free_cells_lst \
                            and (0 < px < 7 and 0 < py < 7):  # клетка в списке свободных и существует
                        lst_cand.append(Pos(px, py))  # добавляем клетку в список кандидатов
                    else:
                        break  # прерываем данное направление
                else:  # если все направление проверено успешно
                    cand_ship = Ship([first_cell] + lst_cand)  # создаем корабль кандидат
                    lst_ships_cand.append(cand_ship)  # добавляем его в список кораблей кандидатов
        if not lst_ships_cand:  # список кораблей кандидатов пуст
            return None  # возврат None, корабль не создан
        ship_choice = rnd.choice(lst_ships_cand)  # случайный выбор корабля из достойных кандидатов
        lst_rem = ship_choice.pos_list + pos_around_ship(ship_choice)  # получаем объединенный список из клеток
        # нового корабля и его соседних клеток
        rem_num_cells(lst_rem, self.__free_cells_lst)  # удаляем из списка своб клеток
        return ship_choice  # возврат нового корабля


class Board:
    def __init__(self, ships) -> None:
        self.__cells_matrix = [[0 for _ in range(6)] for _ in range(6)]       # пустое поле 6 x 6
        self.__free_cells_lst = list(range(1, 37))                            # список свободных номеров клеток
        self.__ships = ships.ships_lst                            # передаем в класс список кораблей из объекта эскадры
        self.__count_hit = 0                                                  # счетчик подбитых клеток кораблей
        self.__status_last_move = ''                                          # статус поля после последнего хода
                                                                              # (попадание - 'hit', промах - 'miss')
        self.__ships_hit = []                                                 # список подбитых кораблей
        for ship in self.__ships:                                             # расставляем корабли на поле
            for pos in ship.pos_list:
                self.__cells_matrix[pos.x - 1][pos.y - 1] = chr(9632)         # заполняем поле кораблями по клеточно

    @property
    def count_hit(self):
        return self.__count_hit

    @property
    def cells_matrix(self):
        return self.__cells_matrix

    @property
    def status_last_move(self):
        return self.__status_last_move

    @property
    def ships_hit(self):
        return self.__ships_hit

    @property
    def free_sells_lst(self):
        return self.__free_cells_lst

    def shoot(self, pos):                                                # отметка хода на поле
        num = (pos.x - 1) * 6 + pos.y                                    # номер клетки по координатам
        self.__free_cells_lst.remove(num)                                # убираем номер клетки из списка своб клеток
        if self.__cells_matrix[pos.x - 1][pos.y - 1] == 0:
            self.__cells_matrix[pos.x - 1][pos.y - 1] = 'T'              # пометили промах
            self.__status_last_move = 'miss'                             # статус последнего хода - промах
            return 0                                                     # возврат 0, если промах
        elif self.__cells_matrix[pos.x - 1][pos.y - 1] == chr(9632):
            self.__cells_matrix[pos.x - 1][pos.y - 1] = 'X'              # пометили попадание
            self.__count_hit += 1                                        # +1 в счетчик попаданий
            self.__status_last_move = 'hit'                              # статус последнего хода - попадание
            if (ship_hit := self.find_ship_hit()) is not None:           # проверка, нет ли уничтоженного корабля
                pos_lst = pos_around_ship(ship_hit)                      # список точек вокруг подбитого корабля
                for pos in pos_lst:
                    self.__cells_matrix[pos.x - 1][pos.y - 1] = 'T'      # помечаем, в эту точку уже бессмысленно ходить
                rem_num_cells(pos_lst, self.__free_cells_lst)            # удаляем точки из списка свободных клеток
            return 1                                                     # возврат 1, если попадание
        else:
            return None                                                  # повторный ход в ту же клетку - возврат None

    def find_ship_hit(self):                               # проверка оставшихся кораблей на уничтожение после попадания
        for ship in self.__ships:                          # проходим по оставшимся кораблям
            hit_ship = True                                # предполагаем, что тек корабль подбит
            for pos in ship.pos_list:                      # проходим по клеткам корабля
                if self.__cells_matrix[pos.x - 1][pos.y - 1] != 'X':  # если хоть одна клетка не подбита
                    hit_ship = False                                  # корабль не подбит
                    break                                             # останавливаем проверку для данного корабля
            if hit_ship:                                              # выявлен подбитый корабль
                self.__ships_hit.append(ship)                         # помещаем корабль в список подбитых кораблей
                self.__ships.remove(ship)                             # убираем корабль из основного списка кораблей
                return ship                                           # прекращаем проход кораблей и возвращаем подбитый
                                                            # корабль, т.к. за один ход можно добить только один корабль
        return None                                                   # не нашелся подбитый корабль, возврат None


class Display:
    """Отображает поля игроков"""

    def __init__(self):
        pass

    @staticmethod
    def show_boards(player_board, comp_board):                        # отображение досок игрока и компьютера
        lst_str = [
            '        Поле игрока                    Поле компьютера     ',
            '  | 1 | 2 | 3 | 4 | 5 | 6 |        | 1 | 2 | 3 | 4 | 5 | 6 |'
        ]                                                                        # список выводимых на экран строк

        for i in range(6):
            str_user = str_comp = ''                                             # строки досок игрока и компа
            for j in range(6):
                cell = comp_board.cells_matrix[i][j]
                hide_cell = '0' if cell == chr(9632) else cell                   # сокрытие клеток кораблей компа
                str_user += f" {player_board.cells_matrix[i][j]} |"              # заполняем строку из доски игрока
                str_comp += f" {hide_cell} |"                                    # заполняем строку из доски компа
            lst_str.append(f"{i + 1} |{str_user}      {i + 1} |{str_comp}")      # формируем общую строку
        for str_out in lst_str:                                                  # распечатываем список строк для вывода
            print(str_out)

    @staticmethod
    def txt_message(txt):
        print(txt)

    @staticmethod
    def input_message(ask):
        return input(ask)


class PlayerComp:
    def __init__(self, board):
        self.__board = board

    def do_move(self):
        num_cell_shoot = rnd.choice(self.__board.free_sells_lst)     # случайный выбор клетки для выстрела
        px = (num_cell_shoot - 1) // 6 + 1                           # координата x из номера клетки
        py = (num_cell_shoot - 1) % 6 + 1                            # координата y из номера клетки
        pos = Pos(px, py)                                            # создаем точку
        return self.__board.shoot(pos)                               # стреляем по доске с возвратом результата стрельбы


class PlayerUser:
    def __init__(self, board):
        self.__board = board

    def do_move(self):
        while True:
            try:
                lst_pos = list(map(int, Display.input_message('Введите координаты выстрела: ').split()))
                if not (0 < lst_pos[0] < 7 and 0 < lst_pos[1] < 7):                    # контроль правильности координат
                    raise IndexError
                if num_cell(lst_pos[0], lst_pos[1]) not in self.__board.free_sells_lst:  # контроль на свободную клетку
                    raise CellError
            except ValueError:                                                           # неправильный ввод (не int)
                Display.txt_message('Неправильный ввод')
            except IndexError:
                Display.txt_message('Неверные координаты')
            except CellError:                                                               # выбрана несвободная клетка
                Display.txt_message('Выбрана использованная клетка или соседняя с подбитым кораблем')
            else:                                                                       # не возникло никаких исключений
                pos = Pos(lst_pos[0], lst_pos[1])
                return self.__board.shoot(pos)


class GameLogic:

    def __init__(self):
        pass

    @staticmethod
    def run():
        ships_comp = Ships()                                 # создаем эскадру компа
        ships_user = Ships()                                 # создаем эскадру игрока
        comp_board = Board(ships_comp)                       # создаем доску компа
        user_board = Board(ships_user)                       # создаем доску игрока
        player_comp = PlayerComp(user_board)                 # создание игрока-компа с передачей ему доски игрока
        player_user = PlayerUser(comp_board)                 # создание игрока-игрока с передачей ему доски игрока компа
        Display.show_boards(user_board, comp_board)
        Display.txt_message('Игра началась')
        while True:                                          # цикл ходов в игре до чьей-то победы
            while True:                                      # цикл пока игрок не промахнется
                rez = player_user.do_move()
                Display.show_boards(user_board, comp_board)
                if comp_board.count_hit == 11:               # проверка, что все клетки кораблей компа побиты
                    game_over = "Игрок"
                    return game_over
                if rez != 1:                                 # если нет попадания - передать ход оппоненту
                    break
            while True:                                      # цикл пока комп не промахнется
                rez = player_comp.do_move()
                Display.show_boards(user_board, comp_board)
                if user_board.count_hit == 11:               # проверка, что все клетки кораблей игрока побиты
                    game_over = "Компьютер"
                    return game_over
                if rez != 1:
                    break
                time.sleep(1)                      # если комп ходит несколько раз подряд, пауза 1 сек, чтобы было видно


if __name__ == "__main__":
    game_result = GameLogic().run()
    Display.txt_message(f" Выиграл {game_result}!")
