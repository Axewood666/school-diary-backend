import random
from transliterate import translit

def username_from_fio(fio: str) -> str:
    """
    Преобразует ФИО в username вида SurnameIO000.
    """
    parts = [part.strip() for part in fio.split(" ") if part.strip()]
    
    translit_parts = []
    for part in parts:
        try:
            translit_part = translit(part, 'ru', reversed=True)
            translit_part = ''.join([c for c in translit_part if c.isalpha()])
            translit_parts.append(translit_part)
        except:
            translit_part = ''.join([c for c in part if c.isalpha()])
            translit_parts.append(translit_part)
    
    surname = translit_parts[0]
    initials = ""
    
    if len(translit_parts) > 1:
        initials += translit_parts[1][0].upper()
    if len(translit_parts) > 2:
        initials += translit_parts[2][0].upper()
    
    random_suffix = str(random.randint(100, 999))
    
    username = f"{surname.capitalize()}{initials}{random_suffix}"
    return username