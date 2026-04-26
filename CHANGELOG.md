## 0.12.0 (2026-04-26)

### Feat

- make email field uneditable from users api

## 0.11.0 (2026-04-26)

### Feat

- add is_active field to UserDetailsSerializer

## 0.10.0 (2026-04-25)

### Feat

- add is_active filter and filter definition
- add is_active column to default column preferences
- add management command to load default filter variants
- add custom PageNumberPagination
- add API endpoint for filter variants
- add API endpoint for user filter preferences
- add API endpoint for filter definitions
- add filters for users API
- add API endpoint for user column preferences
- add API endpoint for default column preferences
- create models for ui preferences

## 0.9.0 (2026-04-20)

### Feat

- add group permissions API endpoint
- add group users API endpoint
- add user groups API endpoint
- update User serializers to have uuid field instead of id
- add groups API endpoint
- add permissions API endpoint

## 0.8.0 (2026-04-17)

### Feat

- update preferences API to also return labels
- add user preferences API endpoint
- add fiori theme choices API endpoint
- add time format choices API endpoint
- add timezone choices API endpoint
- add decimal format choices API endpoint
- add date format choices API endpoint
- add UserPreferences model

### Fix

- schema generation for UserPreferences

## 0.7.0 (2026-04-14)

### Feat

- add users API
- configure default pagination
- configure DjangoModelPermissions as default permission class

### Fix

- User model

## 0.6.0 (2026-04-12)

### Feat

- configure drf-spectacular and client generation

### Fix

- user activation link to match updated API url

## 0.5.0 (2026-04-12)

### Feat

- add /api/me endpoint

## 0.4.0 (2026-04-11)

### Feat

- configure django-cors-headers

## 0.3.0 (2026-04-11)

### Feat

- add token verify API endpoint
- add token blacklist API endpoint
- add token refresh API endpoint
- add token API endpoint
- add user activate endpoint
- send registration email in register API
- change user model's primary key to uuid field
- add register API endpoint

## 0.2.0 (2026-04-11)

### Feat

- add users app with custom User model
- create django project
