import random

def username_from_fio(fio: str) -> str:
    """
    Преобразует ФИО в username вида ФамилияИО000
    """
    if len(fio.split(" ")) == 3:
        return fio.split(" ")[0].upper() + fio.split(" ")[1].upper() + fio.split(" ")[2].upper() + str(random.randint(100, 999))
    elif len(fio.split(" ")) == 2:
        return fio.split(" ")[0].upper() + fio.split(" ")[1].upper() + str(random.randint(100, 999))
    else:
        return fio.split(" ")[0].upper() + str(random.randint(100, 999))
    
    