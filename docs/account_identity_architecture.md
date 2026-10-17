
## 21. Сессия

После успешной аутентификации система может создать **Session**, связанную с **User** и с той **Identity**, через которую была выполнена аутентификация.

Концептуально:

```text
Identity
      │
      ▼
 Authentication
      │
      ▼
 Session
   ├── user_id
   └── identity_id
```

Один User может иметь несколько одновременно существующих сессий, в том числе сессии, созданные через разные Identity.

Например:

```text
User
├── EmailIdentity
│     └── Session #1
│
├── UsernameIdentity
│     └── Session #2
│
└── GoogleIdentity
      └── Session #3
```

Сессия не является Identity.

Identity отвечает на вопрос:

> Каким способом этот User может быть идентифицирован?

Authentication отвечает на вопрос:

> Как система проверяет владение этой Identity?

Session отвечает на вопрос:

> Есть ли сейчас активный результат успешной аутентификации, и через какую Identity он был получен?

Хранение `identity_id` в Session позволяет независимо управлять сессиями разных Identity.

Например:

```text
Session #1 → EmailIdentity
Session #2 → GoogleIdentity
```

При отзыве GoogleIdentity Session #2 может быть отозвана, не затрагивая Session #1.

Полный logout User, наоборот, может завершить все его sessions.

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

При этом в User рядом с Identity могут существовать:

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
User может иметь много identities разных типов.

Контактных данных одного типа может быть много, но только явно выбранный и подтверждённый механизм может сделать конкретное значение ключом соответствующей Identity.

Authentication проверяет Identity и создаёт Session.

---

# 33. Архитектурная точка назначения

В дальнейшем все решения по моделям должны соответствовать следующей формуле:

> **Один User может иметь много способов идентификации, но максимум один способ каждого типа. Identity является ключом доступа, Contact является только данными. Один User не может существовать без Identity. Linking, unlinking, merging и splitting меняют связи между User и Identity, но не должны автоматически превращать контактные данные в способы авторизации. Любое превращение контактных данных в ключ доступа требует явного подтверждения пользователя. Authentication проверяет Identity и создаёт Session. Authentication и Session не должны изменять фундаментальную модель User, Identity и Contact. Бизнес-логика не зависит от конкретной инфраструктуры, а внешние системы подключаются через Interfaces и их Implementations.**
