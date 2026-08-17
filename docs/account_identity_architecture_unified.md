# Архитектура аккаунтов, пользователей, идентичностей и аутентификации

## 1. Основная модель

В системе существует центральная сущность **User**.

`User` представляет сам аккаунт пользователя и является владельцем его данных.

Способы входа и идентификации пользователя представлены отдельными сущностями **Identity**.

Концептуально:

```text
User
├── EmailIdentity
├── UsernameIdentity
├── GoogleIdentity
├── PhoneIdentity
├── AppleIdentity
└── ...
```

Разные типы Identity не объединяются в одну универсальную модель только ради унификации. Каждый тип Identity может иметь собственные свойства и правила.

---

## 2. User может иметь несколько идентичностей

Один User может одновременно иметь несколько identities разных типов.

Например:

```text
User
├── EmailIdentity
├── UsernameIdentity
└── GoogleIdentity
```

Количество типов Identity в будущем может расширяться: Apple, Phone, Passkey, GitHub, Telegram и т. д.

---

## 3. У одного User может быть только одна Identity конкретного типа

Это принципиальное ограничение.

Для каждого типа Identity у User может существовать **не более одной активной Identity этого типа**.

Допустимо:

```text
User A
├── EmailIdentity
├── UsernameIdentity
└── GoogleIdentity
```

Недопустимо:

```text
User A
├── GoogleIdentity #1
└── GoogleIdentity #2
```

Также недопустимо:

```text
User A
├── UsernameIdentity #1
└── UsernameIdentity #2
```

Таким образом:

> **User может иметь много identities, но максимум одну identity каждого типа.**

---

## 4. Identity принадлежит только одному User

Каждая Identity в каждый момент времени принадлежит ровно одному User.

Одна и та же Identity не может одновременно быть связана с двумя аккаунтами.

При linking Identity переносится от одного User к другому.

---

## 5. Идентификатор Identity глобально уникален

Каждый provider должен иметь свой уникальный идентификатор.

Примеры:

```text
EmailIdentity
    email = alex@example.com
```

```text
UsernameIdentity
    username = alex
```

```text
GoogleIdentity
    google_user_id = 123456
```

Один и тот же идентификатор одного типа не может принадлежать двум разным identities.

Это гарантирует однозначное определение аккаунта по конкретному authentication identity.

---

## 6. Identity и контактные данные — не одно и то же

Это одно из ключевых правил архитектуры.

У User могут существовать **контактные данные**, которые не являются способами авторизации.

Например:

```text
User
├── Email contacts
│   ├── alex@example.com
│   ├── alex.work@example.com
│   └── alex.old@example.com
│
├── Phone contacts
│   ├── +31...
│   └── +380...
│
└── Other contacts
    ├── Telegram
    └── WhatsApp
```

Наличие контактного значения **не означает**, что по нему разрешён вход в аккаунт.

Контакт и Identity — разные понятия.

---

## 7. Для каждого типа контакта может быть несколько значений

Пользователь может сохранить несколько email, телефонов и других контактных данных одного типа.

Например:

```text
Email contacts
├── personal@example.com  ← primary
├── work@example.com
└── old@example.com
```

Среди значений одного типа может быть один ключевой контакт, используемый как основной для соответствующей функции.

---

## 8. Только ключевая Identity определяет способ входа

Наличие email в данных пользователя не означает наличие EmailIdentity.

Например:

```text
User
└── UsernameIdentity
      └── email = alex@example.com
```

Это **не означает**:

```text
EmailIdentity
    email = alex@example.com
```

Следовательно, пользователь не может автоматически войти через email только потому, что этот email где-то сохранён в UsernameIdentity.

---

## 9. Identity определяет право на конкретный способ авторизации

Если существует:

```text
EmailIdentity
    email = alex@example.com
```

то именно она означает, что `alex@example.com` является идентификатором, через который разрешена email-аутентификация данного аккаунта.

Если существует только:

```text
UsernameIdentity
    username = alex
    email = alex@example.com
```

то email является лишь связанными с username данными.

Он **не становится EmailIdentity автоматически**.

---

## 10. Контакт не превращается в Identity автоматически

Это особенно важно для linking.

Допустим:

```text
User A
└── UsernameIdentity
      username = alex
      email = alex@example.com
```

Позже к User A привязывается:

```text
EmailIdentity
    email = alex@example.com
```

После этого email внутри UsernameIdentity не становится вторым способом email-аутентификации.

Существует одна EmailIdentity, а значение email внутри UsernameIdentity остаётся дополнительными данными.

---

## 11. Если Identity одного типа уже существует, другое значение этого типа не становится ключом автоматически

Например:

```text
User A
└── EmailIdentity
      alex@example.com
```

и одновременно:

```text
UsernameIdentity
    username = alex
    email = alex.work@example.com
```

`alex.work@example.com` не становится EmailIdentity автоматически.

Для превращения его в ключ email-аутентификации требуется **явное действие пользователя и соответствующее подтверждение**.

Это принципиально важно для безопасности.

---

## 12. Linking не должен смешивать контактные данные и identities

Операция linking означает:

> существующая Identity связывается с существующим User.

Она не означает:

> все данные, найденные внутри этой Identity, автоматически становятся способами авторизации.

Например Google может предоставить:

```text
GoogleIdentity
├── google_id
├── email
└── name
```

При linking Google Identity к User:

```text
GoogleIdentity → User
```

не следует автоматически создавать EmailIdentity только потому, что Google сообщил email.

Email должен стать самостоятельной EmailIdentity только в результате соответствующего явно определённого процесса.

---

## 13. Unlink должен учитывать Identity и контакты отдельно

При удалении Identity:

```text
User
├── EmailIdentity
├── UsernameIdentity
└── GoogleIdentity
```

и unlink Google:

```text
User
├── EmailIdentity
└── UsernameIdentity
```

данные, которые были получены от Google или сохранены как контактные, не должны автоматически становиться новой Identity.

Unlink удаляет или переносит **право идентификации**, а не автоматически меняет остальные способы доступа.

---

## 14. User без Identity существовать не должен

Это фундаментальный инвариант.

User должен иметь хотя бы одну Identity.

Недопустимо:

```text
User
└── no identities
```

Следовательно, любая операция, которая удаляет или переносит последнюю Identity User, должна одновременно решить судьбу User:

- создать новый User для отделяемой Identity;
- перенести Identity на другого User;
- удалить User;
- либо выполнить другую явно определённую бизнес-операцию.

Но система не должна оставлять обычный User без Identity.

---

## 15. Linking двух пользователей

Если:

```text
User A
├── UsernameIdentity
└── EmailIdentity

User B
└── GoogleIdentity
```

и GoogleIdentity связывается с User A:

```text
User A
├── UsernameIdentity
├── EmailIdentity
└── GoogleIdentity
```

то User B больше не должен существовать как пустой аккаунт.

Если у него не осталось identities, он должен быть удалён либо обработан другим предусмотренным сценарием.

---

## 16. Merge нескольких пользователей

Архитектура должна поддерживать объединение:

```text
User A
├── EmailIdentity
└── UsernameIdentity

User B
└── GoogleIdentity

User C
└── PhoneIdentity
```

в:

```text
User A
├── EmailIdentity
├── UsernameIdentity
├── GoogleIdentity
└── PhoneIdentity
```

при условии, что не нарушаются ограничения:

- максимум одна Identity каждого типа у User;
- глобальная уникальность идентификаторов;
- отсутствие конфликтующих identities.

Исходные Users после успешного объединения не должны оставаться пустыми.

---

## 17. Split / unlink также должен быть полноценной операцией

Обратная операция должна быть возможна.

Например:

```text
User A
├── EmailIdentity
├── UsernameIdentity
└── GoogleIdentity
```

может быть разделён так, чтобы:

```text
User A
├── EmailIdentity
└── UsernameIdentity

User B
└── GoogleIdentity
```

При этом новая структура должна быть создана осознанно, а не как побочный эффект удаления связи.

---

# 18. Аутентификация как отдельная часть архитектуры

**Authentication** отвечает за проверку того, что субъект обладает соответствующей Identity, и за управление сессиями после успешной аутентификации.

При этом Authentication не должна подменять модель User/Identity.

Концептуально:

```text
User
 │
 └── Identity
       │
       ▼
 Authentication
       │
       ▼
 Session
```

Identity определяет, **каким способом пользователь может быть идентифицирован**.

Authentication определяет, **как происходит проверка этого способа идентификации**.

Session представляет **результат успешной аутентификации и состояние доступа пользователя**.

---

## 19. Authentication Service

Аутентификация является отдельной областью бизнес-логики и не должна быть непосредственно связана с конкретной инфраструктурой.

Auth Service отвечает за authentication-related use cases, например:

- регистрацию;
- аутентификацию;
- создание и управление сессиями;
- завершение сессии;
- восстановление доступа.

При этом конкретные способы аутентификации реализуются через соответствующие Identity и механизмы проверки.

Например:

```text
EmailIdentity
      │
      ▼
Email Authentication
      │
      ▼
Session
```

или:

```text
GoogleIdentity
      │
      ▼
Google OAuth / OIDC Authentication
      │
      ▼
Session
```

или:

```text
PhoneIdentity
      │
      ▼
Phone OTP Authentication
      │
      ▼
Session
```

Таким образом, добавление нового способа входа не должно требовать изменения самой сущности User.

---

## 20. Аутентификация и пароль

Пароль является механизмом аутентификации, а не идентичностью пользователя.

Например:

```text
User
└── EmailIdentity
      └── email = alex@example.com
```

может использовать пароль для подтверждения владения этой Identity.

Концептуально:

```text
EmailIdentity
      │
      ├── identifier
      │     └── email
      │
      └── authentication credentials
            └── password
```

Поэтому наличие пароля не создаёт отдельного User и не заменяет Identity.

Пароль должен храниться в защищённом виде через механизм password hashing.

---

## 21. Сессия

После успешной аутентификации система может создать **Session**, связанную с User.

Концептуально:

```text
User
 ├── Identity
 ├── Identity
 └── Identity
       │
       ▼
 Authentication
       │
       ▼
 Session
```

Один User может иметь несколько одновременно существующих сессий.

Сессия не является Identity.

Identity отвечает на вопрос:

> Каким способом этот User может быть идентифицирован?

Session отвечает на вопрос:

> Есть ли сейчас активный результат успешной аутентификации этого User?

---

## 22. Access Token и Refresh Token

Для token-based authentication могут использоваться:

```text
Session
├── Access Token
└── Refresh Token
```

Access Token представляет краткоживущий результат авторизации текущего доступа.

Refresh Token используется для продолжения сессии и получения нового Access Token.

Token infrastructure не должна быть частью модели User или Identity.

То есть:

```text
User
├── Identity
├── Identity
└── Identity

Session
├── Access Token
└── Refresh Token
```

а не:

```text
User
└── access_token
└── refresh_token
```

---

## 23. Password Reset

Восстановление пароля является операцией Authentication и не должно создавать новую Identity.

Концептуально:

```text
EmailIdentity
      │
      ▼
Password Reset
      │
      ▼
изменение authentication credential
```

Если пользователь изменяет пароль, его Identity не меняется.

Если пользователь получает письмо для восстановления пароля на контактный email, это само по себе также не создаёт EmailIdentity.

Право использовать конкретный email для authentication определяется наличием соответствующей EmailIdentity.

---

# 24. Архитектурные слои

Auth Service должен следовать принципам **Clean Architecture / Hexagonal Architecture**.

Основное правило:

> зависимости направлены внутрь, а бизнес-логика не зависит от инфраструктуры.

Концептуальная схема:

```text
External World
      ↓
Router / Controller
      ↓
Service / Use Cases
      ↓
Interfaces
      ↑
Implementations
```

Или:

```text
Router → Service → Interfaces ← Implementations
```

---

# 25. Router / Controller

Router является внешним входом в систему.

Он отвечает за:

- получение HTTP-запросов;
- валидацию входных данных;
- преобразование DTO;
- вызов соответствующего Service / Use Case;
- формирование HTTP-ответа.

Router не должен содержать бизнес-логику.

Например:

```text
POST /auth/login
        ↓
     Router
        ↓
 Authentication Service
```

Решение о том, существует ли Identity, допустима ли операция или можно ли создать Session, относится к бизнес-логике, а не к Router.

---

# 26. Service / Use Cases

Service содержит бизнес-логику и use cases.

Service работает с доменной моделью:

```text
User
Identity
Contact
Session
```

и не должен напрямую зависеть от:

- конкретной базы данных;
- HTTP framework;
- JWT library;
- password hashing library;
- SMTP provider;
- конкретного OAuth provider;
- других инфраструктурных реализаций.

Service использует Interfaces.

---

# 27. Interfaces

Interfaces определяют контракты между бизнес-логикой и внешними зависимостями.

Примеры:

```text
UserRepository
IdentityRepository
SessionRepository
PasswordResetRepository

TokenProvider
PasswordHasher
EmailSender
```

Также отдельные authentication providers могут быть представлены через соответствующие интерфейсы.

Например:

```text
AuthenticationProvider
├── EmailAuthenticationProvider
├── GoogleAuthenticationProvider
└── PhoneAuthenticationProvider
```

Интерфейс определяет поведение, но не его конкретную реализацию.

---

# 28. Implementations

Implementations содержат конкретные реализации Interfaces.

Например:

```text
UserRepository
├── PostgresUserRepository
└── MongoUserRepository
```

```text
SessionRepository
└── RedisSessionRepository
```

```text
TokenProvider
└── JWTTokenProvider
```

```text
PasswordHasher
└── ArgonPasswordHasher
```

```text
EmailSender
├── SMTPEmailSender
└── SendgridEmailSender
```

Для внешней authentication provider:

```text
GoogleAuthenticationProvider
└── Google OAuth / OIDC implementation
```

Implementations могут зависеть от:

- базы данных;
- Redis;
- SMTP;
- внешних API;
- OAuth/OIDC libraries;
- JWT libraries;
- других third-party libraries.

Бизнес-логика от этих деталей зависеть не должна.

---

# 29. Dependency Rules

### Правило 1

Зависимости направлены внутрь.

Правильно:

```text
Router → Service → Interfaces
Implementations → Interfaces
```

Неправильно:

```text
Service → PostgreSQL
Service → Redis
Service → SMTP
Service → JWT library
```

---

### Правило 2

Business logic должна оставаться infrastructure-agnostic.

Service не должен знать:

- какая база данных используется;
- какой email provider используется;
- какая библиотека используется для JWT;
- какой конкретный password hashing implementation используется;
- какой внешний OAuth provider реализует конкретную Implementation.

---

### Правило 3

Infrastructure должна быть заменяемой.

Например:

```text
UserRepository
├── PostgresUserRepository
└── MongoUserRepository
```

или:

```text
EmailSender
├── SMTPEmailSender
└── SendgridEmailSender
```

Замена Implementation не должна требовать изменения основной бизнес-логики.

---

# 30. Связь архитектуры Authentication с User и Identity

Authentication не должна становиться альтернативной моделью аккаунта.

Правильная структура:

```text
                         USER
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
        EmailIdentity  UsernameIdentity  GoogleIdentity
             │             │             │
             │             │             │
             ▼             ▼             ▼
        authentication  authentication  authentication
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                       Session
```

При этом рядом с User могут существовать:

```text
User
├── Identities
│   ├── EmailIdentity
│   ├── UsernameIdentity
│   └── GoogleIdentity
│
├── Email contacts
│   ├── email #1
│   ├── email #2
│   └── ...
│
├── Phone contacts
│   ├── phone #1
│   ├── phone #2
│   └── ...
│
└── Other contacts
```

Identity определяет возможность идентификации и authentication.

Contact — нет.

Session представляет результат успешной authentication.

---

# 31. Главный принцип модели

Вся архитектура строится вокруг разделения четырёх понятий:

```text
User
```

— аккаунт и владелец данных.

```text
Identity
```

— подтверждённый способ идентификации/аутентификации аккаунта.

```text
Contact
```

— дополнительная контактная информация пользователя, которая сама по себе не даёт права входа.

```text
Session
```

— состояние активного доступа, созданное в результате успешной аутентификации.

Их нельзя считать взаимозаменяемыми.

---

# 32. Итоговая модель

```text
                         USER
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
        Identities      Contacts       Data
             │
      ┌──────┼──────┐
      │      │      │
      ▼      ▼      ▼
    Email  Username Google
      │      │      │
      └──────┼──────┘
             │
             ▼
       Authentication
             │
             ▼
          Session
          /     \
         ▼       ▼
 Access Token  Refresh Token
```

При этом:

```text
User
├── Identities
│   ├── EmailIdentity
│   ├── UsernameIdentity
│   └── GoogleIdentity
│
├── Contacts
│   ├── Email contacts
│   ├── Phone contacts
│   └── Other contacts
│
└── Sessions
    ├── Session #1
    ├── Session #2
    └── ...
```

Для каждого типа Identity у User существует максимум одна активная Identity, но сам User может иметь много identities разных типов.

Контактных данных одного типа может быть много, но только явно выбранный и подтверждённый механизм может сделать конкретное значение ключом соответствующей Identity.

Authentication проверяет Identity и создаёт Session.

Session не является Identity и не заменяет её.

---

# 33. Архитектурная точка назначения

В дальнейшем все решения по моделям должны соответствовать следующей формуле:

> **Один User может иметь много способов идентификации, но максимум один способ каждого типа. Identity является ключом доступа, Contact является только данными. Один User не может существовать без Identity. Linking, unlinking, merging и splitting меняют связи между User и Identity, но не должны автоматически превращать контактные данные в способы авторизации. Любое превращение контактных данных в ключ доступа требует явного подтверждения пользователя. Authentication проверяет Identity и создаёт Session. Authentication и Session не должны изменять фундаментальную модель User, Identity и Contact. Бизнес-логика не зависит от конкретной инфраструктуры, а внешние системы подключаются через Interfaces и их Implementations.**
