![yatube-yandex-youtube](https://user-images.githubusercontent.com/94482915/175423560-8f9833ed-fcc9-4655-b0e5-e9cff0d58412.png)


# Социальная сеть Yatube

### Для чего этот проект:
Социальная сеть позволяет размещать личные дневники. Социальная сеть позволяет завести свою страницу. При переходе на страницу автора отображаются все посты автора. Можно подписыаться на любимых авторов и оставлять комментарии под постами. К постам можно добавлять изображения. При размещении поста можно указывть группу и просматривать выдачу постов по группам.
### Технологии:
- Python 3.7
- Django 3.0
- Unittest

### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

```
git@github.com:Andr3w-k/yatube_final.git
```

```
cd yatube_final
```

Шаблон наполнения env-файла:
```
SECRET_KEY = '***'
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
cd yatube

python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
