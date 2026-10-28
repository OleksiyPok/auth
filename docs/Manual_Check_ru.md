# Ручная проверка сервиса авторизации

Пошаговое руководство по первому запуску и ручной проверке всех реализованных операций: вход, способы входа (Link, Unlink, Merge), сессии, 2FA, деактивация и purge, защита.

Проверка идёт через Swagger в браузере. Автотесты не нужны.

## Как пользоваться документом

- Выполняйте разделы по порядку: следующие используют пользователей и данные из предыдущих.
- В каждой таблице три колонки: **Шаг**, **Действие**, **Ожидаемый результат**. Если результат другой, отметьте шаг как проваленный и действуйте по разделу 13.
- Все команды рассчитаны на Windows PowerShell. Каждая команда выполняется отдельно.
- Все адреса API начинаются с `/api/v1`. Полный адрес эндпоинта на локальной машине: `http://127.0.0.1:8000/api/v1/...`.
- Коды в таблицах (`USER_ALREADY_EXISTS` и т. д.) смотрите в поле `code` тела ошибки.

## Содержание

1. Подготовка окружения
2. Запуск и состояние сервиса
3. Регистрация и вход по username
4. Регистрация и вход по email
5. Токены, профиль и сессии
6. Link: добавление способов входа
7. Unlink: удаление способов входа
8. Двухфакторная аутентификация
9. Merge: объединение аккаунтов
10. Деактивация и purge
11. Свежая сессия и лимиты частоты
12. Очистка временных записей
13. Если что-то не работает
14. Итоговая таблица проверки

---

## 1. Подготовка окружения

**Что проверяем:** сервис устанавливается и стартует на чистой базе. Это первый настоящий запуск, поэтому ошибки на этом этапе ожидаемы.

### 1.1. Установка

Откройте PowerShell в корне проекта и выполните по отдельности:

```powershell
python -m venv .venv
```
```powershell
.venv\Scripts\Activate.ps1
```
```powershell
python -m pip install -r requirements.txt
```

Если PowerShell запрещает запуск скриптов, выполните один раз `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` и повторите активацию.

### 1.2. Файл `.env`

Создайте файл `.env` в корне проекта (рядом с `README.md`). Для проверки без Google достаточно заглушек в Google-параметрах.

Сгенерируйте секрет для токенов:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Содержимое `.env` (подставьте сгенерированный секрет):

```
JWT_SECRET_KEY=ВСТАВЬТЕ_СГЕНЕРИРОВАННЫЙ_СЕКРЕТ
SUPERADMIN_LOGIN=superadmin
SUPERADMIN_PASSWORD=Sup3rAdmin!123
SUPERADMIN_EMAIL=superadmin@example.com
GOOGLE_CLIENT_ID=dummy
GOOGLE_CLIENT_SECRET=dummy
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/api/v1/google/auth/callback
EMAIL_SERVICE=dummy
FRESH_SESSION_MINUTES=15
CLEANUP_INTERVAL_SECONDS=3600
```

Значения `FRESH_SESSION_MINUTES` и `CLEANUP_INTERVAL_SECONDS` в разделах 11 и 12 временно меняются; после изменения `.env` сервис нужно перезапускать.

### 1.3. Чистая база

Файл базы `app.db` лежит в корне проекта. Перед первым запуском его не должно быть:

```powershell
Remove-Item app.db -ErrorAction SilentlyContinue
```

Полный сброс состояния в любой момент: остановить сервис (Ctrl+C), удалить `app.db`, запустить заново. Это также сбрасывает счётчики лимитов, они хранятся в памяти процесса.

### 1.4. Запуск

```powershell
python -m app.main
```

Сервис слушает `http://127.0.0.1:8000`. Swagger открывается по адресу `http://127.0.0.1:8000/docs`.

### 1.5. Письма с кодами

Пока `EMAIL_SERVICE=dummy`, письма не отправляются, а пишутся в файл `logs\email_dummy_logs\emails_ГГГГ-ММ-ДД.log`. Все коды подтверждения берутся оттуда. Показать последние письма:

```powershell
Get-Content (Get-ChildItem logs\email_dummy_logs | Sort-Object LastWriteTime | Select-Object -Last 1).FullName -Tail 25
```

В каждом письме строка `To:` показывает адресата, а `Your verification code is: NNNNNN` содержит код.

### 1.6. Работа с токенами в Swagger

1. Вызовите вход (`POST /api/v1/auth/login`) через **Try it out**: поля `username` и `password` (остальные поля формы пустые).
2. Из ответа скопируйте `access_token`.
3. Нажмите **Authorize** вверху страницы, в блоке **Authentication** вставьте токен (без слова `Bearer`), нажмите **Authorize** и **Close**.
4. Теперь все защищённые запросы идут от этого пользователя. Чтобы сменить пользователя, нажмите **Authorize**, **Logout** в блоке и вставьте другой токен.

Токен действует 15 минут (`ACCESS_TOKEN_EXPIRE_MINUTES`). После истечения получите новый входом.

### 1.7. Тестовые данные

Во всех проверках используется один пароль для тестовых пользователей: `Passw0rd!123`.

| Пользователь | Способ входа | Роль |
|---|---|---|
| `superadmin` | username (из `.env`) и email `superadmin@example.com` | superadmin |
| `alice` | username `alice` | user |
| `bob` | email `bob@example.com` | user |

Пользователи `carol`, `dave` и другие создаются в соответствующих разделах.

### 1.8. Проверка базы (по желанию)

Для разделов 10 и 12 нужен просмотр строк в базе. Создайте временный файл `scripts\check_db.py`:

```python
import sqlite3
import sys

connection = sqlite3.connect("app.db")
for row in connection.execute(sys.argv[1]).fetchall():
    print(row)
```

Запуск, например:

```powershell
python scripts\check_db.py "select id, role, status from users"
```

После проверки файл `scripts\check_db.py` удалите.

---

## 2. Запуск и состояние сервиса

**Что проверяем:** приложение стартует, база создаётся, суперадмин появляется, служебные эндпоинты отвечают.

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 2.1 | Запустить `python -m app.main` на чистой базе | В консоли нет ошибок и трассировок, есть `App starting...` и сообщение uvicorn о запуске |
| 2.2 | Открыть `http://127.0.0.1:8000/docs` | Swagger открывается, видны группы Auth, Identities, Two-Factor Authentication, Sessions, Users и другие |
| 2.3 | `GET /health` | 200 |
| 2.4 | `GET /health/ready` | 200, база доступна |
| 2.5 | Проверить файл `app.db` в корне | Файл создан |
| 2.6 | Войти суперадмином: `POST /api/v1/auth/login`, `username=superadmin`, `password=Sup3rAdmin!123` | 200, в ответе `access_token`, `refresh_token`, `requires_two_factor: false` |
| 2.7 | Авторизоваться токеном (п. 1.6), вызвать `GET /api/v1/users/me` | 200, `role: superadmin`, `status: active` |
| 2.8 | Остановить сервис (Ctrl+C) и запустить снова | Запуск без ошибок; второй суперадмин не создаётся: `python scripts\check_db.py "select count(*) from users"` даёт `(1,)` |
| 2.9 | Войти суперадмином по email: `POST /api/v1/auth/email/login`, `username=superadmin@example.com` (в это поле формы вводится email) | 200 и токены |

---

## 3. Регистрация и вход по username

**Что проверяем:** создание пользователя с username, вход, ошибки входа.

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 3.1 | `POST /api/v1/auth/register`: `{"username":"alice","password":"Passw0rd!123","first_name":"Alice","last_name":"Test"}` | 201, ответ с `id`, `username: alice`, `role: user` |
| 3.2 | Повторить тот же запрос | 409 (пользователь уже существует) |
| 3.3 | Повторить с `"username":"  ALICE  "` (пробелы и верхний регистр) | 409: имя нормализуется (`strip` + `casefold`), это тот же пользователь |
| 3.4 | `POST /api/v1/auth/login`: `alice` / `Passw0rd!123` | 200, `access_token`, `refresh_token`, `requires_two_factor: false` |
| 3.5 | Вход с `ALICE` и тем же паролем | 200: регистр имени не важен |
| 3.6 | Вход с неверным паролем | 401, `code: INVALID_CREDENTIALS` |
| 3.7 | Вход с несуществующим username | 401, тот же `code: INVALID_CREDENTIALS` (ответ не должен отличаться от шага 3.6) |
| 3.8 | `GET /api/v1/users/me` с токеном alice | 200, `first_name: Alice`, `role: user`, `status: active` |
| 3.9 | `GET /api/v1/users/me` без токена | 401 |
| 3.10 | `GET /api/v1/identities` с токеном alice | 200, один элемент: `type: username`, `display_identifier: alice` |

Запомните `id` пользователя alice из шага 3.1: он нужен в разделах 9 и 10.

---

## 4. Регистрация и вход по email

**Что проверяем:** регистрация с подтверждением кодом, повторная отправка, ошибки кода.

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 4.1 | `POST /api/v1/auth/email/register`: `{"email":"bob@example.com","password":"Passw0rd!123","first_name":"Bob","last_name":"Test"}` | 202, в ответе `registration_id` и `expires_at` |
| 4.2 | Открыть лог писем (п. 1.5) | Письмо на `bob@example.com` с темой `Confirm your email registration`, 6-значным кодом и ссылкой вида `http://localhost:3000/register/confirm?registration_id=...` с тем же `registration_id` |
| 4.3 | Войти по email до подтверждения: `POST /api/v1/auth/email/login`, `username=bob@example.com` | 401, `INVALID_EMAIL_CREDENTIALS`: пока код не введён, пользователя нет |
| 4.4 | `POST /api/v1/auth/email/register/confirm` с `registration_id` и неверным кодом `000000` | 401, `INVALID_EMAIL_VERIFICATION_CODE` |
| 4.5 | Сразу `POST /api/v1/auth/email/register/resend` с `registration_id` | 429, `EMAIL_VERIFICATION_RESEND_TOO_EARLY` (пауза 60 секунд) |
| 4.6 | Подождать 60 секунд, повторить resend | 202, в логе новое письмо с новым кодом; старый код больше не подходит |
| 4.7 | Подтвердить `register/confirm` кодом из нового письма | 201, в ответе `email: bob@example.com`, `role: user` |
| 4.8 | Повторно подтвердить тем же кодом | 404, `EMAIL_REGISTRATION_NOT_FOUND` |
| 4.9 | Войти по email: `POST /api/v1/auth/email/login`, `username=bob@example.com`, пароль `Passw0rd!123` | 200, токены |
| 4.10 | Вход с адресом `  BOB@Example.com ` | 200: адрес нормализуется |
| 4.11 | Зарегистрировать тот же адрес повторно (`email/register`) и подтвердить | Ожидается отказ: 409 (пользователь уже существует), либо на этапе регистрации, либо при подтверждении |
| 4.12 | Пять раз подряд ввести неверный код при новой регистрации (другой адрес, например `eve@example.com`) | На пятой (или шестой) попытке 429, `EMAIL_VERIFICATION_TOO_MANY_ATTEMPTS`; верный код после этого не принимается |
| 4.13 | `GET /api/v1/identities` с токеном bob | 200, один элемент `type: email`, `display_identifier` в замаскированном виде (`b***@example.com`) |

---

## 5. Токены, профиль и сессии

**Что проверяем:** обновление токенов, выход, список сессий, отзыв сессий, изменение профиля.

Войдите alice два раза (два разных входа создают две сессии) и сохраните оба ответа: `token1` и `token2` (access и refresh каждого).

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 5.1 | `GET /api/v1/sessions` с `token1` | 200, не меньше двух активных сессий alice |
| 5.2 | `POST /api/v1/auth/refresh`: `{"refresh_token":"<refresh первого входа>"}` | 200, новая пара токенов |
| 5.3 | `GET /api/v1/users/me` с новым access-токеном | 200 |
| 5.4 | `POST /api/v1/auth/refresh` с произвольной строкой | 401, `INVALID_REFRESH_TOKEN` |
| 5.5 | `PATCH /api/v1/users/me`: `{"first_name":"Alicia"}` | 200, имя изменено; `GET /users/me` показывает `Alicia` |
| 5.6 | `POST /api/v1/sessions/{session_id}/revoke` для второй сессии (id берётся из списка `GET /sessions`) | 204 |
| 5.7 | Любой защищённый запрос токеном отозванной сессии | 401 (`SESSION_REVOKED` или `INVALID_TOKEN`) |
| 5.8 | Отозвать чужую сессию (id сессии bob) токеном alice | 403 или 404, но не 204 |
| 5.9 | `POST /api/v1/auth/logout` с актуальным токеном alice | 204 |
| 5.10 | Запрос с этим же access-токеном после выхода | 401 |
| 5.11 | Войти alice два раза и вызвать `POST /api/v1/sessions/revoke_all_session` | 204; оба прежних токена перестают работать (401), новый вход работает |

После раздела 5 войдите alice заново и держите свежий токен.

---

## 6. Link: добавление способов входа

**Что проверяем:** пользователь с одним способом входа добавляет другой, защита от конфликтов, требование свежей сессии.

Alice сейчас имеет только username. Вход должен быть выполнен недавно (в пределах `FRESH_SESSION_MINUTES`, то есть 15 минут): иначе Link вернёт 403 `FRESH_SESSION_REQUIRED`.

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 6.1 | Токеном alice: `POST /api/v1/identities/email`: `{"email":"alice@example.com","password":"Passw0rd!123"}` | 202, в ответе `challenge_id` |
| 6.2 | Лог писем | Письмо на `alice@example.com` с кодом |
| 6.3 | `GET /api/v1/identities` до подтверждения | Всё ещё один способ входа (username) |
| 6.4 | `POST /api/v1/identities/email/confirm` с `challenge_id` и неверным кодом | 401, `INVALID_EMAIL_VERIFICATION_CODE` |
| 6.5 | Подтвердить верным кодом | 201, в ответе `type: email` |
| 6.6 | `GET /api/v1/identities` | Два элемента: username и email |
| 6.7 | Выйти и войти по email: `POST /auth/email/login`, `alice@example.com` | 200: новый способ входа работает, это тот же пользователь (`GET /users/me` показывает `Alicia`) |
| 6.8 | Link email повторно (у alice уже есть email): `POST /identities/email` | 409, `IDENTITY_TYPE_CONFLICT` |
| 6.9 | Токеном bob (у него только email): `POST /api/v1/identities/username`: `{"username":"bob","password":"Passw0rd!123"}` | 201, `type: username`, `display_identifier: bob` |
| 6.10 | Токеном bob: Link username с уже занятым именем `{"username":"alice","password":"Passw0rd!123"}` у пользователя, у которого username ещё нет (создайте пользователя `frank` по email и попробуйте) | 409, `IDENTITY_CONFLICT` |
| 6.11 | Токеном bob повторно Link username (он у него уже есть) | 409, `IDENTITY_TYPE_CONFLICT` |
| 6.12 | Токеном bob: Link email с адресом, которым уже пользуется alice (`alice@example.com`) у пользователя без email-способа | 409, `IDENTITY_CONFLICT` на этапе подтверждения или запроса |
| 6.13 | Link без токена | 401 |
| 6.14 | `POST /api/v1/identities/google` токеном пользователя без Google | 200, в ответе `authorization_url` (при заглушках `dummy` реальный вход через Google не пройдёт, ограничиваемся получением ссылки) |

**Google (необязательно).** Полная проверка входа и привязки через Google возможна только с настоящими `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` и `GOOGLE_REDIRECT_URI`. Если они есть: `GET /api/v1/google/auth/login` даёт ссылку, после входа в Google callback `/api/v1/google/auth/callback` возвращает токены. Если email Google совпадает с существующей email-идентичностью, а пользователь новый, в ответе `email_match: true`, и автоматической привязки нет.

---

## 7. Unlink: удаление способов входа

**Что проверяем:** безопасное удаление способа входа и отзыв связанных сессий.

Состояние: alice имеет username и email (после шага 6.5). Войдите alice **по username** и сохраните этот токен как `tokenU`. Войдите alice **по email** и сохраните токен как `tokenE`. Из `GET /identities` запишите `id` username-способа (`idU`) и email-способа (`idE`). Вход должен быть свежим (до 15 минут).

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 7.1 | `tokenU`: `DELETE /api/v1/identities/idU` (удаление способа, через который вошли) | 409, `CURRENT_IDENTITY` |
| 7.2 | `tokenU`: `DELETE /api/v1/identities/неизвестный-id` | 404, `IDENTITY_NOT_FOUND` |
| 7.3 | `tokenU`: `DELETE /api/v1/identities/<id любого способа bob>` | 403, `IDENTITY_NOT_OWNED` |
| 7.4 | `tokenU`: `DELETE /api/v1/identities/idE` | 204 |
| 7.5 | `tokenU`: `GET /api/v1/identities` | Остался один способ: username |
| 7.6 | `tokenE`: `GET /api/v1/users/me` (сессия удалённого способа) | 401: сессии способа отозваны вместе с ним |
| 7.7 | Вход по email `alice@example.com` | 401, `INVALID_EMAIL_CREDENTIALS`: способа входа больше нет |
| 7.8 | `tokenU`: `DELETE /api/v1/identities/idU` (последний способ) | 409, `LAST_IDENTITY` (а не `CURRENT_IDENTITY`: у единственного способа сначала срабатывает проверка последнего) |
| 7.9 | `tokenU`: `DELETE` без свежей сессии (см. раздел 11) | 403, `FRESH_SESSION_REQUIRED` |
| 7.10 | Вернуть email alice: Link email заново (шаги 6.1–6.5) | Два способа входа снова есть |

---

## 8. Двухфакторная аутентификация

**Что проверяем:** добавление и подтверждение метода, включение и отключение 2FA, вход с кодом, повтор кода, recovery-коды, удаление метода.

Подготовка: alice с двумя способами входа (username и email), свежий вход по username (токен `tokenA`).

### 8.1. Методы

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 8.1.1 | `GET /api/v1/auth/2fa/status` | 200, `enabled: false`, `methods: []` |
| 8.1.2 | `POST /api/v1/auth/2fa/enable` (включить без метода) | 409, `TWO_FACTOR_METHOD_NOT_AVAILABLE` |
| 8.1.3 | `POST /api/v1/auth/2fa/methods/email`: `{"email":"alice@example.com"}` | 200, `challenge_id`; письмо с кодом на этот адрес |
| 8.1.4 | `GET /auth/2fa/status` | Метод ещё не подтверждён: `methods` пустой |
| 8.1.5 | `POST /api/v1/auth/2fa/methods/email/confirm`: `challenge_id` и неверный код | 401, `INVALID_TWO_FACTOR_CODE` |
| 8.1.6 | Подтвердить верным кодом | 204 |
| 8.1.7 | `GET /auth/2fa/status` | `methods` содержит один метод `type: email`, замаскированный адрес, `is_default: true`; запомните его `id` как `methodId` |
| 8.1.8 | Добавить тот же адрес повторно (`methods/email`) | 409, `TWO_FACTOR_METHOD_ALREADY_EXISTS` |

### 8.2. Включение и вход

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 8.2.1 | `POST /auth/2fa/enable` | 200, `challenge_id`; в логе письмо с кодом на адрес метода |
| 8.2.2 | `POST /auth/2fa/enable/confirm`: `challenge_id` и код | 204 |
| 8.2.3 | В логе письмо `Two-factor authentication enabled` | Уведомление есть |
| 8.2.4 | `GET /auth/2fa/status` | `enabled: true` |
| 8.2.5 | Вход alice по username: `POST /auth/login` | 200, `requires_two_factor: true`, `challenge_id`, `access_token: null` |
| 8.2.6 | `POST /auth/2fa/login/confirm`: `challenge_id` и неверный код | 401, `INVALID_TWO_FACTOR_CODE` |
| 8.2.7 | Сразу `POST /auth/2fa/login/resend`: `{"challenge_id":"..."}` | 429, `TWO_FACTOR_RESEND_TOO_EARLY` |
| 8.2.8 | Подождать 60 секунд и повторить resend | 200, новый `challenge_id`, новое письмо |
| 8.2.9 | Подтвердить старым кодом (до resend) | 404 или 401: старый challenge недействителен |
| 8.2.10 | Подтвердить новым кодом на новом `challenge_id` | 200, `access_token` и `refresh_token`; `requires_two_factor: false` |
| 8.2.11 | Повторить тот же код | 404, `TWO_FACTOR_CHALLENGE_NOT_FOUND` (код одноразовый) |
| 8.2.12 | Вход по email (`/auth/email/login`) | Тоже `requires_two_factor: true`: 2FA относится к аккаунту, а не к способу входа |

### 8.3. Recovery-коды

Токен после входа с 2FA назовём `token2fa`.

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 8.3.1 | `POST /auth/2fa/recovery-codes` токеном `token2fa` | 200, `codes`: 10 кодов вида `ABCDE-FGHJK` |
| 8.3.2 | Запомнить два кода (`R1`, `R2`) | Коды показываются один раз |
| 8.3.3 | Вход по username, получить `challenge_id`, `POST /auth/2fa/login/confirm` с `code = R1` | 200, токены |
| 8.3.4 | Повторить с тем же кодом `R1` на новом входе | 401, `INVALID_TWO_FACTOR_CODE` (код использован) |
| 8.3.5 | Вход с кодом `R2` в нижнем регистре и без дефиса | 200 (формат нормализуется) |
| 8.3.6 | Сгенерировать recovery-коды заново | Новые 10 кодов; ни один старый больше не подходит |
| 8.3.7 | Генерация recovery-кодов при выключенной 2FA (после раздела 8.5) | 409, `TWO_FACTOR_NOT_ENABLED` |

### 8.4. Удаление метода

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 8.4.1 | `DELETE /auth/2fa/methods/methodId` пока 2FA включена | 409, `TWO_FACTOR_LAST_METHOD` |
| 8.4.2 | Добавить второй метод (адрес `alice2@example.com`, подтвердить) | В `status` два метода, default остаётся первый |
| 8.4.3 | `DELETE /auth/2fa/methods/methodId` (первый, default) | 204; default переходит ко второму методу (`is_default: true` у оставшегося) |
| 8.4.4 | `DELETE /auth/2fa/methods/неизвестный-id` | 404, `TWO_FACTOR_METHOD_NOT_FOUND` |
| 8.4.5 | Вход alice | Код приходит на адрес оставшегося метода (`alice2@example.com`) |

### 8.5. Отключение

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 8.5.1 | `POST /auth/2fa/disable` | 200, `challenge_id`, код на адрес метода |
| 8.5.2 | `POST /auth/2fa/disable/confirm` с кодом | 204, в логе письмо `Two-factor authentication disabled` |
| 8.5.3 | `GET /auth/2fa/status` | `enabled: false` |
| 8.5.4 | Вход alice | Сразу токены, без challenge |
| 8.5.5 | Включить 2FA снова и проверить recovery-коды | Старые коды из 8.3.6 не работают: после отключения они удаляются |

После раздела 8 оставьте 2FA у alice **выключенной**.

---

## 9. Merge: объединение аккаунтов

**Что проверяем:** перенос способов входа и контактов в целевой аккаунт, доказательство владения, ограничения, 2FA источника, деактивацию источника, письмо.

Объединяется **источник** (удаляется как аккаунт) в **цель** (тот, кто выполняет запрос).

### 9.1. Подготовка

Создайте двух пользователей (через username и email регистрацию, как в разделах 3 и 4):

- `carol` (username) с паролем `Passw0rd!123`: **цель**.
- `dave@example.com` (email, имя `Dave`) с паролем `Passw0rd!123`: **источник**.

Войдите carol (свежий вход) и сохраните токен `tokenCarol`. Войдите dave и сохраните токен `tokenDave`.

### 9.2. Merge без 2FA

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 9.2.1 | `tokenCarol`: `POST /api/v1/users/me/merge/proofs/email`: `{"email":"dave@example.com","password":"Passw0rd!123"}` | 200, `proof_id`, `expires_at`, `requires_two_factor: false` |
| 9.2.2 | Тот же запрос с неверным паролем | 403, `MERGE_INVALID_CREDENTIALS` |
| 9.2.3 | Доказательство своего же аккаунта (username carol) | Отказ при Merge на шаге 9.2.8: 400, `MERGE_SAME_USER` |
| 9.2.4 | `POST /users/me/merge/proofs/email` с несуществующим email | 404, `MERGE_ACCOUNT_NOT_FOUND` |
| 9.2.5 | `POST /users/me/merge`: `{"proof_id":"<чужой или выдуманный id>"}` | 404, `MERGE_PROOF_NOT_FOUND` |
| 9.2.6 | `POST /users/me/merge`: `{"proof_id":"<proof_id из 9.2.1>"}` | 204 |
| 9.2.7 | `tokenCarol`: `GET /identities` | Два способа: username `carol` и email (замаскированный `d***@example.com`) |
| 9.2.8 | Повторить Merge с тем же `proof_id` | 409, `MERGE_PROOF_USED` |
| 9.2.9 | `tokenDave`: `GET /users/me` | 401: сессии источника отозваны |
| 9.2.10 | Вход по email `dave@example.com`, пароль `Passw0rd!123` | 200, но это **carol**: `GET /users/me` показывает аккаунт carol (способ входа теперь принадлежит ей) |
| 9.2.11 | Проверить статус старого аккаунта Dave в базе: `python scripts\check_db.py "select first_name, status from users"` | Строка Dave имеет `status = deactivated_by_merge`, строка carol `active` |
| 9.2.12 | Лог писем | Письмо `Accounts merged` на `dave@example.com` |

### 9.3. Ограничения

Создайте ещё двух пользователей с username: `erin1` и `erin2` (оба только username).

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 9.3.1 | `erin1` (свежий вход): `POST /users/me/merge/proofs/username`: `{"username":"erin2","password":"Passw0rd!123"}` | 200, `proof_id` |
| 9.3.2 | `POST /users/me/merge` с этим `proof_id` | 409, `MERGE_TYPE_CONFLICT`: у обоих есть username-способ |
| 9.3.3 | После отказа проверить `erin2` | Аккаунт и способ входа не изменились, вход `erin2` работает |
| 9.3.4 | Merge с использованием токена, полученного более `FRESH_SESSION_MINUTES` минут назад (см. раздел 11) | 403, `FRESH_SESSION_REQUIRED` |
| 9.3.5 | Merge без токена | 401 |

### 9.4. Merge с 2FA источника

Создайте `gina` (username, цель) и `hank@example.com` (email, источник). У `hank` включите 2FA (раздел 8: добавить метод, подтвердить, включить).

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 9.4.1 | `gina` (свежий вход): `POST /users/me/merge/proofs/email` для `hank` | 200, `requires_two_factor: true`, `challenge_id`; письмо с кодом на метод hank |
| 9.4.2 | `POST /users/me/merge` с этим `proof_id` до подтверждения | 403, `MERGE_PROOF_NOT_CONFIRMED` |
| 9.4.3 | `POST /users/me/merge/proofs/confirm`: `{"proof_id":"...","code":"неверный"}` | 401, `INVALID_TWO_FACTOR_CODE` |
| 9.4.4 | Подтвердить верным кодом | 200 |
| 9.4.5 | `POST /users/me/merge` | 204; у `gina` появился email-способ |
| 9.4.6 | `GET /auth/2fa/status` для gina | `enabled: false`: настройки 2FA источника не переносятся |

### 9.5. Контакты

Контакты пока создаются только в базе (эндпоинтов для них нет). Проверка переноса: перед Merge добавьте контакт источнику напрямую в базе, после Merge убедитесь, что он принадлежит цели. Если эта проверка не нужна сейчас, пропустите этот пункт.

---

## 10. Деактивация и purge

**Что проверяем:** деактивация пользователем и администратором, невозможность входа, удаление данных из базы (purge) только для неактивных, защита.

Создайте пользователей `ivan` и `judy` (username).

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 10.1 | `ivan`: `POST /api/v1/users/me/deactivate` | 204 |
| 10.2 | Токеном ivan: `GET /users/me` | 401 (сессии отозваны) |
| 10.3 | Вход ivan | 403, `USER_INACTIVE` |
| 10.4 | Повторная деактивация ivan администратором: `superadmin`, `POST /users/{ivan_id}/deactivate` | 409, `USER_ALREADY_DEACTIVATED` |
| 10.5 | `superadmin`: `POST /users/{judy_id}/deactivate` | 204; вход judy возвращает 403 `USER_INACTIVE` |
| 10.6 | Токеном обычного пользователя (alice): `POST /users/{judy_id}/deactivate` | 403, `INSUFFICIENT_PERMISSIONS` |
| 10.7 | `superadmin`: деактивировать самого себя | Отказ: 400 (последний superadmin) |
| 10.8 | Проверить статусы в базе: `python scripts\check_db.py "select first_name, status from users"` | `ivan` имеет `deactivated_by_user`, `judy` имеет `deactivated_by_admin` |
| 10.9 | `superadmin` (свежий вход): `DELETE /users/{alice_id}?confirm_user_id={alice_id}` (активный пользователь) | 409, `USER_STILL_ACTIVE` |
| 10.10 | `DELETE /users/{ivan_id}?confirm_user_id=другой-id` | 400, `PURGE_CONFIRMATION_MISMATCH` |
| 10.11 | `DELETE /users/{ivan_id}?confirm_user_id={ivan_id}` токеном админа (не superadmin) | 403, `INSUFFICIENT_PERMISSIONS` |
| 10.12 | `DELETE /users/{ivan_id}?confirm_user_id={ivan_id}` токеном superadmin со свежей сессией | 204 |
| 10.13 | Проверить базу: `python scripts\check_db.py "select count(*) from users where first_name='ivan'"` и по таблицам `username_identities`, `sessions`, `two_factor_challenges`, `contacts` | Строк ivan нет нигде (проверьте также, что нет ошибок внешних ключей в консоли сервиса) |
| 10.14 | `DELETE /users/{judy_id}?confirm_user_id={judy_id}` токеном superadmin со **старой** сессией (см. раздел 11) | 403, `FRESH_SESSION_REQUIRED` |

---

## 11. Свежая сессия и лимиты частоты

### 11.1. Свежая сессия

**Что проверяем:** чувствительные действия требуют недавнего входа.

Остановите сервис, в `.env` поставьте `FRESH_SESSION_MINUTES=1`, запустите заново. Войдите alice, подождите 70 секунд и выполните каждое действие тем же токеном:

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 11.1.1 | `DELETE /identities/{id}` | 403, `FRESH_SESSION_REQUIRED` |
| 11.1.2 | `POST /identities/username` | 403, `FRESH_SESSION_REQUIRED` |
| 11.1.3 | `POST /identities/email` | 403, `FRESH_SESSION_REQUIRED` |
| 11.1.4 | `POST /identities/email/confirm` | 403, `FRESH_SESSION_REQUIRED` |
| 11.1.5 | `POST /identities/google` | 403, `FRESH_SESSION_REQUIRED` |
| 11.1.6 | `POST /auth/2fa/methods/email` | 403, `FRESH_SESSION_REQUIRED` |
| 11.1.7 | `DELETE /auth/2fa/methods/{id}` | 403, `FRESH_SESSION_REQUIRED` |
| 11.1.8 | `POST /auth/2fa/disable` | 403, `FRESH_SESSION_REQUIRED` |
| 11.1.9 | `POST /users/me/merge` | 403, `FRESH_SESSION_REQUIRED` |
| 11.1.10 | `GET /users/me`, `GET /identities`, `GET /auth/2fa/status` | 200: чтение не требует свежей сессии |
| 11.1.11 | Новый вход и сразу действие из 11.1.2 | Запрос проходит (не 403) |
| 11.1.12 | Обновить токены (`/auth/refresh`) и повторить старое действие | По-прежнему 403: refresh не делает сессию свежей |

После проверки верните `FRESH_SESSION_MINUTES=15` и перезапустите сервис.

### 11.2. Лимиты частоты

**Что проверяем:** превышение лимита возвращает 429. Счётчики хранятся в памяти процесса; перезапуск сервиса их обнуляет.

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 11.2.1 | Регистрация по username четыре раза подряд с одним и тем же именем `limit1` | Первые попытки 201 и 409, на четвёртой 429, `RATE_LIMIT_EXCEEDED` (3 в час на имя) |
| 11.2.2 | `POST /auth/login` с неверным паролем 11 раз подряд для одного username | Примерно с 11-й попытки 429 (10 за 15 минут на имя) |
| 11.2.3 | `POST /auth/email/register` четыре раза с одним адресом | Четвёртая попытка 429 (3 в час на адрес) |
| 11.2.4 | `POST /identities/email` четыре раза с одним адресом свежей сессией | Четвёртая попытка 429 (3 в час на адрес) |
| 11.2.5 | Запросы любого лимитируемого эндпоинта после 429 через время окна | Снова обычные ответы (проверять не обязательно, окно до часа) |

Для сброса лимитов между проверками перезапускайте сервис.

---

## 12. Очистка временных записей

**Что проверяем:** фоновая задача удаляет использованные и просроченные временные записи без запросов.

1. Остановите сервис, в `.env` поставьте `CLEANUP_INTERVAL_SECONDS=15`, запустите заново.
2. Выполните вход пользователя с 2FA (раздел 8.2.5 и 8.2.10): после успешного входа challenge помечается как использованный.
3. Сразу проверьте:
   ```powershell
   python scripts\check_db.py "select id, purpose, used from two_factor_challenges"
   ```
   Использованный challenge ещё виден.
4. Подождите около 20 секунд и повторите команду.

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 12.1 | Сервис работает 20 секунд после использования challenge | Строки с `used = 1` из `two_factor_challenges` исчезли |
| 12.2 | Просроченная регистрация: начать `email/register`, не подтверждать, подождать больше 10 минут (`CHALLENGE_EXPIRE_MINUTES=10`) и следить за `select * from email_registrations` | После очередного прогона просроченная строка исчезает |
| 12.3 | Остановка сервиса (Ctrl+C) | Остановка без ошибок и предупреждений о незавершённой задаче |
| 12.4 | Вернуть `CLEANUP_INTERVAL_SECONDS=3600` | Перезапустить сервис |

Если в консоли после остановки или во время работы появляется `Periodic cleanup failed` с трассировкой, это ошибка: пришлите её.

---

## 13. Если что-то не работает

Для каждого проваленного шага соберите и пришлите:

1. Номер шага из этого документа.
2. Адрес и метод запроса и его тело (пароли можно не присылать).
3. Статус и тело ответа (особенно поле `code`).
4. Трассировку из консоли сервиса, если она есть (весь блок от `Traceback` до последней строки).
5. Для шагов с письмами: последние строки лога писем.

Типичные причины, которые стоит проверить первыми:

| Симптом | Что проверить |
|---|---|
| Сервис не стартует, `ValidationError` по настройкам | В `.env` нет обязательной переменной (`JWT_SECRET_KEY`, `SUPERADMIN_*`, `GOOGLE_*`) |
| Ошибка про отсутствующую колонку или таблицу | Остался старый `app.db`: удалите его (в проекте пока нет миграций) |
| Ошибка внешнего ключа при удалении | Пришлите трассировку, это ошибка очерёдности удаления |
| 401 сразу после входа | Токен истёк (15 минут) или вставлен вместе со словом `Bearer` |
| 429 там, где его не ждали | Сработал лимит частоты: перезапустите сервис |
| 403 `FRESH_SESSION_REQUIRED` | Вход старше `FRESH_SESSION_MINUTES`: войдите заново |
| Нет письма в логе | Проверьте `EMAIL_SERVICE=dummy` и папку `logs\email_dummy_logs` |

---

## 14. Итоговая таблица проверки

Отмечайте результат разделов: ✅ всё прошло, ⚠️ есть отклонения, ❌ не работает.

| Раздел | Что проверено | Результат |
|---|---|---|
| 2 | Запуск, база, суперадмин | |
| 3 | Регистрация и вход по username | |
| 4 | Регистрация и вход по email | |
| 5 | Токены, профиль, сессии | |
| 6 | Link | |
| 7 | Unlink | |
| 8 | 2FA и recovery-коды | |
| 9 | Merge | |
| 10 | Деактивация и purge | |
| 11 | Свежая сессия и лимиты | |
| 12 | Очистка временных записей | |
