# Ручная проверка сервиса авторизации

Пошаговое руководство по первому запуску и ручной проверке реализованных операций: регистрация и вход, токены и сессии, способы входа (Link, Unlink, Merge), двухфакторная аутентификация, деактивация и purge, защита от злоупотреблений, фоновая очистка.

Документ составлен по коду ветки `dev` (коммит `6b20c24`): маршруты, схемы запросов и коды ошибок сверены с исходниками. Само приложение при составлении не запускалось, поэтому ожидаемые результаты взяты из кода, а не из реального прогона. Если результат шага отличается, отметьте шаг как проваленный и действуйте по разделу 13.

## Как пользоваться

- Разделы выполняйте по порядку: следующие используют пользователей из предыдущих.
- В таблицах: **Шаг**, **Действие**, **Ожидаемый результат**. Ответы на ошибки имеют вид `{"code": "...", "message": "..."}`; в таблицах указан `code`.
- Все адреса API начинаются с `/api/v1`. Исключение: `/health` и `/health/ready` без префикса.
- Команды рассчитаны на **Windows PowerShell**. Если у вас обычная командная строка (cmd), введите `powershell` и нажмите Enter, приглашение сменится на `PS C:\...>`.
- Почти все запросы выполняются в Swagger (`http://127.0.0.1:8000/docs`). Группы в Swagger свёрнуты, раскрывайте их по названию (список групп в разделе 2).

## Содержание

1. Подготовка
2. Запуск, список маршрутов, состояние сервиса
3. Регистрация и вход по username
4. Регистрация и вход по email
5. Токены, профиль, сессии
6. Link: добавление способов входа
7. Unlink: удаление способов входа
8. Двухфакторная аутентификация
9. Merge: объединение аккаунтов
10. Роли, деактивация, purge
11. Свежая сессия и лимиты частоты
12. Фоновая очистка
13. Если что-то не работает
14. Итоговая таблица

---

## 1. Подготовка

**Что проверяем:** окружение собирается и сервис стартует на чистой базе. Это первый настоящий запуск.

### 1.1. Установка

В корне проекта (там, где `README.md` и `requirements.txt`), каждую команду отдельно:

```powershell
python -m venv .venv
```
```powershell
.venv\Scripts\Activate.ps1
```
```powershell
python -m pip install -r requirements.txt
```

Если PowerShell запрещает запуск скриптов: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, затем повторить активацию. Все дальнейшие команды выполняются **в корне проекта** с активированным окружением (в начале строки `(.venv)`).

### 1.2. Файл `.env`

Файл `.env` создаётся в корне проекта. В репозитории лежит образец `.env-example`: можно скопировать его, но **значения `secret` и `GOOGLE_REDIRECT_URI` с `${...}` не годятся** (подстановки `${APP_HOST}` не раскрываются). Минимальный рабочий `.env`:

```
JWT_SECRET_KEY=СЮДА_СЕКРЕТ
SUPERADMIN_LOGIN=superadmin
SUPERADMIN_PASSWORD=Sup3rAdmin!123
SUPERADMIN_EMAIL=superadmin@example.com
GOOGLE_CLIENT_ID=dummy
GOOGLE_CLIENT_SECRET=dummy
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/api/v1/google/auth/callback
EMAIL_SERVICE=dummy
```

Секрет для `JWT_SECRET_KEY`:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Обязательные ключи без значения по умолчанию: `JWT_SECRET_KEY`, `SUPERADMIN_LOGIN`, `SUPERADMIN_PASSWORD`, `SUPERADMIN_EMAIL`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`. Остальное имеет значения по умолчанию, в том числе: `FRESH_SESSION_MINUTES=15`, `ACCESS_TOKEN_EXPIRE_MINUTES=15`, `CLEANUP_INTERVAL_SECONDS=3600`, `MERGE_PROOF_EXPIRE_MINUTES=10`, `CLIENT_BASE_URL=http://localhost:3000`, `DATABASE_URL=sqlite+aiosqlite:///./app.db`.

Ключ `SECRETS_ENCRYPTION_KEY` для этой проверки не нужен.

### 1.3. Чистая база

База `app.db` создаётся в корне проекта при запуске. Перед первой проверкой:

```powershell
Remove-Item app.db -ErrorAction SilentlyContinue
```

Полный сброс в любой момент: остановить сервис (Ctrl+C), удалить `app.db`, запустить заново.

### 1.4. Запуск

```powershell
python -m app.main
```

Сервис слушает `http://127.0.0.1:8000`. Остановка: Ctrl+C. **Перезапуск сервиса сбрасывает счётчики лимитов частоты** (они в памяти), данные в базе остаются.

### 1.5. Письма с кодами

При `EMAIL_SERVICE=dummy` письма не отправляются, а дописываются в файл `logs\email_dummy_logs\emails_ГГГГ-ММ-ДД.log`. Показать конец файла за сегодня:

```powershell
Get-Content (Get-ChildItem logs\email_dummy_logs | Sort-Object LastWriteTime | Select-Object -Last 1).FullName -Tail 25
```

Формат записи:

```
Sent at: 2026-10-28 14:05
To: bob@example.com
Subject: Confirm your email registration
Body:
Your verification code is: 123456
```

Код всегда 6 цифр, действует 10 минут. Все коды ниже берутся отсюда.

### 1.6. Токены в Swagger

1. Выполните вход (`POST /api/v1/auth/login`) через **Try it out**: заполните только `username` и `password` (остальные поля формы пустые).
2. Скопируйте `access_token` из ответа.
3. Нажмите **Authorize** вверху страницы. В блоке **Authentication** (тип http, Bearer) вставьте токен без слова `Bearer`, нажмите **Authorize**, затем **Close**.
4. Теперь запросы идут от этого пользователя. Чтобы сменить пользователя: **Authorize**, **Logout** в блоке, вставить другой токен.

Access-токен живёт 15 минут. После истечения: `401 INVALID_TOKEN`, нужно войти заново.

Для нескольких пользователей одновременно удобно держать токены в текстовом файле заметок: `alice-U: ...`, `alice-E: ...`.

### 1.7. Лимиты частоты и порядок проверки

Лимиты считаются по IP, а проверка идёт с одного адреса, поэтому **перед каждым разделом перезапускайте сервис**, чтобы счётчики были нулевыми. Самые «тесные»:

| Лимит | Значение | Какие запросы считает |
|---|---|---|
| REGISTER_IP | 10 за час | регистрация по username, регистрация по email |
| LOGIN_IP | 20 за 10 минут | оба входа, вход Google, все три `merge/proofs/...` кроме `confirm` |
| SEND_CODE_IP | 10 за 10 минут | повторная отправка кода регистрации, 2FA: добавить метод, `enable`, `disable`, `recovery-codes`, `login/resend` |
| CONFIRM_IP | 20 за 10 минут | все подтверждения кода |
| LINK_IP / UNLINK_IP | 20 за час | Link и Unlink |

Подробно лимиты проверяются в разделе 11.

### 1.8. Просмотр базы (дополнительно)

Для разделов 10 и 12 пригодится просмотр таблиц. Создайте временный файл `scripts\check_db.py`:

```python
import sqlite3
import sys

connection = sqlite3.connect("app.db")
for row in connection.execute(sys.argv[1]).fetchall():
    print(row)
```

Пример запуска:

```powershell
python scripts\check_db.py "select id, first_name, role, status from users"
```

Таблицы: `users`, `username_identities`, `email_identities`, `google_identities`, `sessions`, `two_factor_challenges`, `two_factor_methods`, `two_factor_recovery_codes`, `user_security_settings`, `email_registrations`, `email_link_requests`, `merge_proofs`, `contacts`. После проверки файл `scripts\check_db.py` удалите.

### 1.9. Тестовые данные

Пароль всех тестовых пользователей: `Passw0rd!123`. Пользователи создаются в тех разделах, где нужны:

| Пользователь | Способ входа | Где создаётся |
|---|---|---|
| `superadmin` (`superadmin@example.com`) | username и email, пароль из `.env` | автоматически при первом запуске |
| `alice` | username | раздел 3 |
| `bob@example.com` | email | раздел 4 |
| `carol`, `frank@example.com` | username; email | раздел 6 |
| `dave@example.com`, `erin1`, `erin2`, `gina`, `hank@example.com` | см. раздел 9 | раздел 9 |
| `ivan`, `judy`, `kate` | username | раздел 10 |

Пароль суперадмина (`Sup3rAdmin!123`) не совпадает с паролем тестовых пользователей.

---

## 2. Запуск, список маршрутов, состояние сервиса

**Что проверяем:** приложение стартует, база и суперадмин создаются, все ожидаемые маршруты зарегистрированы, служебные эндпоинты отвечают.

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 2.1 | Запустить `python -m app.main` на чистой базе | В консоли `App starting...` и сообщения uvicorn о запуске, без трассировок. Появились `app.db` и папка `logs\email_dummy_logs` |
| 2.2 | Открыть `http://127.0.0.1:8000/docs` | Открывается Swagger. Группы: Auth, Username Authentication, Email Authentication, Google Authentication, Two-Factor Authentication, Identities, Merge, Sessions, Users, Development, Health |
| 2.3 | Открыть `http://127.0.0.1:8000/health` | `{"status":"ok"}` |
| 2.4 | Открыть `http://127.0.0.1:8000/health/ready` | `{"status":"ok"}` (при недоступной базе было бы 503) |
| 2.5 | Вывести все маршруты (команда ниже) | Список совпадает с таблицей маршрутов ниже |
| 2.6 | Войти суперадмином: `POST /api/v1/auth/login` (группа Username Authentication), `username=superadmin`, `password=Sup3rAdmin!123` | 200. В ответе `access_token`, `refresh_token`, `token_type: bearer`, `requires_two_factor: false`, `challenge_id: null` |
| 2.7 | Авторизоваться токеном (п. 1.6), `GET /api/v1/users/me` | 200: `id`, `first_name: Superadministrator`, `last_name: System`, `role: superadmin` |
| 2.8 | Остановить сервис (Ctrl+C) и запустить снова | Запуск без ошибок. Второй суперадмин не создаётся: `python scripts\check_db.py "select count(*) from users"` даёт `(1,)` |
| 2.9 | Войти суперадмином по email: `POST /api/v1/auth/email/login`, в поле `username` указать `superadmin@example.com` | 200 и токены |
| 2.10 | `GET /api/v1/identities` с токеном суперадмина | Два способа: `username` (`display_identifier: superadmin`) и `email` (`s***@example.com`) |

Вывод всех маршрутов (сервис должен работать, команда выполняется во втором окне PowerShell):

```powershell
(Invoke-RestMethod http://127.0.0.1:8000/openapi.json).paths.PSObject.Properties | ForEach-Object { $path = $_.Name; $_.Value.PSObject.Properties.Name | ForEach-Object { "$($_.ToUpper()) $path" } }
```

Ожидаемые маршруты (всего 46 без `/docs`, `/openapi.json`, `/favicon.ico`):

| Группа | Маршруты |
|---|---|
| Health | `GET /health`, `GET /health/ready` |
| Username Authentication | `POST /api/v1/auth/register`, `POST /api/v1/auth/login` |
| Auth | `POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout` |
| Email Authentication | `POST /api/v1/auth/email/register`, `/auth/email/register/resend`, `/auth/email/register/confirm`, `/auth/email/login` |
| Google Authentication | `POST /api/v1/google/auth/login`, `GET /api/v1/google/auth/callback` |
| Two-Factor Authentication | `GET /api/v1/auth/2fa/status`, `POST /auth/2fa/methods/email`, `POST /auth/2fa/methods/email/confirm`, `DELETE /auth/2fa/methods/{method_id}`, `POST /auth/2fa/recovery-codes`, `POST /auth/2fa/login/confirm`, `POST /auth/2fa/login/resend`, `POST /auth/2fa/enable`, `/enable/confirm`, `/disable`, `/disable/confirm` |
| Identities | `GET /api/v1/identities`, `DELETE /identities/{identity_id}`, `POST /identities/username`, `/identities/email`, `/identities/email/confirm`, `/identities/google` |
| Merge | `POST /api/v1/users/me/merge/proofs/username`, `/proofs/email`, `/proofs/google`, `/proofs/confirm`, `POST /users/me/merge` |
| Sessions | `GET /api/v1/sessions`, `POST /sessions/revoke_all_session`, `POST /sessions/{session_id}/revoke` |
| Users | `GET /api/v1/users`, `GET /users/me`, `GET /users/{user_id}`, `PATCH /users/me`, `PATCH /users/{user_id}/role`, `POST /users/me/deactivate`, `POST /users/{user_id}/deactivate`, `DELETE /users/{user_id}` |
| Development | `POST /api/v1/dev/email/send` |

Если в списке нет `POST /api/v1/auth/login`, пришлите мне вывод команды целиком: это значит, что запущена не та версия кода.

---

## 3. Регистрация и вход по username

**Что проверяем:** создание пользователя с username, нормализация имени, вход, ошибки входа. Перед разделом перезапустите сервис (сброс лимитов).

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 3.1 | `POST /api/v1/auth/register`: `{"username":"alice","password":"Passw0rd!123","first_name":"Alice","last_name":"Test"}` | 201: `id`, `username: alice`, `first_name`, `last_name`, `role: user`. Запишите `id` как `aliceId` |
| 3.2 | Повторить тот же запрос | 409, `USER_ALREADY_EXISTS` |
| 3.3 | Повторить с `"username":"  ALICE  "` | 409, `USER_ALREADY_EXISTS`: имя нормализуется (обрезаются пробелы, регистр не важен) |
| 3.4 | `POST /api/v1/auth/login`: `alice` / `Passw0rd!123` | 200, `access_token`, `refresh_token`, `requires_two_factor: false` |
| 3.5 | Вход с `ALICE` | 200 |
| 3.6 | Вход с неверным паролем | 401, `INVALID_CREDENTIALS` |
| 3.7 | Вход с несуществующим username | 401, `INVALID_CREDENTIALS` (тот же код, что в 3.6) |
| 3.8 | `GET /api/v1/users/me` с токеном alice | 200: `id` = `aliceId`, `first_name: Alice`, `last_name: Test`, `role: user` |
| 3.9 | `GET /api/v1/users/me` без токена (нажать **Authorize**, **Logout**) | 401, `INVALID_TOKEN` |
| 3.10 | `GET /api/v1/users/me` с мусорным токеном `abc` | 401, `INVALID_TOKEN` |
| 3.11 | `GET /api/v1/identities` с токеном alice | 200, один элемент: `type: username`, `display_identifier: alice`, есть `id` и `created_at` |

---

## 4. Регистрация и вход по email

**Что проверяем:** регистрация по email с подтверждением кодом, повторная отправка, лимит попыток. Перезапустите сервис перед разделом.

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 4.1 | `POST /api/v1/auth/email/register`: `{"email":"bob@example.com","password":"Passw0rd!123","first_name":"Bob","last_name":"Test"}` | 202: `registration_id`, `expires_at`, `message` |
| 4.2 | Письмо в логе (п. 1.5) | `To: bob@example.com`, `Subject: Confirm your email registration`, код из 6 цифр и ссылка `http://localhost:3000/register/confirm?registration_id=...` с тем же `registration_id` |
| 4.3 | `POST /api/v1/auth/email/login`, `username=bob@example.com`, пароль `Passw0rd!123` | 401, `INVALID_EMAIL_CREDENTIALS`: пока код не введён, пользователя нет |
| 4.4 | `POST /api/v1/auth/email/register/confirm`: `registration_id` и неверный код `000000` | 401, `INVALID_EMAIL_VERIFICATION_CODE` |
| 4.5 | Сразу `POST /api/v1/auth/email/register/resend`: `{"registration_id":"..."}` | 429, `EMAIL_VERIFICATION_RESEND_TOO_EARLY` (пауза 60 секунд с момента отправки) |
| 4.6 | Подождать 60 секунд, повторить resend | 202, в логе новое письмо с новым кодом. Старый код больше не подходит |
| 4.7 | `register/confirm` с кодом из нового письма | 201: `id`, `email: bob@example.com`, `role: user`. Запишите `id` как `bobId` |
| 4.8 | Повторить confirm тем же кодом | 404, `EMAIL_REGISTRATION_NOT_FOUND` |
| 4.9 | `POST /auth/email/login`, `username=bob@example.com`, `Passw0rd!123` | 200, токены |
| 4.10 | Вход с `username=  BOB@Example.com ` | 200: адрес нормализуется |
| 4.11 | Вход с неверным паролем | 401, `INVALID_EMAIL_CREDENTIALS` |
| 4.12 | `POST /auth/email/register` с уже занятым `bob@example.com` | 409, `USER_ALREADY_EXISTS` сразу на регистрации |
| 4.13 | `POST /auth/email/register/resend` с выдуманным `registration_id` | 404, `EMAIL_REGISTRATION_NOT_FOUND` |
| 4.14 | `GET /api/v1/identities` с токеном bob | 200, один элемент: `type: email`, `display_identifier: b***@example.com` |

### Лимит попыток кода

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 4.15 | `email/register` для `eve@example.com` | 202, `registration_id` |
| 4.16 | Четыре раза `register/confirm` с неверным кодом | Каждый раз 401, `INVALID_EMAIL_VERIFICATION_CODE` |
| 4.17 | Пятый неверный код | 429, `EMAIL_VERIFICATION_TOO_MANY_ATTEMPTS` |
| 4.18 | Верный код из письма | 429, `EMAIL_VERIFICATION_TOO_MANY_ATTEMPTS`: после лимита попыток код не принимается |
| 4.19 | Подождать 60 секунд, `register/resend` | 202, счётчик попыток сброшен; верный новый код подтверждает регистрацию (201) |

---

## 5. Токены, профиль, сессии

**Что проверяем:** обновление токенов, выход, список сессий, отзыв сессий, изменение профиля. Перезапустите сервис перед разделом.

Подготовка: войдите alice (`POST /auth/login`), авторизуйтесь токеном, вызовите `POST /api/v1/sessions/revoke_all_session` (204): остальные сессии alice закрыты, текущая тоже. Войдите alice заново: это сессия **A1** (access `a1`, refresh `r1`).

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 5.1 | `GET /api/v1/sessions` токеном `a1` | 200, один элемент: `id`, `ip_address`, `user_agent`, `created_at`, `last_used_at`, `expires_at`. Запишите `id` как `idA1` |
| 5.2 | Ещё раз войти alice: сессия **A2** (`a2`, `r2`). `GET /sessions` токеном `a1` | Два элемента. Новый `id` запишите как `idA2` |
| 5.3 | `POST /api/v1/auth/refresh`: `{"refresh_token":"<r1>"}` | 200: новые `access_token` и `refresh_token`. Это новые `a1b`, `r1b` |
| 5.4 | Повторить refresh со старым `r1` | 401, `INVALID_REFRESH_TOKEN` (refresh-токен одноразовый, при обновлении заменяется) |
| 5.5 | `GET /users/me` токеном `a1b` | 200 |
| 5.6 | `GET /users/me` старым токеном `a1` | 200: старый access-токен живёт до истечения (сессия та же) |
| 5.7 | `POST /auth/refresh` с произвольной строкой | 401, `INVALID_REFRESH_TOKEN` |
| 5.8 | `PATCH /api/v1/users/me`: `{"first_name":"Alicia"}` | 200, `first_name: Alicia`, `last_name: Test` |
| 5.9 | `GET /users/me` | `first_name: Alicia` |
| 5.10 | `POST /api/v1/sessions/{idA2}/revoke` токеном `a1b` | 204 |
| 5.11 | Любой защищённый запрос токеном `a2` | 401, `SESSION_REVOKED` |
| 5.12 | Повторно `POST /sessions/{idA2}/revoke` | 204 (повторный отзыв ничего не делает) |
| 5.13 | `POST /sessions/неизвестный-id/revoke` | 404, `SESSION_NOT_FOUND` |
| 5.14 | Войти bob, `GET /sessions` его токеном, взять `id` его сессии. `POST /sessions/{bobSessionId}/revoke` токеном alice | 403, `SESSION_ACCESS_DENIED` |
| 5.15 | `POST /auth/refresh` с refresh-токеном отозванной сессии A2 (`r2`) | 401, `SESSION_REVOKED` |
| 5.16 | Войти alice ещё раз (сессия A3), `POST /auth/logout` её токеном | 204 |
| 5.17 | Запрос токеном `a1b` или токеном A3 | 401, `SESSION_REVOKED`. **Важно:** `logout` в текущей реализации закрывает **все** сессии пользователя, а не только текущую. Если это не задумано, сообщите: это отдельная доработка |
| 5.18 | Войти alice (A4), войти ещё раз (A5), `POST /sessions/revoke_all_session` токеном A4 | 204. Токены A4 и A5 перестают работать (401 `SESSION_REVOKED`) |

После раздела 5 войдите alice заново.

---

## 6. Link: добавление способов входа

**Что проверяем:** пользователь добавляет к аккаунту другой способ входа; не больше одного способа каждого типа; конфликты; требование свежей сессии. Перезапустите сервис перед разделом.

Все запросы Link требуют **свежую сессию**: вход должен быть не старше `FRESH_SESSION_MINUTES` (15 минут). Если получаете `403 FRESH_SESSION_REQUIRED`, войдите заново и вставьте новый токен.

Подготовка: у alice сейчас только username. Войдите alice (свежий токен `aliceU`).

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 6.1 | `aliceU`: `POST /api/v1/identities/email`: `{"email":"alice@example.com","password":"Passw0rd!123"}` | 202: `challenge_id`, `expires_at` |
| 6.2 | Лог писем | `To: alice@example.com`, `Subject: Confirm your email address`, 6-значный код |
| 6.3 | `GET /identities` до подтверждения | Всё ещё один способ (username) |
| 6.4 | `POST /identities/email/confirm`: `challenge_id` и неверный код | 401, `INVALID_EMAIL_VERIFICATION_CODE` |
| 6.5 | Confirm с верным кодом | 201: `type: email`, `display_identifier: a***@example.com`, `id`. Запишите как `idE` |
| 6.6 | `GET /identities` | Два способа: username и email |
| 6.7 | Войти по email: `POST /auth/email/login`, `alice@example.com` / `Passw0rd!123` | 200, токен `aliceE`. `GET /users/me` им показывает того же пользователя (тот же `id`, `first_name: Alicia`) |
| 6.8 | `aliceU`: повторить `POST /identities/email` (email у alice уже есть) | 409, `IDENTITY_TYPE_CONFLICT` |
| 6.9 | `aliceU`: `POST /identities/username` (username уже есть) с любым именем | 409, `IDENTITY_TYPE_CONFLICT` |
| 6.10 | `aliceU`: `confirm` с чужим или выдуманным `challenge_id` | 404, `EMAIL_LINK_REQUEST_NOT_FOUND` |

### Link username к email-пользователю

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 6.11 | Войти bob по email (свежий токен). `POST /identities/username`: `{"username":"bob","password":"Passw0rd!123"}` | 201: `type: username`, `display_identifier: bob` |
| 6.12 | Вход `POST /auth/login`, `bob` / `Passw0rd!123` | 200, это тот же пользователь (`id` = `bobId`) |
| 6.13 | Повторить 6.11 | 409, `IDENTITY_TYPE_CONFLICT` |
| 6.14 | Создать `frank@example.com` (регистрация по email, как в разделе 4), войти. `POST /identities/username`: `{"username":"alice","password":"Passw0rd!123"}` | 409, `IDENTITY_CONFLICT` (имя `alice` уже занято) |
| 6.15 | Создать `carol` (регистрация username, раздел 3), войти. `POST /identities/email`: `{"email":"alice@example.com","password":"Passw0rd!123"}` | 409, `IDENTITY_CONFLICT` (адрес занят) |
| 6.16 | Link без токена | 401, `INVALID_TOKEN` |

### Google (необязательно)

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 6.17 | Свежим токеном пользователя без Google: `POST /api/v1/identities/google` | 200: `authorization_url` со ссылкой на `accounts.google.com` |
| 6.18 | `POST /api/v1/google/auth/login` (без токена) | 200: `authorization_url` |

Полный вход и привязка через Google возможны только с настоящими `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` и `GOOGLE_REDIRECT_URI`. С заглушками `dummy` проверяется только получение ссылки.

---

## 7. Unlink: удаление способов входа

**Что проверяем:** безопасное удаление способа входа: нельзя удалить последний и тот, через который выполнен вход; чужие и неизвестные отклоняются; сессии удалённого способа закрываются. Перезапустите сервис перед разделом.

Подготовка: у alice два способа (username и email, после раздела 6). Выполните **два свежих входа**: по username (токен `tokenU`) и по email (токен `tokenE`). Из `GET /identities` запишите `idU` (username) и `idE` (email). Также возьмите любой `id` способа входа bob из `GET /identities` его токеном: `bobIdentityId`.

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 7.1 | `tokenU`: `DELETE /api/v1/identities/{idU}` (способ, через который вошли) | 409, `CURRENT_IDENTITY` |
| 7.2 | `tokenU`: `DELETE /identities/неизвестный-id` | 404, `IDENTITY_NOT_FOUND` |
| 7.3 | `tokenU`: `DELETE /identities/{bobIdentityId}` | 403, `IDENTITY_NOT_OWNED` |
| 7.4 | `tokenU`: `DELETE /identities/{idE}` | 204 |
| 7.5 | `tokenU`: `GET /identities` | Один способ: username |
| 7.6 | `tokenE`: `GET /users/me` (сессия удалённого способа) | 401, `SESSION_REVOKED` |
| 7.7 | `tokenU`: `GET /users/me` | 200: сессии других способов остаются |
| 7.8 | `POST /auth/email/login`, `alice@example.com` | 401, `INVALID_EMAIL_CREDENTIALS`: способа входа больше нет |
| 7.9 | `tokenU`: `DELETE /identities/{idU}` (единственный способ) | 409, `LAST_IDENTITY` (проверка «последний» срабатывает раньше проверки «текущий») |
| 7.10 | Вернуть email alice: Link email заново (шаги 6.1–6.5) | Два способа входа снова есть |

---

## 8. Двухфакторная аутентификация

**Что проверяем:** метод 2FA (адрес для кодов), включение и отключение, вход с кодом, повторная отправка, recovery-коды, удаление метода. Перезапустите сервис перед разделом.

Подготовка: alice с двумя способами (username, email), свежий вход по username: `tokenA`. Двухфакторность привязана к аккаунту, а не к способу входа.

Для ускорения паузы повторной отправки можно перед запуском сервиса задать (только для этой сессии PowerShell):

```powershell
$env:RESEND_COOLDOWN_SECONDS="5"
```

Тогда в шагах ниже вместо 60 секунд ждите 5. Параметры 2FA читаются только из переменных окружения, не из `.env`. Если не задавать, используется 60 секунд.

### 8.1. Методы

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 8.1.1 | `tokenA`: `GET /api/v1/auth/2fa/status` | 200: `enabled: false`, `methods: []` |
| 8.1.2 | `POST /auth/2fa/enable` без метода | 409, `TWO_FACTOR_METHOD_NOT_AVAILABLE` |
| 8.1.3 | `POST /auth/2fa/methods/email`: `{"email":"alice@example.com"}` | 200: `challenge_id`. В логе письмо `Subject: Confirm the new two-factor method` на этот адрес |
| 8.1.4 | `GET /auth/2fa/status` | Неподтверждённый метод не показывается: `methods: []` |
| 8.1.5 | `POST /auth/2fa/methods/email/confirm`: `challenge_id` и неверный код | 401, `INVALID_TWO_FACTOR_CODE` |
| 8.1.6 | Confirm с верным кодом | 204 |
| 8.1.7 | `GET /auth/2fa/status` | `methods`: один элемент `type: email`, `destination: a***@example.com`, `is_default: true`. Запишите его `id` как `methodId`. `enabled` ещё `false` |
| 8.1.8 | Добавить тот же адрес повторно (`methods/email` и подтверждение, либо сразу ответ) | 409, `TWO_FACTOR_METHOD_ALREADY_EXISTS` сразу на запросе |

### 8.2. Включение и вход

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 8.2.1 | `POST /auth/2fa/enable` | 200: `challenge_id`. В логе письмо `Subject: Enable two-factor authentication` на адрес метода |
| 8.2.2 | `POST /auth/2fa/enable/confirm`: `challenge_id` и код | 204. В логе письмо `Subject: Two-factor authentication enabled` |
| 8.2.3 | `GET /auth/2fa/status` | `enabled: true` |
| 8.2.4 | Повторить `POST /auth/2fa/enable` | 409, `TWO_FACTOR_ALREADY_ENABLED` |
| 8.2.5 | Войти alice: `POST /auth/login` | 200: `requires_two_factor: true`, `challenge_id`, `access_token: null`, `refresh_token: null`. В логе письмо `Subject: Confirm your login` |
| 8.2.6 | `POST /auth/2fa/login/confirm`: `challenge_id` и неверный код | 401, `INVALID_TWO_FACTOR_CODE` |
| 8.2.7 | Сразу `POST /auth/2fa/login/resend`: `{"challenge_id":"..."}` | 429, `TWO_FACTOR_RESEND_TOO_EARLY` |
| 8.2.8 | Подождать (60 или 5 секунд), повторить resend | 200: **новый** `challenge_id`, новое письмо |
| 8.2.9 | Подтвердить старый `challenge_id` (до resend) | 404, `TWO_FACTOR_CHALLENGE_NOT_FOUND`: старый challenge закрыт |
| 8.2.10 | Подтвердить новым кодом на новом `challenge_id` | 200: `access_token`, `refresh_token`, `requires_two_factor: false`. Токен запишите как `token2fa` |
| 8.2.11 | Повторить тот же confirm | 404, `TWO_FACTOR_CHALLENGE_NOT_FOUND` (код одноразовый) |
| 8.2.12 | Вход по email: `POST /auth/email/login` | Тоже `requires_two_factor: true` |
| 8.2.13 | Пять неверных кодов подряд на одном challenge | Четыре раза 401 `INVALID_TWO_FACTOR_CODE`, пятый 429 `TWO_FACTOR_TOO_MANY_ATTEMPTS`. Верный код после этого не принимается |
| 8.2.14 | Два входа подряд, затем confirm кодом первого входа | 404: новый вход закрывает предыдущий challenge того же назначения |

### 8.3. Recovery-коды

Токен после входа с 2FA: `token2fa` (получите свежий через 8.2.5 и 8.2.10, если нужно).

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 8.3.1 | `POST /auth/2fa/recovery-codes` токеном `token2fa` | 200: `codes`, 10 кодов вида `ABCDE-FGHJK`. Запишите несколько (`R1`, `R2`): показываются один раз |
| 8.3.2 | Войти alice, `POST /auth/2fa/login/confirm` с `code = R1` | 200, токены (recovery-код принимается вместо кода из письма) |
| 8.3.3 | Новый вход, confirm с тем же `R1` | 401, `INVALID_TWO_FACTOR_CODE` (код одноразовый) |
| 8.3.4 | Новый вход, confirm с `R2` в нижнем регистре и без дефиса | 200 (формат нормализуется) |
| 8.3.5 | `POST /auth/2fa/recovery-codes` ещё раз | Новые 10 кодов. Ни один из прежних больше не подходит |

### 8.4. Удаление метода

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 8.4.1 | `DELETE /auth/2fa/methods/{methodId}` при включённой 2FA и единственном методе | 409, `TWO_FACTOR_LAST_METHOD` |
| 8.4.2 | Добавить второй метод (адрес `alice2@example.com`, подтвердить кодом из лога) | `status` показывает два метода; `is_default: true` у первого |
| 8.4.3 | `DELETE /auth/2fa/methods/{methodId}` (первый, он же default) | 204. `status`: остался один метод, он стал `is_default: true` |
| 8.4.4 | `DELETE /auth/2fa/methods/неизвестный-id` | 404, `TWO_FACTOR_METHOD_NOT_FOUND` |
| 8.4.5 | Войти alice | Код входа приходит на `alice2@example.com` |

### 8.5. Отключение

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 8.5.1 | Войти, подтвердить код, взять свежий токен. `POST /auth/2fa/disable` | 200: `challenge_id`. Письмо `Subject: Disable two-factor authentication` на адрес метода |
| 8.5.2 | `POST /auth/2fa/disable/confirm` с кодом | 204. В логе письмо `Subject: Two-factor authentication disabled` |
| 8.5.3 | `GET /auth/2fa/status` | `enabled: false` |
| 8.5.4 | Повторить `POST /auth/2fa/disable` | 409, `TWO_FACTOR_ALREADY_DISABLED` |
| 8.5.5 | `POST /auth/2fa/recovery-codes` | 409, `TWO_FACTOR_NOT_ENABLED` |
| 8.5.6 | Войти alice | Сразу токены, без challenge |
| 8.5.7 | `python scripts\check_db.py "select count(*) from two_factor_recovery_codes"` | `(0,)`: при отключении recovery-коды удаляются |

После раздела 8 у alice 2FA **выключена**, метод `alice2@example.com` остаётся.

---

## 9. Merge: объединение аккаунтов

**Что проверяем:** перенос способов входа в целевой аккаунт после доказательства владения исходным; ограничения; 2FA исходного аккаунта; деактивация исходного; письмо. Перезапустите сервис перед разделом.

**Цель** (target): аккаунт, который выполняет запрос и остаётся. **Источник** (source): аккаунт, который вливается и деактивируется. Токен цели пользуется всеми шагами. Только финальный `POST /users/me/merge` требует свежей сессии, сами доказательства (`proofs`) не требуют.

### 9.1. Подготовка

Создайте: `carol` уже есть (username), `dave@example.com` (email, как в разделе 4). Войдите carol свежо (`tokenCarol`), войдите dave (`tokenDave`). Из `GET /users/me` запишите `id` обоих.

### 9.2. Merge без 2FA

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 9.2.1 | `tokenCarol`: `POST /api/v1/users/me/merge/proofs/email`: `{"email":"dave@example.com","password":"неверный"}` | 403, `MERGE_INVALID_CREDENTIALS` |
| 9.2.2 | То же с несуществующим email | 403, `MERGE_INVALID_CREDENTIALS` (код одинаковый: ответ не выдаёт, существует ли аккаунт) |
| 9.2.3 | `POST /users/me/merge/proofs/username`: `{"username":"carol","password":"Passw0rd!123"}` (собственный аккаунт) | 400, `MERGE_SAME_USER` |
| 9.2.4 | `POST /users/me/merge/proofs/email`: `{"email":"dave@example.com","password":"Passw0rd!123"}` | 201: `proof_id`, `expires_at`, `requires_two_factor: false`, `challenge_id: null` |
| 9.2.5 | `POST /users/me/merge`: `{"proof_id":"выдуманный"}` | 404, `MERGE_PROOF_NOT_FOUND` |
| 9.2.6 | `POST /users/me/merge/proofs/confirm` с этим `proof_id` и кодом `123456` | 409, `MERGE_PROOF_CONFIRMATION_NOT_REQUIRED` (2FA у источника нет) |
| 9.2.7 | `POST /users/me/merge`: `{"proof_id":"<из 9.2.4>"}` | 204 |
| 9.2.8 | `tokenCarol`: `GET /identities` | Два способа: username `carol` и email `d***@example.com` |
| 9.2.9 | Повторить `POST /users/me/merge` с тем же `proof_id` | 409, `MERGE_PROOF_USED` |
| 9.2.10 | `tokenDave`: `GET /users/me` | 401, `SESSION_REVOKED` (сессии источника закрыты) |
| 9.2.11 | `POST /auth/email/login`, `dave@example.com` / `Passw0rd!123` | 200. `GET /users/me` этим токеном возвращает аккаунт carol (`id` carol): способ входа теперь принадлежит ей |
| 9.2.12 | Войти superadmin. `GET /users/{daveId}` | 200: `status: deactivated_by_merge` |
| 9.2.13 | Лог писем | `To: dave@example.com`, `Subject: Accounts merged` |

### 9.3. Ограничения

Создайте `erin1` и `erin2` (оба только username, регистрация как в разделе 3). Войдите erin1 свежо.

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 9.3.1 | `erin1`: `POST /users/me/merge/proofs/username`: `{"username":"erin2","password":"Passw0rd!123"}` | 201, `proof_id` |
| 9.3.2 | `POST /users/me/merge` с этим `proof_id` | 409, `MERGE_TYPE_CONFLICT`: у обоих есть username-способ |
| 9.3.3 | Проверить `erin2`: вход `erin2` / `Passw0rd!123` и `GET /identities` | Всё как раньше: операция откатилась целиком |
| 9.3.4 | Повторить `POST /users/me/merge` с тем же `proof_id` | Снова 409 `MERGE_TYPE_CONFLICT` (при откате доказательство не расходуется) |
| 9.3.5 | `POST /users/me/merge` без токена | 401, `INVALID_TOKEN` |
| 9.3.6 | Merge со старой сессией (см. раздел 11) | 403, `FRESH_SESSION_REQUIRED` |

### 9.4. Merge с 2FA исходного аккаунта

Создайте `gina` (username, цель) и `hank@example.com` (email, источник). Войдите hank свежо, включите 2FA так же, как у alice (метод на `hank@example.com`: раздел 8.1 и 8.2), выйдите.

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 9.4.1 | `gina` (свежий вход): `POST /users/me/merge/proofs/email`: `{"email":"hank@example.com","password":"Passw0rd!123"}` | 201: `requires_two_factor: true`, `challenge_id`. Письмо `Subject: Confirm the merge of accounts` на адрес метода hank |
| 9.4.2 | `POST /users/me/merge` с этим `proof_id` до подтверждения | 403, `MERGE_PROOF_NOT_CONFIRMED` |
| 9.4.3 | `POST /users/me/merge/proofs/confirm`: `{"proof_id":"...","code":"000000"}` | 401, `INVALID_TWO_FACTOR_CODE` |
| 9.4.4 | Confirm с верным кодом из письма | 200: `proof_id`, `expires_at` |
| 9.4.5 | `POST /users/me/merge` | 204; у gina появился email-способ |
| 9.4.6 | `GET /auth/2fa/status` токеном gina | `enabled: false`: настройки 2FA источника удалены и не переносятся |
| 9.4.7 | Вход `hank@example.com` | 200 без challenge: это уже аккаунт gina без 2FA |

### 9.5. Срок доказательства

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 9.5.1 | Создать доказательство и подождать больше 10 минут (`MERGE_PROOF_EXPIRE_MINUTES`) | `POST /users/me/merge`: 400, `MERGE_PROOF_EXPIRED` |

### 9.6. Контакты (необязательно)

Эндпоинтов для контактов нет, перенос проверяется только через базу: добавьте контакт источнику напрямую (таблица `contacts`: `user_id`, `type`, `value`), выполните Merge и убедитесь запросом `select user_id, type, value from contacts`, что `user_id` стал идентификатором цели. Если это не нужно сейчас, пропустите.

---

## 10. Роли, деактивация, purge

**Что проверяем:** права по ролям, смену роли, деактивацию самим пользователем и администратором, невозможность входа неактивного пользователя, удаление данных (purge). Перезапустите сервис перед разделом.

Создайте `ivan`, `judy`, `kate` (username, раздел 3). Запишите их `id` из ответов регистрации: `ivanId`, `judyId`, `kateId`. Войдите superadmin (свежий токен `tokenSA`) и alice (`tokenAlice`).

### 10.1. Права и роли

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 10.1.1 | `tokenAlice` (роль user): `GET /api/v1/users` | 403, `INSUFFICIENT_PERMISSIONS` |
| 10.1.2 | `tokenSA`: `GET /api/v1/users` | 200, список (`id`, `first_name`, `last_name`, `role`), все созданные пользователи |
| 10.1.3 | `tokenSA`: `GET /users/{ivanId}` | 200: добавлены `status: active`, `created_at`, `updated_at` |
| 10.1.4 | `tokenSA`: `PATCH /users/{kateId}/role`: `{"role":"admin"}` | 200, `role: admin` |
| 10.1.5 | `tokenSA`: `PATCH /users/{kateId}/role`: `{"role":"выдуманная"}` | 400, `INVALID_ROLE` |
| 10.1.6 | `tokenSA`: `PATCH` собственной роли (`id` суперадмина) | 400, `CANNOT_CHANGE_OWN_ROLE` |
| 10.1.7 | `tokenAlice`: `PATCH /users/{kateId}/role` | 403, `INSUFFICIENT_PERMISSIONS` |
| 10.1.8 | Войти kate (admin), `tokenKate`: `GET /users` | 200 (у admin есть право читать пользователей) |
| 10.1.9 | `tokenKate`: `POST /users/{judyId}/deactivate` | 403, `INSUFFICIENT_PERMISSIONS` (деактивировать других может только superadmin) |
| 10.1.10 | `tokenKate`: `DELETE /users/{ivanId}?confirm_user_id={ivanId}` | 403, `INSUFFICIENT_PERMISSIONS` (purge только у superadmin) |

### 10.2. Деактивация

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 10.2.1 | Войти ivan (`tokenIvan`). `POST /users/me/deactivate` | 204 |
| 10.2.2 | `tokenIvan`: `GET /users/me` | 401, `SESSION_REVOKED` |
| 10.2.3 | Вход `ivan` / `Passw0rd!123` | 403, `USER_INACTIVE` |
| 10.2.4 | `tokenSA`: `GET /users/{ivanId}` | `status: deactivated_by_user` |
| 10.2.5 | `tokenSA`: `POST /users/{ivanId}/deactivate` (уже неактивен) | 409, `USER_ALREADY_DEACTIVATED` |
| 10.2.6 | `tokenSA`: `POST /users/{judyId}/deactivate` | 204. `GET /users/{judyId}`: `status: deactivated_by_admin`. Вход judy: 403 `USER_INACTIVE` |
| 10.2.7 | `tokenSA`: `POST /users/{несуществующий}/deactivate` | 404, `USER_NOT_FOUND` |
| 10.2.8 | `tokenSA`: `POST /users/{superadminId}/deactivate` (единственный superadmin) | 400, `LAST_SUPERADMIN_DEACTIVATION` |
| 10.2.9 | Регистрация нового пользователя с username `ivan` | 409, `USER_ALREADY_EXISTS`: имя остаётся занятым до purge |

### 10.3. Purge

Purge удаляет пользователя и все строки о нём без возможности восстановления. Только superadmin со свежей сессией.

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 10.3.1 | `tokenSA`: `DELETE /users/{aliceId}?confirm_user_id={aliceId}` (alice активна) | 409, `USER_STILL_ACTIVE` |
| 10.3.2 | `tokenSA`: `DELETE /users/{ivanId}?confirm_user_id=другой-id` | 400, `PURGE_CONFIRMATION_MISMATCH` |
| 10.3.3 | `tokenSA`: `DELETE /users/неизвестный-id?confirm_user_id=неизвестный-id` | 404, `USER_NOT_FOUND` |
| 10.3.4 | `tokenAlice`: `DELETE /users/{ivanId}?confirm_user_id={ivanId}` | 403, `INSUFFICIENT_PERMISSIONS` |
| 10.3.5 | `tokenSA`: `DELETE /users/{ivanId}?confirm_user_id={ivanId}` | 204 |
| 10.3.6 | `tokenSA`: `GET /users/{ivanId}` | 404, `USER_NOT_FOUND` |
| 10.3.7 | `python scripts\check_db.py "select count(*) from username_identities where username='ivan'"` | `(0,)` |
| 10.3.8 | Проверить остальные таблицы по `ivanId`: `select count(*) from sessions where user_id='<ivanId>'`, то же для `two_factor_challenges`, `two_factor_methods`, `user_security_settings`, `contacts` | Везде `(0,)`; в консоли сервиса нет ошибок внешних ключей |
| 10.3.9 | Регистрация нового пользователя `ivan` | 201: имя освободилось |
| 10.3.10 | Purge пользователя с включённой 2FA (после деактивации): повторить 10.3.5 для такого пользователя | 204, строки в `two_factor_methods`, `user_security_settings`, `two_factor_recovery_codes` для него удалены |
| 10.3.11 | Purge со **старой** сессией (см. раздел 11) | 403, `FRESH_SESSION_REQUIRED` |

---

## 11. Свежая сессия и лимиты частоты

### 11.1. Свежая сессия

**Что проверяем:** чувствительные действия требуют недавнего входа. Возраст считается от создания сессии; `refresh` его не обновляет.

Остановите сервис, в `.env` добавьте `FRESH_SESSION_MINUTES=1`, запустите. Войдите alice (если включена 2FA, отключите: раздел 8.5) и подождите 70 секунд. Затем выполните каждое действие тем же токеном:

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
| 11.1.10 | Суперадмин со старой сессией: `DELETE /users/{id}?confirm_user_id={id}` | 403, `FRESH_SESSION_REQUIRED` |
| 11.1.11 | `GET /users/me`, `GET /identities`, `GET /auth/2fa/status`, `GET /sessions` | 200: чтение свежей сессии не требует |
| 11.1.12 | `POST /auth/2fa/enable`, `/auth/2fa/recovery-codes`, `/users/me/merge/proofs/...` | Не 403 `FRESH_SESSION_REQUIRED` (эти действия свежей сессии не требуют) |
| 11.1.13 | `POST /auth/refresh` и повтор 11.1.1 новым access-токеном | По-прежнему 403: refresh сессию не «освежает» |
| 11.1.14 | Новый вход и сразу действие из 11.1.2 | Запрос проходит дальше (не 403 `FRESH_SESSION_REQUIRED`) |

После проверки удалите `FRESH_SESSION_MINUTES=1` из `.env` и перезапустите сервис.

### 11.2. Лимиты частоты

**Что проверяем:** превышение лимита возвращает 429 `RATE_LIMIT_EXCEEDED`. Счётчики в памяти, перезапуск их сбрасывает. **Перезапускайте сервис перед каждым шагом таблицы**, иначе лимиты накладываются.

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 11.2.1 | Регистрация username `limit1` четыре раза подряд | 201, затем 409, 409, на четвёртом 429 (лимит 3 в час на одно имя) |
| 11.2.2 | `POST /auth/login` с неверным паролем 11 раз для одного username | Десять раз 401 `INVALID_CREDENTIALS`, на 11-й 429 (10 за 15 минут на имя) |
| 11.2.3 | `POST /auth/email/register` четыре раза с одним адресом | На четвёртом 429 (3 в час на адрес) |
| 11.2.4 | `POST /auth/login` 21 раз подряд (любые данные) | С 21-го запроса 429 (20 за 10 минут на IP; по имени лимит 10 может сработать раньше, если имя одно, поэтому меняйте имя в запросах) |
| 11.2.5 | `POST /identities/email` свежей сессией четыре раза с одним адресом | На четвёртом 429 (3 в час на адрес) |
| 11.2.6 | Сообщение при 429 | `message`: `Too many requests, try again in N seconds` |
| 11.2.7 | Перезапуск сервиса и повтор запроса из 11.2.1 | Лимит сброшен (запрос снова проходит) |

---

## 12. Фоновая очистка

**Что проверяем:** фоновая задача удаляет использованные и просроченные временные записи: 2FA-challenge (`used` или `expires_at` в прошлом), регистрации по email (`expires_at` в прошлом), OAuth-состояния Google. Первый прогон выполняется через один интервал после старта.

Остановите сервис, в `.env` задайте `CLEANUP_INTERVAL_SECONDS=15`. Для проверки просроченных записей запускайте сервис так:

```powershell
$env:CHALLENGE_EXPIRE_MINUTES="1"
```
```powershell
python -m app.main
```

(Параметры 2FA читаются из окружения, а не из `.env`; в этой же сессии PowerShell сервис будет считать код действующим 1 минуту.)

| Шаг | Действие | Ожидаемый результат |
|---|---|---|
| 12.1 | Выполнить вход пользователя с 2FA (8.2.5 и 8.2.10) и сразу `python scripts\check_db.py "select purpose, used from two_factor_challenges"` | Есть строка `('login', 1)` |
| 12.2 | Подождать 20 секунд, повторить команду | Строк с `used = 1` нет |
| 12.3 | Начать `email/register` для `zoe@example.com`, не подтверждать. `python scripts\check_db.py "select email from email_registrations"` | Строка есть |
| 12.4 | Подождать больше минуты и ещё 15 секунд | Строки нет: просроченная регистрация удалена |
| 12.5 | Остановить сервис (Ctrl+C) | Остановка без ошибок и без `Periodic cleanup failed` |
| 12.6 | Вернуть `CLEANUP_INTERVAL_SECONDS=3600` (или удалить строку) и закрыть окно PowerShell, чтобы сбросить `CHALLENGE_EXPIRE_MINUTES` | Перезапустить сервис в новом окне |

Если в консоли появляется `Periodic cleanup failed` с трассировкой, это ошибка: пришлите её.

---

## 13. Если что-то не работает

Для каждого проваленного шага пришлите:

1. Номер шага из этого документа.
2. Метод, адрес и тело запроса (пароли можно не присылать).
3. Статус и тело ответа (особенно поле `code`).
4. Трассировку из консоли сервиса: весь блок от `Traceback` до последней строки.
5. Для шагов с письмами: последние строки лога писем.

Типичные причины:

| Симптом | Что проверить |
|---|---|
| `'Get-Content' is not recognized...` | Вы в cmd. Введите `powershell` |
| Сервис не стартует, `ValidationError` | В `.env` нет обязательной переменной (п. 1.2) |
| Ошибка про отсутствующую колонку или таблицу | Остался старый `app.db`: удалите его (миграций пока нет) |
| Ошибка внешнего ключа при удалении | Пришлите трассировку: это ошибка порядка удаления |
| 401 сразу после входа | Токен истёк (15 минут) или вставлен вместе со словом `Bearer` |
| 429 там, где не ждали | Сработал лимит: перезапустите сервис |
| 403 `FRESH_SESSION_REQUIRED` | Вход старше 15 минут: войдите заново |
| Нет письма в логе | `EMAIL_SERVICE=dummy`, папка `logs\email_dummy_logs`, дата в имени файла |
| В Swagger не видно запроса | Группы свёрнуты: раскройте «Username Authentication», «Auth» и т. д. Либо проверьте список маршрутов (п. 2.5) |

---

## 14. Итоговая таблица

Отметьте результат: ✅ всё прошло, ⚠️ есть отклонения, ❌ не работает.

| Раздел | Что проверено | Результат |
|---|---|---|
| 2 | Запуск, база, суперадмин, список маршрутов | |
| 3 | Регистрация и вход по username | |
| 4 | Регистрация и вход по email, лимит попыток | |
| 5 | Токены, профиль, сессии, logout | |
| 6 | Link | |
| 7 | Unlink | |
| 8 | 2FA и recovery-коды | |
| 9 | Merge | |
| 10 | Роли, деактивация, purge | |
| 11 | Свежая сессия и лимиты | |
| 12 | Фоновая очистка | |
