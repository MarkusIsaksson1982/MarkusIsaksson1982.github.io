### Table: `questions`

This table stores the individual questions for the quizzes.

| Column          | Type      | Constraints                     | Description                                            |
| --------------- | --------- | ------------------------------- | ------------------------------------------------------ |
| `id`            | `uuid`    | `PRIMARY KEY`, `DEFAULT gen_random_uuid()` | The unique identifier for the question.                |
| `created_at`    | `timestamptz` | `DEFAULT now()`                 | Timestamp of when the record was created.              |
| `text`          | `text`    | `NOT NULL`                      | The question text itself (e.g., "What is phishing?").   |
| `options`       | `jsonb`   | `NOT NULL`                      | An array of possible answers. Ex: `["A", "B", "C", "D"]` |
| `correct_answer`| `text`    | `NOT NULL`                      | The correct value from the `options` array.            |
| `category`      | `text`    | `NULLABLE`                      | A category to group questions (e.g., "Cyber Safety").  |

---
#### Example SQL `CREATE TABLE` statement:
```sql
CREATE TABLE public.questions (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  text text NOT NULL,
  options jsonb NOT NULL,
  correct_answer text NOT NULL,
  category text,
  CONSTRAINT questions_pkey PRIMARY KEY (id)
);
