# Архитектура аккаунтов, пользователей и идентичностей

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

## 4. Identity принадлежит только одному User

Каждая Identity в каждый момент времени принадлежит ровно одному User.

Одна и та же Identity не может одновременно быть связана с двумя аккаунтами.

При linking Identity переносится от одного User к другому.

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

## 18. Главный принцип модели

Вся архитектура строится вокруг разделения трёх понятий:

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

Их нельзя считать взаимозаменяемыми.

## 19. Итоговая модель

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

**Identity определяет доступ. Contact — нет.**

Для каждого типа Identity у User существует максимум одна активная Identity, но сам User может иметь много identities разных типов.

Контактных данных одного типа может быть много, но только явно выбранный и подтверждённый механизм может сделать конкретное значение ключом соответствующей Identity.

## Архитектурная точка назначения

В дальнейшем все решения по моделям должны соответствовать следующей формуле:

> **Один User может иметь много способов идентификации, но максимум один способ каждого типа. Identity является ключом доступа, Contact является только данными. Один User не может существовать без Identity. Linking, unlinking, merging и splitting меняют связи между User и Identity, но не должны автоматически превращать контактные данные в способы авторизации. Любое превращение контактных данных в ключ доступа требует явного подтверждения пользователя.**
