# HAMMEL Website — работа в PyCharm

## Структура
- `index.html` — HOME.
- `unternehmen/index.html` — ÜBER UNS.
- `maschinen/`, `loesungen/`, `weltweit/`, `service/`, `karriere/`, `kontakt/`, `aktuelles/` — другие страницы.
- `assets/css/` — стили страниц и компонентов.
- `assets/js/` — интерактивность и анимации.
- `assets/img/`, `assets/video/` — медиафайлы.

## Как открыть
Откройте папку `hammel-redesign` как проект в PyCharm. Запустите локальный сервер из корня проекта: `python3 -m http.server 8000`. Откройте `http://localhost:8000`.

## Форматирование
HTML разбит на строки с отступами, CSS — на блоки и объявления, JS — с помощью синтаксического парсера TypeScript. `.editorconfig` задаёт 2 пробела. Не объединяйте файлы при редактировании — разделение по страницам сохранено.

Примечание: форматирование проверено синтаксически, но визуальное поведение в Safari не тестировалось.
