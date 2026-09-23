# Быстрый Git-гайд: как обновлять материалы курса

Этот файл рассчитан на обычный workflow: локальная папка репозитория уже существует, вы меняете/добавляете материалы и отправляете их на GitHub.

## 1. Перейти в корень репозитория

```powershell
cd "C:\path\to\DFT-QE-course"
```

Проверка:

```powershell
git status
```

## 2. Перед своей работой подтянуть изменения с GitHub

```powershell
git pull --rebase
```

`--rebase` сначала подтягивает удалённые commits, затем переигрывает ваши локальные commits поверх них. Это удобно для линейной истории.

Если у вас есть незакоммиченные изменения и Git не разрешает rebase, сначала посмотрите `git status`; важные файлы сохраните/закоммитьте или временно используйте `git stash`.

## 3. Скопировать/изменить нужные файлы

Например, добавить всю новую практику как:

```text
DFT-QE-course/practice_02/
```

## 4. Добавить изменения в staging area

Только practice_02:

```powershell
git add practice_02
```

Или конкретный файл:

```powershell
git add practice_02/docs/Практика_2_recovery_guide.docx
```

Проверить, что именно попадёт в commit:

```powershell
git status
```

## 5. Создать commit

```powershell
git commit -m "Add practice 2 materials"
```

Для небольшого исправления:

```powershell
git commit -m "Update practice 2 guide"
```

## 6. Отправить на GitHub

```powershell
git push
```

## Если push отклонён: `fetch first`

Это означает, что на GitHub появились commits, которых ещё нет локально.

```powershell
git pull --rebase
git push
```

Если rebase остановился на конфликте:

```powershell
git status
```

Исправьте конфликтные файлы, затем:

```powershell
git add <исправленный-файл>
git rebase --continue
```

Если хотите отменить rebase и вернуться к состоянию до него:

```powershell
git rebase --abort
```

## Как студентам получить ваши изменения

Если репозиторий уже клонирован:

```bash
cd DFT-QE-course
git pull
```

Повторный `git clone` не нужен.

## Полезные команды

```powershell
git status                 # что изменено / staged / untracked
git log --oneline -5       # последние commits
git diff                   # незастейдженные текстовые изменения
git diff --staged          # что войдёт в следующий commit
git remote -v              # куда настроен push/pull
git pull --rebase          # подтянуть remote и переиграть локальные commits сверху
git push                   # отправить локальные commits
```

## Практический шаблон на будущее

```powershell
cd "C:\path\to\DFT-QE-course"
git pull --rebase
git status
# ...копируете/редактируете файлы...
git add <папка-или-файлы>
git status
git commit -m "Короткое описание изменения"
git push
```

Не используйте `git add .` автоматически, если в репозитории могут лежать большие outputs, временные расчётные файлы, API keys или приватные данные. Сначала всегда полезно посмотреть `git status`.
